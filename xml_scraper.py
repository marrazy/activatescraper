import asyncio
import httpx


from logger import log_error

URL = "https://www.activateuts.com.au/club-sitemap.xml"

async def scrape_xml(client, url, semaphore: asyncio.Semaphore = asyncio.Semaphore()):
    async with semaphore:
        try:
            resp = await client.get(url)

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", "5"))
                print(f"Rate limited on {url}, retrying in {retry_after}s...")
                await asyncio.sleep(retry_after)
                return await scrape_xml(client, url)
            
            if resp.status_code != 200:
                log_error(url, resp.status_code, resp.text)
                return url, {"error": f"Status code {resp.status_code}"}


        except Exception as e:
                    log_error(url, "Exception", str(e))
                    return url, {"error": str(e)}
    

import requests



TEST = requests.get("https://www.activateuts.com.au/club-sitemap.xml")
print(TEST.content)