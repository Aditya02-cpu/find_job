"""
Indian Jobs API client.
Supports Adzuna, JSearch (RapidAPI), and Jooble with normalized output
matching the format used by the USAJobs client for UI compatibility.
"""

import requests
from config import Config


class IndianJobsClient:
    """Client for Indian job listings from multiple providers."""

    def __init__(self):
        self.provider = Config.INDIAN_JOB_PROVIDER

    def search_jobs(
        self,
        keyword: str = "",
        location: str = "",
        results_per_page: int = 25,
        page: int = 1,
    ) -> dict:
        if self.provider == "adzuna":
            return self._search_adzuna(keyword, location, results_per_page, page)
        elif self.provider == "jsearch":
            return self._search_jsearch(keyword, location, results_per_page, page)
        elif self.provider == "jooble":
            return self._search_jooble(keyword, location, results_per_page, page)
        else:
            raise ValueError(f"Unsupported Indian job provider: {self.provider}")

    def parse_job_listings(self, raw_response: dict) -> list[dict]:
        return raw_response.get("parsed_jobs", [])

    def fetch_and_parse(
        self,
        keyword: str = "",
        location: str = "",
        results_per_page: int = 25,
        page: int = 1,
    ) -> tuple[list[dict], int]:
        raw = self.search_jobs(
            keyword=keyword,
            location=location,
            results_per_page=results_per_page,
            page=page,
        )
        total = raw.get("total", 0)
        jobs = self.parse_job_listings(raw)
        return jobs, total

    def _search_adzuna(
        self,
        keyword: str = "",
        location: str = "",
        results_per_page: int = 25,
        page: int = 1,
    ) -> dict:
        if not Config.ADZUNA_APP_ID or not Config.ADZUNA_APP_KEY:
            raise ValueError(
                "Missing Adzuna API keys. Add ADZUNA_APP_ID and ADZUNA_APP_KEY to your .env file."
            )

        # Adzuna uses 1-based pages
        adzuna_page = max(page, 1)
        url = f"{Config.ADZUNA_BASE_URL}/in/search/{adzuna_page}"
        params = {
            "app_id": Config.ADZUNA_APP_ID,
            "app_key": Config.ADZUNA_APP_KEY,
            "results_per_page": results_per_page,
            "content-type": "application/json",
        }
        if keyword:
            params["what"] = keyword
        if location:
            params["where"] = location
        else:
            params["where"] = "India"

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        parsed_jobs = []
        for item in data.get("results", []):
            company = item.get("company", {}) or {}
            category = item.get("category", {}) or {}
            loc = item.get("location", {}) or {}
            salary_min = item.get("salary_min")
            salary_max = item.get("salary_max")

            if salary_min and salary_max:
                salary = f"₹{int(salary_min):,} - ₹{int(salary_max):,} per annum"
            elif salary_min:
                salary = f"₹{int(salary_min):,}+ per annum"
            elif salary_max:
                salary = f"Up to ₹{int(salary_max):,} per annum"
            else:
                salary = "Not disclosed"

            description = item.get("description", "") or ""
            parsed_jobs.append(
                {
                    "title": item.get("title", "N/A"),
                    "organization": company.get("display_name") or "N/A",
                    "department": category.get("label") or "N/A",
                    "location": loc.get("display_name") or location or "India",
                    "salary": salary,
                    "grade": "N/A",
                    "url": item.get("redirect_url") or "N/A",
                    "open_date": item.get("created") or "N/A",
                    "close_date": "N/A",
                    "description": description[:5000],
                    "duties": description,
                    "qualifications": "N/A",
                    "position_id": item.get("id") or "N/A",
                    "source": "adzuna",
                }
            )

        return {"parsed_jobs": parsed_jobs, "total": data.get("count", len(parsed_jobs))}

    def _search_jsearch(
        self,
        keyword: str = "",
        location: str = "",
        results_per_page: int = 25,
        page: int = 1,
    ) -> dict:
        if not Config.RAPIDAPI_KEY:
            raise ValueError(
                "Missing RapidAPI key. Add RAPIDAPI_KEY to your .env file for JSearch."
            )

        url = "https://jsearch.p.rapidapi.com/search"
        query_parts = []
        if keyword:
            query_parts.append(keyword)
        if location:
            query_parts.append(f"in {location}")
        else:
            query_parts.append("in India")
        query = " ".join(query_parts) or "jobs in India"

        headers = {
            "X-RapidAPI-Key": Config.RAPIDAPI_KEY,
            "X-RapidAPI-Host": Config.RAPIDAPI_JSEARCH_HOST,
        }
        params = {
            "query": query,
            "page": str(page),
            "num_pages": "1",
            "country": "in",
        }

        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        parsed_jobs = []
        for item in data.get("data", []):
            job_title = item.get("job_title") or item.get("title") or "N/A"
            employer = item.get("employer_name") or "N/A"
            city = item.get("job_city") or ""
            state = item.get("job_state") or ""
            country = item.get("job_country") or "India"
            loc_parts = [p for p in [city, state, country] if p]
            location_name = ", ".join(loc_parts) if loc_parts else location or "India"

            salary_min = item.get("job_min_salary")
            salary_max = item.get("job_max_salary")
            salary_period = item.get("job_salary_period") or "yearly"
            if salary_min and salary_max:
                salary = f"₹{salary_min} - ₹{salary_max} {salary_period}"
            elif salary_min:
                salary = f"₹{salary_min}+ {salary_period}"
            elif salary_max:
                salary = f"Up to ₹{salary_max} {salary_period}"
            else:
                salary = "Not disclosed"

            description = item.get("job_description", "") or ""
            qualifications = item.get("job_highlights", {}).get("Qualifications") if isinstance(item.get("job_highlights"), dict) else "N/A"
            if isinstance(qualifications, list):
                qualifications = "\n".join(f"- {q}" for q in qualifications)

            parsed_jobs.append(
                {
                    "title": job_title,
                    "organization": employer,
                    "department": item.get("job_job_title") or "N/A",
                    "location": location_name,
                    "salary": salary,
                    "grade": "N/A",
                    "url": item.get("job_apply_link") or item.get("job_google_link") or "N/A",
                    "open_date": item.get("job_posted_at_datetime_utc") or "N/A",
                    "close_date": "N/A",
                    "description": description[:5000],
                    "duties": description,
                    "qualifications": qualifications or "N/A",
                    "position_id": item.get("job_id") or "N/A",
                    "source": "jsearch",
                }
            )

        total = data.get("total", len(parsed_jobs))
        return {"parsed_jobs": parsed_jobs, "total": total}

    def _search_jooble(
        self,
        keyword: str = "",
        location: str = "",
        results_per_page: int = 25,
        page: int = 1,
    ) -> dict:
        if not Config.JOOBLE_API_KEY:
            raise ValueError("Missing Jooble API key. Add JOOBLE_API_KEY to your .env file.")

        url = f"https://jooble.org/api/{Config.JOOBLE_API_KEY}"
        payload = {
            "keywords": keyword or "jobs",
            "location": location or "India",
            "page": page,
            "searchRadius": "50",
        }

        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        parsed_jobs = []
        for item in data.get("jobs", []):
            salary = item.get("salary") or "Not disclosed"
            description = item.get("snippet", "") or item.get("description", "") or ""

            parsed_jobs.append(
                {
                    "title": item.get("title", "N/A"),
                    "organization": item.get("company", "N/A"),
                    "department": "N/A",
                    "location": item.get("location", location or "India"),
                    "salary": salary,
                    "grade": "N/A",
                    "url": item.get("link", "N/A"),
                    "open_date": item.get("updated") or "N/A",
                    "close_date": "N/A",
                    "description": description[:5000],
                    "duties": description,
                    "qualifications": "N/A",
                    "position_id": item.get("id") or "N/A",
                    "source": "jooble",
                }
            )

        total = data.get("totalCount", len(parsed_jobs))
        return {"parsed_jobs": parsed_jobs, "total": total}
