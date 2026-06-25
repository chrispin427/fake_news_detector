# src/timeline_checker.py

from datetime import datetime


def check_timeline(publish_date):

    if publish_date is None:

        return {
            "status": "Unknown",
            "years_old": None
        }

    try:

        now = datetime.now()

        age_days = (
            now - publish_date
        ).days

        years_old = round(
            age_days / 365,
            1
        )

        if age_days > 365:

            status = "Old Article"

        elif age_days > 90:

            status = "Not Recent"

        else:

            status = "Recent"

        return {
            "status": status,
            "years_old": years_old
        }

    except Exception:

        return {
            "status": "Unknown",
            "years_old": None
        }