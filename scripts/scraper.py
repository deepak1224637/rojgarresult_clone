import os
import sys
import django
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rojgar_project.settings")
django.setup()

from core.models import JobPost, AdmitCard, Result, Syllabus

BASE_URL = "https://www.rojgarresult.com/latestjob.php"

def fetch_all_posts():
    print("🔍 Scraping latest posts from rojgarresult.com...")

    try:
        res = requests.get(BASE_URL, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print("❌ Request failed:", e)
        return

    soup = BeautifulSoup(res.content, "html.parser")
    anchors = soup.select("a[href^='https://www.rojgarresult.com/']:not([href*='latestjob.php'])")

    if not anchors:
        print("❌ No posts found. Selector may need adjustment.")
        return

    for a in anchors:
        title = a.get_text(strip=True)
        href = a.get("href")
        if not title or not href:
            continue

        full_link = urljoin(BASE_URL, href.strip().lower())
        saved = False

        # Match and save by type
        if any(keyword in full_link for keyword in ["online-form", "recruitment"]):
            if not JobPost.objects.filter(title=title).exists():
                JobPost.objects.create(
                    title=title,
                    category="Latest Job",
                    description="Auto scraped from rojgarresult.com",
                    last_date=datetime.today().date(),
                    apply_link=full_link
                )
                print(f"✅ Job saved: {title}")
                saved = True

        elif "admit-card" in full_link:
            if not AdmitCard.objects.filter(title=title).exists():
                AdmitCard.objects.create(
                    title=title,
                    download_link=full_link,
                    posted_on=datetime.today()
                )
                print(f"✅ Admit Card saved: {title}")
                saved = True

        elif "result" in full_link:
            if not Result.objects.filter(title=title).exists():
                Result.objects.create(
                    title=title,
                    result_link=full_link,
                    posted_on=datetime.today()
                )
                print(f"✅ Result saved: {title}")
                saved = True

        elif "syllabus" in full_link:
            if not Syllabus.objects.filter(exam_name=title).exists():
                Syllabus.objects.create(
                    exam_name=title,
                    syllabus_pdf=full_link,
                    posted_on=datetime.today()
                )
                print(f"✅ Syllabus saved: {title}")
                saved = True

        if not saved:
            print(f"⏩ Skipped duplicate or unmatched: {title}")

    print("✅ Scraping complete.")

if __name__ == "__main__":
    fetch_all_posts()
