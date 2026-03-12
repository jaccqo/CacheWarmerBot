import aiohttp
import asyncio
import xml.etree.ElementTree as ET

SITEMAP_URL = "https://greatestoflove.com/sitemap.xml"
THROTTLE_DELAY = 0.1
MAX_CONCURRENT = 5
HEADERS = {"User-Agent": "CacheWarmerBot/1.0 (+https://greatestoflove.com)"}

async def fetch(session, url, sem, index, total):
    async with sem:
        try:
            async with session.get(url, headers=HEADERS) as resp:
                print(f"[{index}/{total}] {url} -> {resp.status}")
        except Exception as e:
            print(f"[{index}/{total}] {url} -> ERROR: {e}")
        await asyncio.sleep(THROTTLE_DELAY)

async def main():
    # Fetch sitemap
    async with aiohttp.ClientSession() as session:
        async with session.get(SITEMAP_URL, headers=HEADERS) as resp:
            xml_text = await resp.text()

        root = ET.fromstring(xml_text)
        urls = [elem.text for elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        print(f"Found {len(urls)} URLs in sitemap. Warming cache...")

        sem = asyncio.Semaphore(MAX_CONCURRENT)
        tasks = [fetch(session, url, sem, i+1, len(urls)) for i, url in enumerate(urls)]
        await asyncio.gather(*tasks)  # await all tasks before session closes

    print("Cache warming complete!")

if __name__ == "__main__":
    asyncio.run(main())