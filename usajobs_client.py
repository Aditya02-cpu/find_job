"""
USAJobs API client.
Fetches real government job postings from the USAJobs public API.
"""

import requests
from config import Config


class USAJobsClient:
    """Client for the USAJobs.gov API."""

    def __init__(self):
        self.base_url = Config.USAJOBS_BASE_URL
        self.headers = {
            "Host": "data.usajobs.gov",
            "User-Agent": Config.USAJOBS_EMAIL,
            "Authorization-Key": Config.USAJOBS_API_KEY,
        }

    def search_jobs(
        self,
        keyword: str = "",
        location: str = "",
        position_title: str = "",
        results_per_page: int = 25,
        page: int = 1,
    ) -> dict:
        """
        Search USAJobs for listings matching the given criteria.

        Args:
            keyword: General search keyword (e.g., "data scientist").
            location: Location filter (e.g., "Washington, DC").
            position_title: Specific position title filter.
            results_per_page: Number of results per page (max 500).
            page: Page number for pagination.

        Returns:
            Parsed JSON response from the USAJobs API.
        """
        params = {
            "ResultsPerPage": results_per_page,
            "Page": page,
        }
        if keyword:
            params["Keyword"] = keyword
        if location:
            params["LocationName"] = location
        if position_title:
            params["PositionTitle"] = position_title

        response = requests.get(
            self.base_url,
            headers=self.headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def parse_job_listings(self, raw_response: dict) -> list[dict]:
        """
        Extract clean job listing data from the raw USAJobs API response.

        Returns a list of dicts with relevant fields for each job.
        """
        results = []
        search_result = raw_response.get("SearchResult", {})
        items = search_result.get("SearchResultItems", [])

        for item in items:
            matched = item.get("MatchedObjectDescriptor", {})
            position_loc = matched.get("PositionLocation", [{}])
            location_name = position_loc[0].get("LocationName", "N/A") if position_loc else "N/A"

            user_area = matched.get("UserArea", {}).get("Details", {})
            major_duties = user_area.get("MajorDuties", "N/A")
            qualifications = matched.get("QualificationSummary", "N/A")

            # Pay range
            position_remuneration = matched.get("PositionRemuneration", [{}])
            if position_remuneration:
                pay_min = position_remuneration[0].get("MinimumRange", "N/A")
                pay_max = position_remuneration[0].get("MaximumRange", "N/A")
                pay_interval = position_remuneration[0].get("RateIntervalCode", "")
                salary = f"${pay_min} - ${pay_max} {pay_interval}"
            else:
                salary = "N/A"

            results.append({
                "title": matched.get("PositionTitle", "N/A"),
                "organization": matched.get("OrganizationName", "N/A"),
                "department": matched.get("DepartmentName", "N/A"),
                "location": location_name,
                "salary": salary,
                "grade": matched.get("JobGrade", [{}])[0].get("Code", "N/A") if matched.get("JobGrade") else "N/A",
                "url": matched.get("PositionURI", "N/A"),
                "open_date": matched.get("PositionStartDate", "N/A"),
                "close_date": matched.get("PositionEndDate", "N/A"),
                "description": matched.get("UserArea", {}).get("Details", {}).get("JobSummary", "N/A"),
                "duties": major_duties,
                "qualifications": qualifications,
                "position_id": matched.get("PositionID", "N/A"),
            })

        return results

    def fetch_and_parse(
        self,
        keyword: str = "",
        location: str = "",
        position_title: str = "",
        results_per_page: int = 25,
    ) -> tuple[list[dict], int]:
        """
        Convenience method: fetch jobs and return parsed results + total count.

        Returns:
            Tuple of (list of parsed job dicts, total result count).
        """
        raw = self.search_jobs(
            keyword=keyword,
            location=location,
            position_title=position_title,
            results_per_page=results_per_page,
        )
        total = int(
            raw.get("SearchResult", {}).get("SearchResultCount", 0)
        )
        jobs = self.parse_job_listings(raw)
        return jobs, total
