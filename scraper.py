import time
import requests
from bs4 import BeautifulSoup
from config import REQUEST_TIMEOUT, SCRAPE_DELAY, MAX_BODY_TEXT_LENGTH

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def scrape_website(url: str) -> str:
    """Scrape a company website and return extracted text for context."""
    if not url:
        return ""

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ⚠ Could not fetch {url}: {e}")
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove script/style elements
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    parts = []

    # Title
    title = soup.find("title")
    if title:
        parts.append(f"Title: {title.get_text(strip=True)}")

    # Meta description
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        parts.append(f"Description: {meta['content'].strip()}")

    # Main body text
    body_text = soup.get_text(separator=" ", strip=True)
    if body_text:
        parts.append(f"Content: {body_text[:MAX_BODY_TEXT_LENGTH]}")

    time.sleep(SCRAPE_DELAY)
    return "\n".join(parts)


def scrape_linkedin_about(url: str) -> str:
    """Attempt to scrape the LinkedIn company 'about' page. Returns empty string on failure."""
    if not url:
        return ""

    # Normalize URL to point to the about page
    url = url.rstrip("/")
    if "/about" not in url:
        url = url + "/about"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ⚠ Could not fetch LinkedIn page {url}: {e}")
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove script/style
    for tag in soup(["script", "style"]):
        tag.decompose()

    # LinkedIn public pages have content in specific sections
    parts = []

    # Try to find the about/description section
    for selector in ["section.about", "div.about", "p.about"]:
        about = soup.select(selector)
        if about:
            parts.append(about[0].get_text(separator=" ", strip=True))

    # Fallback: get main content area text
    if not parts:
        main = soup.find("main") or soup.find("body")
        if main:
            text = main.get_text(separator=" ", strip=True)
            parts.append(text[:MAX_BODY_TEXT_LENGTH])

    time.sleep(SCRAPE_DELAY)
    return "\n".join(parts) if parts else ""


def research_company(website: str, linkedin: str) -> str:
    """Gather all available research about a company."""
    sections = []

    website_text = scrape_website(website)
    if website_text:
        sections.append(f"=== COMPANY WEBSITE ===\n{website_text}")

    linkedin_text = scrape_linkedin_about(linkedin)
    if linkedin_text:
        sections.append(f"=== LINKEDIN ABOUT ===\n{linkedin_text}")

    if not sections:
        return "No research data available. Personalize based on the company name only."

    return "\n\n".join(sections)
