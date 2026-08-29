"""Helper: scrape the ASRS Report Sets index page for PDF URLs.

This is the ONE piece of working code in the kit, because fetching a list of
links is not the skill you're being hired for.

Run:  python scripts/list_report_sets.py > data/report_set_urls.txt
Then pick 8-10 lines from that file and feed them to fetch_report_sets().
"""
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

INDEX = "https://asrs.arc.nasa.gov/search/reportsets.html"

def main() -> None:
    html = httpx.get(INDEX, timeout=30, follow_redirects=True).text
    soup = BeautifulSoup(html, "html.parser")
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            url = urljoin(INDEX, href)
            if url not in seen:
                seen.add(url)
                print(url)
    if not seen:
        raise SystemExit(
            "No PDF links found — the page structure may have changed. "
            "Open the index page in a browser and copy the links manually."
        )

if __name__ == "__main__":
    main()
