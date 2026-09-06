import asyncio

import json
from pathlib import Path
from urllib.parse import urlparse

import httpx
import xml.etree.ElementTree as ET

from logger import log_error

URL = "https://www.activateuts.com.au/club-sitemap.xml"
OUT_PATH = Path(__file__).parent / "files" / "club_paths.json"


async def get_sitemap(client: httpx.AsyncClient, url: str, retries: int = 3) -> str:
    try:
        resp = await client.get(url)

        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", "5"))
            print(f"Rate limited on {url}, retrying in {retry_after}s...")
            await asyncio.sleep(retry_after)
            if retries > 0:
                return await get_sitemap(client, url, retries - 1)
            raise httpx.HTTPStatusError(
                "Too many retries (429)",
                request=resp.request,
                response=resp,
            )

        resp.raise_for_status()
        return resp.text

    except Exception as e:
        log_error(url, "Exception", str(e))
        return ""


def extract_locs(xml_text: str) -> list[str]:
    sitemap = ET.fromstring(xml_text)
    locs = [el.text.strip() for el in sitemap.findall(".//{*}loc") if el.text and el.text.strip()]
    if not locs:
        for el in sitemap.iter():
            if el.tag.lower().endswith("loc") and el.text:
                locs.append(el.text.strip())
    return locs

def urls_from_locs(locs: list[str]) -> list[str]:
    if any(loc.lower().endswith(".xml") for loc in locs):
        return []  
    return locs

def build_mapping(urls: list[str]) -> dict:
    mapping: dict[str, str] = {}
    for u in urls:
        parsed = urlparse(u)
        path = parsed.path.rstrip("/")
        if not path:
            continue
        slug = path.split("/")[-1]
        mapping[slug] = path
    return mapping

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        root_xml = await get_sitemap(client, URL)
        locs = extract_locs(root_xml)

        urls: list[str] = []
        if any(loc.lower().endswith(".xml") for loc in locs):
            for sitemap_loc in locs:
                try:
                    sub_xml = await get_sitemap(client, sitemap_loc)
                    urls.extend(extract_locs(sub_xml))
                except Exception:
                    continue
        else:
            urls = locs

    mapping = build_mapping(urls)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=4)

    print(f"Wrote {len(mapping)} entries to {OUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())

