import asyncio
from bs4 import BeautifulSoup
from tor_utils_async import get_via_tor, init_tor_sessions, close_tor_sessions

lyric_class = "css-146c3p1 r-1inkyih r-11rrj2j r-fdjqy7 r-1dxmaum r-1it3c9n r-135wba7 r-z2wwpe r-15zivkp"

async def fetch_page(url: str) -> BeautifulSoup:
    print(f"Fetching {url}")
    response = await get_via_tor(url)
    return BeautifulSoup(response, "lxml")

async def get_lyrics_from_url(url: str):
    response = await fetch_page("https://www.musixmatch.com/lyrics/100-gecs-Laura-Les-Dylan-Brady/hand-crushed-by-a-mallet")

    lyrics = response.find_all(class_=lyric_class)
    print(f"Found {len(lyrics)} lines")
    
    result = "\n".join(lyric.get_text() for lyric in lyrics)

    return result

async def main():
    print("Hello Chat!!!")
    await init_tor_sessions()
    

    lyrics = await get_lyrics_from_url("https://www.musixmatch.com/lyrics/100-gecs-Laura-Les-Dylan-Brady/hand-crushed-by-a-mallet")

    print(lyrics)
    #print(response.get_text())

    #print(response)

    await close_tor_sessions()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")
        asyncio.run(close_tor_sessions())
        exit(0)