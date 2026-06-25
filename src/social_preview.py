import requests
from bs4 import BeautifulSoup


def get_preview(url):
    """
    Extract preview information from a URL
    using Open Graph metadata.
    """

    try:
        headers = {
            "User-Agent":
            "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=20,
            allow_redirects=True
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        title = None
        description = None
        image = None

        # Open Graph tags
        og_title = soup.find(
            "meta",
            property="og:title"
        )

        og_description = soup.find(
            "meta",
            property="og:description"
        )

        og_image = soup.find(
            "meta",
            property="og:image"
        )

        if og_title:
            title = og_title.get("content")

        if og_description:
            description = og_description.get("content")

        if og_image:
            image = og_image.get("content")

        return {
            "title": title,
            "description": description,
            "image": image
        }

    except Exception as e:

        print(
            "Preview Error:",
            e
        )

        return None