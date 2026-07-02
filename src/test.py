from search_fallback import (
    search_from_failed_url
)

url = input("URL: ")

results = search_from_failed_url(url)

for item in results:

    print("\nTITLE:")
    print(item["title"])

    print("\nLINK:")
    print(item["link"])

    print("\nSNIPPET:")
    print(item["snippet"])