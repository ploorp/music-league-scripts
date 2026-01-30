import asyncio
from bs4 import BeautifulSoup
from tor_utils_async import get_via_tor, init_tor_sessions, close_tor_sessions

lyric_class = "song-lyric"

async def fetch_page(url: str) -> BeautifulSoup:
    print(f"Fetching {url}")
    response = await get_via_tor(url)
    return BeautifulSoup(response, "lxml")

async def get_lyrics_from_url(url: str):
    response = await fetch_page(url)

    lyrics = response.find_all("p", class_=lyric_class)
    print(f"Found {len(lyrics)} lines")
    
    result = "\n".join(lyric.get_text() for lyric in lyrics)

    return result

async def main():
    print("Hello Chat!!!")
    await init_tor_sessions()
    

    lyrics = await get_lyrics_from_url("https://in2.bloat.cat/100-gecs-money-machine-lyrics?id=4589240")

    print(lyrics)

    await close_tor_sessions()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting...")
        asyncio.run(close_tor_sessions())
        exit(0)