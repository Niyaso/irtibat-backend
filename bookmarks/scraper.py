import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_url_metadata(url: str) -> dict:
    result = {
        "title": "",
        "description": "",
        "thumbnail_url": "",
        "favicon_url": "",
    }

    try:
        response = requests.get(url, headers=HEADERS, timeout=8)
        response.raise_for_status()
    except requests.RequestException:
        return result

    soup = BeautifulSoup(response.text, "html.parser")

    # Title — og:title → twitter:title → <title>
    og_title = soup.find("meta", property="og:title")
    twitter_title = soup.find("meta", attrs={"name": "twitter:title"})
    title_tag = soup.find("title")

    if og_title and og_title.get("content"):
        result["title"] = og_title["content"].strip()
    elif twitter_title and twitter_title.get("content"):
        result["title"] = twitter_title["content"].strip()
    elif title_tag:
        result["title"] = title_tag.get_text(strip=True)

    # Description — og:description → twitter:description → meta description
    og_desc = soup.find("meta", property="og:description")
    twitter_desc = soup.find("meta", attrs={"name": "twitter:description"})
    meta_desc = soup.find("meta", attrs={"name": "description"})

    if og_desc and og_desc.get("content"):
        result["description"] = og_desc["content"].strip()
    elif twitter_desc and twitter_desc.get("content"):
        result["description"] = twitter_desc["content"].strip()
    elif meta_desc and meta_desc.get("content"):
        result["description"] = meta_desc["content"].strip()

    # Thumbnail — og:image → twitter:image
    og_image = soup.find("meta", property="og:image")
    twitter_image = soup.find("meta", attrs={"name": "twitter:image"})

    if og_image and og_image.get("content"):
        result["thumbnail_url"] = make_absolute(og_image["content"], url)
    elif twitter_image and twitter_image.get("content"):
        result["thumbnail_url"] = make_absolute(twitter_image["content"], url)

    # Favicon
    favicon = (
        soup.find("link", rel="icon")
        or soup.find("link", rel="shortcut icon")
        or soup.find("link", rel="apple-touch-icon")
    )

    if favicon and favicon.get("href"):
        result["favicon_url"] = make_absolute(favicon["href"], url)
    else:
        parsed = urlparse(url)
        result["favicon_url"] = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"

    return result


def make_absolute(href: str, base_url: str) -> str:
    if not href:
        return ""
    return urljoin(base_url, href)