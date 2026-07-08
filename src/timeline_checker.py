# src/timeline_checker.py

from datetime import datetime


def check_timeline(publish_date):
    """
    Analyze the publication date of an article.

    - If no publish date is available, return "Unknown" status.
      Unknown is treated as **neutral** by downstream consumers --
      it should NOT reduce credibility simply because the date
      is missing.
    - When a valid date exists, apply normal aging logic.
    """

    if publish_date is None:
        print("  [Timeline] No publish date available -> status=Unknown (neutral - no penalty applied)")
        return {"status": "Unknown", "years_old": None, "debug": {"reason": "No publish date provided", "score_impact": "neutral (no penalty)"}}

    try:
        now = datetime.now()
        age_days = (now - publish_date).days
        years_old = round(age_days / 365, 1)

        if age_days > 365:
            status = "Old Article"
            print(f"  [Timeline] Date={publish_date.date()} -> {age_days}d old -> status=Old Article (penalty applied)")
        elif age_days > 90:
            status = "Not Recent"
            print(f"  [Timeline] Date={publish_date.date()} -> {age_days}d old -> status=Not Recent (partial penalty)")
        else:
            status = "Recent"
            print(f"  [Timeline] Date={publish_date.date()} -> {age_days}d old -> status=Recent (no penalty)")

        return {"status": status, "years_old": years_old, "debug": {"reason": f"Date={publish_date.date()}, age_days={age_days}", "score_impact": "penalty applied" if age_days > 90 else "no penalty"}}
    except Exception as e:
        print(f"  [Timeline] Exception parsing date {publish_date}: {e} -> status=Unknown (neutral)")
        return {"status": "Unknown", "years_old": None, "debug": {"reason": f"Exception: {e}", "score_impact": "neutral (exception fallback)"}}
