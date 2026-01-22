from datetime import date, datetime


class DateUtils:

    @staticmethod
    def parse_date(date_str: str) -> date:
        if not date_str:
            return None

        formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        raise ValueError(f"Date string '{date_str}' is not in a recognized format.")
