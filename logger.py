"""
Persistent logging and output management for the Job Application Assistant.

Tracks all application activity and saves generated materials to disk.
"""

import json
import os
from datetime import datetime
from config import Config


class ApplicationLogger:
    """Logs application activity and saves generated materials."""

    def __init__(self):
        Config.ensure_dirs()
        self.log_file = os.path.join(Config.LOG_DIR, "application_log.json")
        self._ensure_log_file()

    def _ensure_log_file(self):
        """Create the log file if it doesn't exist."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _load_log(self) -> list[dict]:
        """Load the application log."""
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_log(self, data: list[dict]):
        """Save the application log."""
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def log_application(
        self,
        job_data: dict,
        outputs: dict,
    ) -> str:
        """
        Log a completed application run and save generated materials.

        Args:
            job_data: The job listing data.
            outputs: Dict with 'analysis', 'resume_cover_letter', 'linkedin_messages'.

        Returns:
            The unique application ID for this entry.
        """
        timestamp = datetime.now().isoformat()
        app_id = f"APP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Save individual output files
        output_subdir = os.path.join(Config.OUTPUT_DIR, app_id)
        os.makedirs(output_subdir, exist_ok=True)

        files_saved = {}
        for key, content in outputs.items():
            if content and key != "full_output":
                filename = f"{key}.md"
                filepath = os.path.join(output_subdir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                files_saved[key] = filepath

        # Add to log
        entry = {
            "app_id": app_id,
            "timestamp": timestamp,
            "job_title": job_data.get("title", "N/A"),
            "organization": job_data.get("organization", "N/A"),
            "location": job_data.get("location", "N/A"),
            "salary": job_data.get("salary", "N/A"),
            "job_url": job_data.get("url", "N/A"),
            "position_id": job_data.get("position_id", "N/A"),
            "files_saved": files_saved,
            "status": "completed",
        }

        log = self._load_log()
        log.append(entry)
        self._save_log(log)

        return app_id

    def get_all_applications(self) -> list[dict]:
        """Return all logged applications."""
        return self._load_log()

    def get_application(self, app_id: str) -> dict | None:
        """Get a specific application by ID."""
        for entry in self._load_log():
            if entry.get("app_id") == app_id:
                return entry
        return None

    def load_saved_output(self, filepath: str) -> str:
        """Load a saved output file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "File not found."
