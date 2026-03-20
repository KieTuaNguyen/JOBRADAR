import re
import time
import uuid
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

JOB_TITLES = [
    "Data Engineer",
    "Data Analyst",
    "Data Scientist",
    "ML Engineer",
]

LOCATIONS = [
    "New South Wales",
]

PAGES_PER_COMBO = 5
SLEEP_PAGE     = 3
SLEEP_DETAIL   = 2
OUTPUT_DIR     = Path(__file__).resolve().parents[1] / "data" / "raw"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

def get_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-AU")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=options)


def safe(card, sel: str) -> str:
    els = card.find_elements(By.CSS_SELECTOR, sel)
    return els[0].text.strip() if els else "N/A"


def fix_encoding(text: str) -> str:
    if not text or text == "N/A":
        return text
    try:
        return text.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def clean_url(url: str | None) -> str | None:
    return url.split("?")[0] if url else None


def parse_posted_date(text: str) -> str | None:
    if not text or text == "N/A":
        return None
    today = datetime.today()
    text  = text.lower().replace("posted", "").replace("ago", "").strip()
    match = re.match(r"(\d+)\s*(h|d|mo|w|m|y)", text)
    if not match:
        return None
    value, unit = int(match.group(1)), match.group(2)
    deltas = {
        "h":  timedelta(hours=value),
        "d":  timedelta(days=value),
        "w":  timedelta(weeks=value),
        "mo": timedelta(days=value * 30),
        "m":  timedelta(days=value * 30),
        "y":  timedelta(days=value * 365),
    }
    delta = deltas.get(unit)
    return (today - delta).strftime("%Y-%m-%d") if delta else None


def build_url(query: str, location: str, page: int) -> str:
    q = query.replace(" ", "+")
    l = location.replace(" ", "+")
    return f"https://au.jora.com/j?q={q}&l={l}&p={page}&sfr=5"

def collect_cards(driver, query: str, location: str, page: int) -> list[dict]:
    url = build_url(query, location, page)
    log.info("Fetching: %s", url)
    driver.get(url)
    time.sleep(SLEEP_PAGE)

    cards = driver.find_elements(By.CSS_SELECTOR, "div.job-card[data-job-card]")
    log.info("  Found %d cards on page %d", len(cards), page)

    card_data = []
    for card in cards:
        title_el = card.find_elements(By.CSS_SELECTOR, "h2.job-title a")
        card_data.append({
            "title":      title_el[0].text.strip() if title_el else "N/A",
            "company":    safe(card, "span.job-company"),
            "location":   safe(card, "a.job-location"),
            "posted_raw": safe(card, "span.job-listed-date"),
            "url":        clean_url(title_el[0].get_attribute("href")) if title_el else None,
            "search_title":    query,
            "search_location": location,
        })
    return card_data


def fetch_description(driver, url: str) -> str:
    try:
        driver.get(url)
        time.sleep(SLEEP_DETAIL)
        desc_el = driver.find_elements(By.CSS_SELECTOR, "div#job-description-container")
        raw = desc_el[0].text.strip() if desc_el else "N/A"
        return fix_encoding(raw)
    except Exception as e:
        log.warning("  Failed to fetch description: %s", e)
        return f"Error: {e}"


def build_row(job: dict, description: str) -> dict:
    return {
        "job_id":           str(uuid.uuid4()),
        "title":            fix_encoding(job["title"]),
        "company":          fix_encoding(job["company"]),
        "location":         fix_encoding(job["location"]),
        "date_posted":      parse_posted_date(job["posted_raw"]),
        "description":      description,
        "job_url":          job["url"],
        "search_title":     job["search_title"],
        "search_location":  job["search_location"],
        "scraped_at":       datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
    }


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def scrape_all(
    job_titles: list[str]  = JOB_TITLES,
    locations:  list[str]  = LOCATIONS,
    pages:      int        = PAGES_PER_COMBO,
) -> pd.DataFrame:
    driver    = get_driver()
    all_cards = []

    for title in job_titles:
        for location in locations:
            for page in range(1, pages + 1):
                cards = collect_cards(driver, title, location, page)
                all_cards.extend(cards)
                if not cards:
                    log.info("  No cards on page %d — stopping pagination for '%s' / %s", page, title, location)
                    break

    log.info("Total cards collected (pre-dedup): %d", len(all_cards))

    seen_urls: set[str] = set()
    unique_cards = []
    for card in all_cards:
        key = card["url"] or card["title"] + card["company"]
        if key not in seen_urls:
            seen_urls.add(key)
            unique_cards.append(card)

    log.info("Unique jobs after dedup: %d", len(unique_cards))

    rows = []
    total = len(unique_cards)
    for i, job in enumerate(unique_cards, start=1):
        description = fetch_description(driver, job["url"]) if job["url"] else "N/A"
        row = build_row(job, description)
        rows.append(row)
        log.info("  [%d/%d] ✓ %s @ %s", i, total, job["title"], job["company"])

    driver.quit()

    df = pd.DataFrame(rows, columns=[
        "job_id", "title", "company", "location", "date_posted",
        "description", "job_url", "search_title", "search_location", "scraped_at",
    ])
    return df


def save_raw(df: pd.DataFrame) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts       = datetime.today().strftime("%Y%m%d_%H%M%S")
    out_path = OUTPUT_DIR / f"jora_raw_{ts}.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    log.info("Saved %d rows → %s", len(df), out_path)
    return out_path

if __name__ == "__main__":
    log.info("Starting JOBRADAR scrape...")
    df       = scrape_all()
    out_path = save_raw(df)
    log.info("Done! Shape: %s  →  %s", df.shape, out_path)
    print(df.head())