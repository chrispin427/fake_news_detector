import re


def is_url(text):
    url_pattern = r"https?://[^\s]+"
    return bool(re.match(url_pattern, text.strip()))