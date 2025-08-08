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

# ------------------ HELPERS ------------------

def fetch_home_links():
    """Scrape all links from homepage."""
    try:
        res = requests.get(BASE_URL, timeout=10)
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


def filter_links(links, keywords):
    return [(t, l) for t, l in links if any(k in t.lower() for k in keywords)]

def filter_jobs(links):
    return filter_links(links, ["recruitment", "online form", "vacancy"])

def filter_admit_cards(links):
    return filter_links(links, ["admit card", "hall ticket", "call letter"])

def filter_results(links):
    return filter_links(links, ["result", "final list", "merit list"])


def get_official_link(detail_url):
    """Open the rojgarresult detail page and extract official link if present."""
    try:
        res = requests.get(detail_url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"⚠️ Failed to fetch {detail_url}: {e}")
        return detail_url

    soup = BeautifulSoup(res.content, "html.parser")
    for a in soup.select("a[href]"):
        href = a.get("href")
        if href and not href.startswith(BASE_URL):  # External link
            return href
    return detail_url


def preview_data(category, data):
    print(f"\n=== {category.upper()} PREVIEW ===")
    for idx, (title, link) in enumerate(data, start=1):
        print(f"{idx}. {title} -> {link}")
    print(f"Total {category}: {len(data)}")


# ------------------ SAVE FUNCTIONS ------------------

def save_jobs(data):
    for title, link in data:
        official_link = get_official_link(link)
        if not JobPost.objects.filter(title=title).exists():
            JobPost.objects.create(
                title=title,
                category="Latest Job",
                description="Not available",
                last_date=datetime.today().date(),
                apply_link=official_link
            )
            print(f"✅ Job saved: {title}")

def save_admit_cards(data):
    for title, link in data:
        official_link = get_official_link(link)
        if not AdmitCard.objects.filter(title=title).exists():
            AdmitCard.objects.create(
                title=title,
                exam_date=None,
                download_link=official_link,
                date_published=datetime.today().date(),
                category="Latest Admit Card"
            )
            print(f"✅ Admit Card saved: {title}")

def save_results(data):
    for title, link in data:
        official_link = get_official_link(link)
        if not Result.objects.filter(title=title).exists():
            Result.objects.create(
                title=title,
                result_link=official_link,
                result_date=datetime.today().date(),
                category="Latest Result"
            )
            print(f"✅ Result saved: {title}")


# ------------------ MAIN ------------------

if __name__ == "__main__":
    all_links = fetch_home_links()
    
    jobs = filter_jobs(all_links)
    admits = filter_admit_cards(all_links)
    results = filter_results(all_links)

    # Preview
    preview_data("Jobs", jobs)
    preview_data("Admit Cards", admits)
    preview_data("Results", results)

    # Confirm save
    confirm = input("\nSave to DB? (y/n): ").strip().lower()
    if confirm == 'y':
        save_jobs(jobs)
        save_admit_cards(admits)
        save_results(results)
        print("\n✅ All data saved to database.")
    else:
        print("\n❌ No data saved.")
