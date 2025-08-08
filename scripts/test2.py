import os
import sys
import django
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rojgar_project.settings")
django.setup()

from core.models import JobPost, AdmitCard, Result

BASE_URL = "https://www.rojgarresult.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ------------------ HELPERS ------------------

def fetch_home_links():
    """Scrape all links from homepage."""
    try:
        res = requests.get(BASE_URL, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print("❌ Request failed:", e)
        return []

    soup = BeautifulSoup(res.content, "html.parser")
    anchors = soup.select("a[href^='https://www.rojgarresult.com/']")
    
    links = []
    for a in anchors:
        title = " ".join(a.get_text(strip=True).split())
        href = a.get("href")
        if title and href:
            links.append((title, href))
    return links

def filter_jobs(links):
    job_keywords = ["recruitment", "online form", "vacancy"]
    return [(t, l) for t, l in links if any(k in t.lower() for k in job_keywords)]

# ------------------ DETAIL SCRAPER ------------------

def scrape_job_details(link):
    """Scrape details from a single job page."""
    try:
        res = requests.get(link, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to fetch {link}:", e)
        return None

    soup = BeautifulSoup(res.content, "html.parser")

    # Initialize fields
    details = {
        "title": "",
        "eligibility": "",
        "how_to_apply": "",
        "important_links": "",
        "important_dates": "",
        "age_limit": "",
        "exam_fee": "",
        "total_posts": "",
        "apply_link": "",
       # "full_link": link
    }

    # Title
    if soup.title:
        details["title"] = soup.title.get_text(strip=True)

    # Extract text from tables and headings
    for row in soup.find_all(["tr", "p"]):
        text = row.get_text(" ", strip=True).lower()

        if "eligibility" in text:
            details["eligibility"] += row.get_text(" ", strip=True) + "\n"
        elif "how to apply" in text:
            details["how_to_apply"] += row.get_text(" ", strip=True) + "\n"
        elif "important link" in text:
            details["important_links"] += row.get_text(" ", strip=True) + "\n"
        elif "important date" in text:
            details["important_dates"] += row.get_text(" ", strip=True) + "\n"
        elif "age limit" in text:
            details["age_limit"] += row.get_text(" ", strip=True) + "\n"
        elif "application fee" in text or "exam fee" in text:
            details["exam_fee"] += row.get_text(" ", strip=True) + "\n"
        elif "total post" in text:
            details["total_posts"] += row.get_text(" ", strip=True) + "\n"

    # Apply link
    apply_anchor = soup.find("a", string=lambda s: s and "apply" in s.lower())
    if apply_anchor and apply_anchor.get("href"):
        details["apply_link"] = urljoin(link, apply_anchor["href"])

    return details

# ------------------ SAVE FUNCTIONS ------------------

def save_job_details(details):
    if not details:
        return
    if not JobPost.objects.filter(title=details["title"]).exists():
        JobPost.objects.create(
            title=details["title"],
            category="Latest Job",
            description=details["eligibility"],
            last_date=datetime.today().date(),
            apply_link=details["apply_link"],
            #full_link=details["full_link"],
            eligibility=details["eligibility"],
            how_to_apply=details["how_to_apply"],
            important_links=details["important_links"],
            important_dates=details["important_dates"],
            age_limit=details["age_limit"],
            exam_fee=details["exam_fee"],
            total_posts=details["total_posts"],
        )
        print(f"✅ Job saved: {details['title']}")
    else:
        print(f"⏩ Job already exists: {details['title']}")

# ------------------ MAIN ------------------

if __name__ == "__main__":
    all_links = fetch_home_links()
    jobs = filter_jobs(all_links)

    print(f"🔍 Found {len(jobs)} job links.")

    for title, link in jobs:
        print(f"\n📄 Scraping job: {title}")
        job_data = scrape_job_details(link)
        save_job_details(job_data)

    print("\n✅ All job details scraped and saved.")
