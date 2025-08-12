#!/usr/bin/env python3
"""
Robust scraper for rojgarresult.com that:
- Fetches links from homepage
- Filters probable job/recruitment posts
- Scrapes details with safer parsing
- Optionally sends data to Hugging Face for cleaning
- Saves to Django JobPost model with improved duplicate checking
- Supports --auto-save for cron use
"""

import os
import sys
import argparse
import traceback
import django
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import re
import json
from dotenv import load_dotenv

# Load .env
load_dotenv()

# ============= Django setup =============
# Adjust path if script is inside a separate folder; update as needed
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rojgar_project.settings")
django.setup()

from core.models import JobPost  # noqa: E402

# ============= Config =============
BASE_URL = "https://www.rojgarresult.com/"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/80 Safari/537.36"}
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"

# ============= Helpers =============
def safe_request_get(url, timeout=15):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r
    except Exception:
        traceback.print_exc()
        return None

def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def text_from_tag(tag):
    """Return normalized text from a BS tag preserving nested text."""
    if not tag:
        return ""
    return normalize_whitespace(" ".join(tag.stripped_strings))

# Simple date parser: tries multiple patterns, returns ISO date string or None
DATE_PATTERNS = [
    (r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", ["%d-%m-%Y", "%d/%m/%Y", "%d-%m-%y", "%d/%m/%y"]),
    (r"(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})", ["%d %B %Y", "%d %b %Y"]),
    (r"([A-Za-z]{3,9}\s+\d{1,2},\s*\d{4})", ["%B %d, %Y", "%b %d, %Y"]),
]

def parse_date_from_text(text):
    if not text:
        return None
    for pattern, fmts in DATE_PATTERNS:
        m = re.search(pattern, text)
        if m:
            s = m.group(1)
            for fmt in fmts:
                try:
                    dt = datetime.strptime(s, fmt)
                    return dt.date().isoformat()
                except Exception:
                    continue
    return None

def extract_last_date(details_text):
    # Try to find specific keywords around dates, else fallback to parsing any date
    if not details_text:
        return None
    # Look for "last date", "last date to apply", "last date for apply", "last date:"
    candidates = re.findall(r"(?i)(last\s+date[^\n:]*[:\-\s]*([^\n]+))", details_text)
    if candidates:
        # candidates is list of tuples; second element has text after "last date"
        for _, chunk in candidates:
            parsed = parse_date_from_text(chunk)
            if parsed:
                return parsed
    # fallback: parse first date in text
    parsed = parse_date_from_text(details_text)
    return parsed

# ============= Hugging Face AI cleaning =============
def process_with_ai(data: dict):
    """Send scraped job data to Hugging Face inference API for cleaning. Returns cleaned dict or original."""
    if not HF_API_KEY:
        print("⚠️ No HF_API_KEY in .env — skipping AI cleaning.")
        return data

    prompt = (
        "You are a data cleaner. Receive a JSON object of job details. "
        "1) Remove HTML tags and extra whitespace. 2) Keep keys unchanged. "
        "3) Output valid JSON only.\n\n"
        f"INPUT_JSON:\n{json.dumps(data, ensure_ascii=False)}\n\nOUTPUT_JSON:"
    )

    try:
        resp = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": prompt},
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.json()

        # Robust extraction of generated text from possible response shapes
        generated_text = None
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                # several HF models return 'generated_text' or 'content' or 'summary_text'
                for key in ("generated_text", "content", "summary_text", "text"):
                    if key in first:
                        generated_text = first[key]
                        break
                # some models return {'generated_text': '...'} nested deeper
                if not generated_text:
                    # try to find first string value
                    for v in first.values():
                        if isinstance(v, str) and len(v) > 10:
                            generated_text = v
                            break
        elif isinstance(result, dict):
            for key in ("generated_text", "content", "summary_text", "text"):
                if key in result:
                    generated_text = result[key]
                    break
            if not generated_text:
                # maybe a direct dict with keys->strings
                for v in result.values():
                    if isinstance(v, str) and len(v) > 10:
                        generated_text = v
                        break

        if not generated_text:
            print("⚠️ Unexpected HF response format — skipping AI cleaning.")
            return data

        # Trim common wrappers (sometimes HF models reply like: "Here is cleaned JSON: {...}")
        json_start = generated_text.find("{")
        json_end = generated_text.rfind("}")
        if json_start != -1 and json_end != -1:
            json_text = generated_text[json_start:json_end + 1]
        else:
            json_text = generated_text

        try:
            cleaned = json.loads(json_text)
            return cleaned if isinstance(cleaned, dict) else data
        except json.JSONDecodeError:
            print("⚠️ HF returned non-JSON text. Using original data.")
            return data

    except Exception:
        traceback.print_exc()
        return data

# ============= Scrape functions =============
def fetch_home_links():
    res = safe_request_get(BASE_URL)
    if not res:
        return []

    soup = BeautifulSoup(res.content, "html.parser")
    anchors = soup.find_all("a", href=True)

    links = []
    for a in anchors:
        href = a["href"].strip()
        # make absolute URL
        full = urljoin(BASE_URL, href)
        # Only keep same-domain links
        if urlparse(full).netloc.endswith("rojgarresult.com"):
            title = text_from_tag(a)
            if title:
                links.append((title, full))
    # remove duplicates while preserving order
    seen = set()
    deduped = []
    for t, l in links:
        if l not in seen:
            deduped.append((t, l))
            seen.add(l)
    return deduped

def filter_jobs(links):
    job_keywords = ["recruitment", "online form", "vacancy", "notification", "apply", "job", "result"]
    filtered = []
    for title, link in links:
        text = f"{title} {link}".lower()
        if any(k in text for k in job_keywords):
            filtered.append((title, link))
    return filtered

def scrape_job_details(link):
    res = safe_request_get(link)
    if not res:
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
        "updated_date": None,
    }

    # Title
    meta_title = soup.find("meta", property="og:title")
    if meta_title and meta_title.get("content"):
        details["title"] = meta_title["content"].strip()
    elif soup.title:
        details["title"] = text_from_tag(soup.title)

    # Description
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        details["description"] = meta_desc["content"].strip()
    else:
        # try main article / post content heuristics
        article = soup.find(["article", "div"], class_=re.compile(r"(post|entry|single|content)", re.I))
        if article:
            details["description"] = text_from_tag(article)[:4000]  # limit length

    # canonical / image / dates
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        details["full_link"] = canonical["href"]

    meta_img = soup.find("meta", property="og:image")
    if meta_img and meta_img.get("content"):
        details["image_url"] = meta_img["content"]

    pub = soup.find("meta", property="article:published_time")
    if pub and pub.get("content"):
        details["publish_date"] = pub["content"]
    mod = soup.find("meta", property="article:modified_time")
    if mod and mod.get("content"):
        details["updated_date"] = mod["content"]

    # Extract structured info from <tr> and <p> and any table-like content
    for tag in soup.find_all(["tr", "p", "li", "div"]):
        text = text_from_tag(tag)
        low = text.lower()
        if not low:
            continue
        if "eligibility" in low:
            details["eligibility"] += text + "\n"
        elif "how to apply" in low or "how to apply:" in low:
            details["how_to_apply"] += text + "\n"
        elif "important link" in low or "important links" in low:
            details["important_links"] += text + "\n"
        elif "important date" in low or "important dates" in low or "last date" in low:
            details["important_dates"] += text + "\n"
        elif "age limit" in low:
            details["age_limit"] += text + "\n"
        elif "application fee" in low or "exam fee" in low or "fees" in low:
            details["exam_fee"] += text + "\n"
        elif "total post" in low or "total vacancy" in low or "total posts" in low:
            details["total_posts"] += text + "\n"

    # find apply link heuristically
    apply_anchor = soup.find("a", string=lambda s: s and "apply" in s.lower())
    if apply_anchor and apply_anchor.get("href"):
        details["apply_link"] = urljoin(link, apply_anchor["href"])
    else:
        # try to find button-like anchors
        for a in soup.find_all("a", href=True):
            if any(k in a.get_text(" ", strip=True).lower() for k in ("apply", "apply now", "online apply")):
                details["apply_link"] = urljoin(link, a["href"])
                break

    # best-effort publish/updated parsing from page text if meta missing
    if not details["publish_date"]:
        details["publish_date"] = parse_date_from_text(text_from_tag(soup)) or None
    if not details["updated_date"]:
        details["updated_date"] = None

    # dedupe/trim fields
    for k in ("eligibility", "how_to_apply", "important_links", "important_dates", "age_limit", "exam_fee", "total_posts"):
        details[k] = normalize_whitespace(details[k]) if details[k] else ""

    # last_date extraction
    details["last_date"] = extract_last_date(details["important_dates"]) or None

    return details

# ============= Save to DB =============
def save_job_details(details):
    if not details:
        return False
    title = details.get("title") or "(no-title)"
    full_link = details.get("full_link") or details.get("full_link")

    # improved duplicate check: use title + link (or slug) to avoid false duplicates
    exists = JobPost.objects.filter(title=title, full_link=full_link).exists()
    if exists:
        print(f"⏩ Job already exists: {title}")
        return False

    # Last date fallback: prefer parsed last_date else None
    last_date_iso = details.get("last_date")
    last_date_val = None
    try:
        if last_date_iso:
            last_date_val = datetime.fromisoformat(last_date_iso).date()
    except Exception:
        last_date_val = None

    JobPost.objects.create(
        title=title,
        category="Latest Job",
        description=details.get("description", ""),
        last_date=last_date_val,
        apply_link=details.get("apply_link") or "",
        full_link=full_link,
        eligibility=details.get("eligibility") or "",
        how_to_apply=details.get("how_to_apply") or "",
        important_links=details.get("important_links") or "",
        important_dates=details.get("important_dates") or "",
        age_limit=details.get("age_limit") or "",
        exam_fee=details.get("exam_fee") or "",
        total_posts=details.get("total_posts") or "",
        image_url=details.get("image_url") or "",
        publish_date=details.get("publish_date"),
        updated_date=details.get("updated_date"),
    )
    print(f"✅ Job saved: {title}")
    return True

# ============= Main CLI =============
def main(auto_save=False, use_ai=False, limit=None):
    print("🔎 Fetching homepage links...")
    links = fetch_home_links()
    print(f"Found {len(links)} links on homepage.")

    jobs = filter_jobs(links)
    if limit:
        jobs = jobs[:limit]
    print(f"Filtered to {len(jobs)} probable job links.\n")

    job_data_list = []
    for title, link in jobs:
        print(f"📄 Scraping: {title} -> {link}")
        try:
            details = scrape_job_details(link)
            if not details:
                print("⚠️ No details found, skipping.")
                continue
            if use_ai:
                details = process_with_ai(details)
            job_data_list.append(details)
        except Exception:
            traceback.print_exc()
            continue

    print(f"\nPrepared {len(job_data_list)} job items.\n")
    # show summary
    for idx, job in enumerate(job_data_list, 1):
        print(f"--- JOB {idx} ---")
        print(f"title: {job.get('title')}")
        print(f"apply_link: {job.get('apply_link')}")
        print(f"last_date: {job.get('last_date')}")
        print(f"full_link: {job.get('full_link')}")
        print()

    if auto_save:
        confirm_save = True
    else:
        ans = input("Save all data to DB? (y/n): ").strip().lower()
        confirm_save = ans == "y"

    if confirm_save:
        for job in job_data_list:
            try:
                save_job_details(job)
            except Exception:
                traceback.print_exc()
        print("\n✅ Done saving.")
    else:
        print("\n❌ Not saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RojgarResult scraper")
    parser.add_argument("--auto-save", action="store_true", help="Save without prompt (for cron)")
    parser.add_argument("--use-ai", action="store_true", help="Send scraped data to HF for cleaning")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of posts to scrape")
    args = parser.parse_args()

    main(auto_save=args.auto_save, use_ai=args.use_ai, limit=args.limit)
