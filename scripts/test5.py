import os
import sys
import django
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import re
import gradio as gr

# Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rojgar_project.settings")
django.setup()

from core.models import JobPost

BASE_URL = "https://www.rojgarresult.com/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# ------------------ HELPERS ------------------

def fetch_home_links():
    try:
        res = requests.get(BASE_URL, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except Exception as e:
        return [], f"❌ Request failed: {e}"

    soup = BeautifulSoup(res.content, "html.parser")
    anchors = soup.select("a[href^='https://www.rojgarresult.com/']")

    links = []
    for a in anchors:
        title = " ".join(a.get_text(strip=True).split())
        href = a.get("href")
        if title and href:
            links.append((title, href))
    return links, None

def filter_jobs(links):
    job_keywords = ["recruitment", "online form", "vacancy"]
    return [(t, l) for t, l in links if any(k in t.lower() for k in job_keywords)]

def clean_eligibility(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(Read the Notification\.?)+', 'Read the Notification.', text, flags=re.IGNORECASE)
    sentences = []
    for sentence in text.split('. '):
        sentence = sentence.strip()
        if sentence and sentence not in sentences:
            sentences.append(sentence)
    return '. '.join(sentences).strip()

def scrape_job_details(link):
    try:
        res = requests.get(link, headers=HEADERS, timeout=10)
        res.raise_for_status()
    except Exception as e:
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
        details["image_url"] = meta_img["content"]

    publish_date = soup.find("meta", property="article:published_time")
    if publish_date and publish_date.get("content"):
        details["publish_date"] = publish_date["content"]

    updated_date = soup.find("meta", property="article:modified_time")
    if updated_date and updated_date.get("content"):
        details["updated_date"] = updated_date["content"]

    for row in soup.find_all(["tr", "p"]):
        text = row.get_text(" ", strip=True).lower()
        if "eligibility" in text:
            raw_eligibility = row.get_text(" ", strip=True)
            details["eligibility"] += clean_eligibility(raw_eligibility) + "\n"
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
        return "❌ No details"
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
        return f"✅ Saved: {details['title']}"
    else:
        return f"⏩ Already exists: {details['title']}"

# ------------------ GRADIO INTERFACE ------------------

def run_scraper():
    links, error = fetch_home_links()
    if error:
        return {"error": error}
    
    jobs = filter_jobs(links)
    results = []
    for title, link in jobs:
        details = scrape_job_details(link)
        if details:
            msg = save_job_details(details)
            results.append({"title": details["title"], "status": msg, "apply_link": details["apply_link"]})
    return results

demo = gr.Interface(
    fn=run_scraper,
    inputs=[],
    outputs="json",
    title="RojgarResult Job Scraper",
    description="Scrapes latest job posts from RojgarResult.com and saves them into the Django database."
)

if __name__ == "__main__":
    demo.launch(share=True)  # share=True for public Hugging Face link
