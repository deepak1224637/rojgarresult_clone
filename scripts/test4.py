import os
import sys
import django
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import json
from dotenv import load_dotenv

# ✅ Load environment variables from .env file
load_dotenv()

# ================= Django Setup =================
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rojgar_project.settings")
django.setup()

from core.models import JobPost

BASE_URL = "https://www.rojgarresult.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ================= Hugging Face Setup =================
HF_API_KEY = os.getenv("HF_API_KEY")  # ✅ .env file me set karo: HF_API_KEY=your_key
HF_MODEL = os.getenv("HF_MODEL")  # ✅ Working public model

def process_with_ai(data):
    """Send scraped job data to Hugging Face for AI cleaning in JSON format."""
    if not HF_API_KEY:
        print("⚠️ No Hugging Face API key found in .env. Skipping AI processing.")
        return data

    prompt = f"""
    You are a data cleaner. Take the following job details dictionary and clean it up:
    1. Remove unnecessary whitespace and HTML tags.
    2. Keep all keys the same.
    3. Ensure the output is valid JSON.

    Job Data:
    {json.dumps(data, ensure_ascii=False)}

    Return only cleaned JSON.
    """

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": prompt},
            timeout=60
        )
        response.raise_for_status()
        result = response.json()

        if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
            cleaned_json = result[0]["generated_text"].strip()
            try:
                return json.loads(cleaned_json)
            except json.JSONDecodeError:
                print("⚠️ AI returned invalid JSON. Using original data.")
                return data
        else:
            print("⚠️ Unexpected AI response. Using original data.")
            return data

    except requests.exceptions.HTTPError as http_err:
        print(f"⚠️ HTTP error from Hugging Face: {http_err}")
        return data
    except Exception as e:
        print("⚠️ Hugging Face API error:", e)
        return data

# ================= Helpers =================
def fetch_home_links():
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

def scrape_job_details(link):
    try:
        res = requests.get(link, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to fetch {link}:", e)
        return None

    soup = BeautifulSoup(res.content, "html.parser")

    details = {
        "title": "",
        "description": "",
        "eligibility": "",
        "how_to_apply": "",
        "important_links": "",
        "important_dates": "",
        "age_limit": "",
        "exam_fee": "",
        "total_posts": "",
        "apply_link": "",
        "full_link": link,
        "image_url": "",
        "publish_date": None,
        "updated_date": None
    }

    meta_title = soup.find("meta", property="og:title")
    if meta_title and meta_title.get("content"):
        details["title"] = meta_title["content"]
    elif soup.title:
        details["title"] = soup.title.get_text(strip=True)

    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        details["description"] = meta_desc["content"]

    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        details["full_link"] = canonical["href"]

    meta_img = soup.find("meta", property="og:image")
    if meta_img and meta_img.get("content"):
        details["image_url"] = meta_img.get("content")

    publish_date = soup.find("meta", property="article:published_time")
    if publish_date and publish_date.get("content"):
        details["publish_date"] = publish_date["content"]

    updated_date = soup.find("meta", property="article:modified_time")
    if updated_date and updated_date.get("content"):
        details["updated_date"] = updated_date["content"]

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

    apply_anchor = soup.find("a", string=lambda s: s and "apply" in s.lower())
    if apply_anchor and apply_anchor.get("href"):
        details["apply_link"] = urljoin(link, apply_anchor["href"])

    return details

def save_job_details(details):
    if not details:
        return
    if not JobPost.objects.filter(title=details["title"]).exists():
        JobPost.objects.create(
            title=details["title"],
            category="Latest Job",
            description=details["description"],
            last_date=datetime.today().date(),
            apply_link=details["apply_link"],
            full_link=details["full_link"],
            eligibility=details["eligibility"],
            how_to_apply=details["how_to_apply"],
            important_links=details["important_links"],
            important_dates=details["important_dates"],
            age_limit=details["age_limit"],
            exam_fee=details["exam_fee"],
            total_posts=details["total_posts"],
            image_url=details["image_url"],
            publish_date=details["publish_date"],
            updated_date=details["updated_date"],
        )
        print(f"✅ Job saved: {details['title']}")
    else:
        print(f"⏩ Job already exists: {details['title']}")

# ================= Main =================
if __name__ == "__main__":
    all_links = fetch_home_links()
    jobs = filter_jobs(all_links)

    print(f"\n🔍 Found {len(jobs)} job links.\n")

    job_data_list = []
    for title, link in jobs:
        print(f"📄 Scraping: {title}")
        details = scrape_job_details(link)
        if details:
            details = process_with_ai(details)
            job_data_list.append(details)

    for idx, job in enumerate(job_data_list, start=1):
        print(f"\n=== JOB {idx} ===")
        for k, v in job.items():
            print(f"{k}: {v}")

    confirm = input("\nSave all data to DB? (y/n): ").strip().lower()
    if confirm == "y":
        for job in job_data_list:
            save_job_details(job)
        print("\n✅ All data saved.")
    else:
        print("\n❌ No data saved.")
