"""Google Sheets sync service — fetches publicly accessible sheets via CSV export"""
import csv
import io
import logging
from typing import List, Dict

import httpx


class GoogleSheetsService:
    """Fetches trade data from a publicly shared Google Sheet"""

    # Public CSV export URL — sheet must be shared as "Anyone with the link can view"
    _EXPORT_URL = (
        "https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    )

    def __init__(self, credentials_file: str = ""):
        # credentials_file kept for API compatibility but unused for public sheets
        self.logger = logging.getLogger(__name__)

    def fetch_sheet_data(self, sheet_id: str, range_name: str = "0") -> List[Dict]:
        """
        Fetch data from a publicly shared Google Sheet.

        Args:
            sheet_id: The Google Sheet ID (from the URL)
            range_name: Sheet tab GID as a string (default "0" = first tab).
                        Use the numeric gid from the sheet URL, e.g. "0", "123456789".

        Returns:
            List of row dicts (first row used as headers)
        """
        gid = range_name if range_name.isdigit() else "0"
        url = self._EXPORT_URL.format(sheet_id=sheet_id, gid=gid)

        try:
            response = httpx.get(url, follow_redirects=True, timeout=30)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to fetch sheet {sheet_id}: {e}")
            raise RuntimeError(
                f"Google Sheet fetch failed (HTTP {e.response.status_code}). "
                "Make sure the sheet is shared as 'Anyone with the link can view'."
            )
        except httpx.RequestError as e:
            self.logger.error(f"Network error fetching sheet {sheet_id}: {e}")
            raise RuntimeError(f"Network error fetching Google Sheet: {str(e)}")

        return self._parse_csv(response.text)

    def _parse_csv(self, csv_text: str) -> List[Dict]:
        """Convert CSV text to list of row dicts using the first row as headers"""
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = [dict(row) for row in reader]
        return rows
