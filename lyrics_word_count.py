import asyncio
import json
import pandas as pd
from thefuzz import fuzz
from urllib.parse import quote
from bs4 import BeautifulSoup
from tor_utils_async import get_via_tor, init_tor_sessions, close_tor_sessions

# The base url of the intellectual mirror (make sure it ends with "/")
base_url = "int.dc09.xyz/"
similarity_threshold = 80
unique_words_threshold = 15


async def fetch_page(url: str) -> BeautifulSoup:
    print(f"Fetching {url}")
    response = await get_via_tor(url)
    return BeautifulSoup(response, "lxml")


async def get_lyrics_from_az_url(url):
    response = await fetch_page(url)
    print(response.get_text())


async def get_lyrics_from_url(url: str, key: str):
    soup = await fetch_page(url)

    lyrics = soup.find_all("p", class_="song-lyric")
    if not lyrics:
        print(f"No lyrics found for {key} ({url}), skipping.")
        return None
    print(f"Found {len(lyrics)} lines")

    result = "\n".join(lyric.get_text() for lyric in lyrics)

    return (key, result)

async def get_lyrics_from_lyrics_dict(lyrics_dict: dict[str, dict[str, str]]):
    results = await asyncio.gather(*(get_lyrics_from_url(value["url"], key) for key, value in lyrics_dict.items()))
    return [item for item in results if item]

async def search_for_song(artist: str, title: str, key: str):
    query = f"{artist} - {title}"
    url = f"{base_url}search?q={quote(query)}"
    soup = await fetch_page(url)
    
    results = soup.find_all("a", class_="song")
    print(f"Found {len(results)} for {query}")
    for result in results:
        found_title_el = result.find("h2", class_="song-title")
        found_artist_el = result.find("h3", class_="song-artist")
        if not (found_title_el and found_artist_el):
            continue
        found_title = found_title_el.get_text(strip=True)
        found_artist = found_artist_el.get_text(strip=True)

        similarity = fuzz.ratio(found_title, title)
        if similarity >= similarity_threshold:
            print(f"{found_artist} - {found_title} is {similarity} similar to {artist} - {title}")
            song_url = f"{base_url}{result['href'][1:]}"
            return key, song_url
    return None


def load_csv(filename) -> pd.DataFrame:
   return pd.read_csv(filename)
        
def load_song_info(filename) -> pd.DataFrame:
    df = load_csv(filename)
    df = df[["Track Name", "Artist Name(s)"]]
    
    def split_artists(value):
        if pd.isna(value):
            return []
        return [name.strip() for name in str(value).split(";") if name.strip()]

    df["Artist Name(s)"] = df["Artist Name(s)"].apply(split_artists)
    return df

async def search_songs(df: pd.DataFrame):
    tasks = []
    for _, row in df.iterrows():
        if not row["Artist Name(s)"]:
            continue
        artist = row["Artist Name(s)"][0]
        title = row["Track Name"]
        key = f"{artist} - {title}"
        tasks.append(search_for_song(artist, title, key))

    urls = await asyncio.gather(*tasks)
    return [item for item in urls if item]


async def scrape_lyrics_from_df(df):
    lyrics_dict = {}
    urls = await search_songs(df)
    for key, url in urls:
        lyrics_dict[key] = {"url": url}



    lyrics = await get_lyrics_from_lyrics_dict(lyrics_dict)
    for key, lyric_text in lyrics:
        lyrics_dict[key]["lyrics"] = lyric_text

    return lyrics_dict


async def find_unique_words(phrase):
    unique_words = set()
    words_list = phrase.split()
    for word in words_list:
        word = word.strip().strip("\"'`“”‘’")
        if not word:
            continue
        word = word.lower()
        
        unique_words.add(word)
    
    return unique_words


async def fill_in_unique_words(lyrics_dict):
    for key, value in lyrics_dict.items():
        unique_words = await find_unique_words(value["lyrics"])
        lyrics_dict[key]["unique_words_count"] = len(unique_words)
        lyrics_dict[key]["unique_words"] = list(unique_words)


def filter_lyrics_by_unique_words(lyrics_dict):
    return {
        key: value
        for key, value in lyrics_dict.items()
        if value.get("unique_words_count", 0) <= unique_words_threshold
    }



async def main():
    print("Hello Chat!!!")
    await init_tor_sessions()
    
    df = load_song_info("songs.csv")

    lyrics_dict = await scrape_lyrics_from_df(df)
    await fill_in_unique_words(lyrics_dict)
    with open("all_lyrics.json", "w") as f:
        json.dump(lyrics_dict, f, indent=4)

    unique_words_dict = filter_lyrics_by_unique_words(lyrics_dict)
    sorted_unique_words = dict(
        sorted(
            unique_words_dict.items(),
            key=lambda item: item[1].get("unique_words_count", 0),
        )
    )
    with open("unique_words.json", "w") as f:
        json.dump(sorted_unique_words, f, indent=4)
    with open("unique_words.txt", "w") as f:
        for key, value in sorted_unique_words.items():
            f.write(f"{key} ({value['unique_words_count']})\n")

    # await get_lyrics_from_az_url("https://www.azlyrics.com/lyrics/100gecs/moneymachine.html")

    await close_tor_sessions()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")
        asyncio.run(close_tor_sessions())
        exit(0)
