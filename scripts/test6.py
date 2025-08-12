import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import gradio as gr

BASE_URL = "https://www.rojgarresult.com/"

# ===== Function to scrape job details from each job link =====
def scrape_job_details(job_url):
    try:
        res = requests.get(job_url)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "lxml")

        details = {
            "title": soup.find("h1").text.strip() if soup.find("h1") else "N/A",
            "how_to_apply": "",
            "important_links": "",
            "important_dates": "",
            "eligibility": "",
            "age_limit": "",
            "exam_fee": "",
            "total_posts": "",
            "apply_link": job_url
        }

        tables = soup.find_all("table")
        for table in tables:
            text = table.get_text(separator="\n").lower()

            if "how to apply" in text:
                details["how_to_apply"] = table.get_text(separator="\n").strip()

            if "important link" in text:
                details["important_links"] = table.get_text(separator="\n").strip()

            if "important date" in text:
                details["important_dates"] = table.get_text(separator="\n").strip()

            if "eligibility" in text:
                details["eligibility"] = table.get_text(separator="\n").strip()

            if "age limit" in text:
                details["age_limit"] = table.get_text(separator="\n").strip()

            if "exam fee" in text:
                details["exam_fee"] = table.get_text(separator="\n").strip()

            if "total post" in text:
                details["total_posts"] = table.get_text(separator="\n").strip()

        return details

    except Exception as e:
        return {"error": str(e)}

# ===== Function to scrape all latest jobs =====
def scrape_latest_jobs():
    try:
        res = requests.get(BASE_URL)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "lxml")

        latest_jobs_section = soup.find("td", string="Latest Jobs")
        if not latest_jobs_section:
            return "Latest Jobs section not found."

        job_links = latest_jobs_section.find_next("table").find_all("a", href=True)
        results = []

        for link in job_links:
            title = link.text.strip()
            job_url = urljoin(BASE_URL, link["href"])
            details = scrape_job_details(job_url)
            results.append(details)

        # Convert to readable format
        output = ""
        for job in results:
            for key, value in job.items():
                output += f"{key.capitalize()}: {value}\n"
            output += "\n" + "="*50 + "\n\n"

        return output

    except Exception as e:
        return str(e)

# ===== Gradio UI =====
def run_scraper():
    return scrape_latest_jobs()

demo = gr.Interface(
    fn=run_scraper,
    inputs=[],
    outputs="text",
    title="Rojgar Result Full Job Scraper",
    description="Scrapes complete job details from rojgarresult.com 'Latest Jobs' section."
)

if __name__ == "__main__":
    demo.launch(share=True)
