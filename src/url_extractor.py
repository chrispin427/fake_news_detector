from newspaper import Article


def extract_article(url):
    try:
        article = Article(url)

        article.download()
        article.parse()

        return {
            "success": True,
            "title": article.title,
            "text": article.text,
            "authors": article.authors,
            "publish_date": article.publish_date,
            "top_image": article.top_image,
            "url": url
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    url = input("Enter URL: ")

    result = extract_article(url)

    if result["success"]:
        print("\nTITLE:")
        print(result["title"])

        print("\nTEXT:")
        print(result["text"][:1000])

    else:
        print("ERROR:", result["error"])