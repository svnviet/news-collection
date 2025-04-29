import requests
from bs4 import BeautifulSoup


def get_vn_express(rss_url):
    # Load RSS feed
    response = requests.get(rss_url)
    soup = BeautifulSoup(response.content, "xml")

    data = []

    # Loop through each item
    for item in soup.find_all("item"):
        title = item.title.text
        link = item.link.text
        description = item.description.text

        # Extract image URL from description using BeautifulSoup again (HTML inside CDATA)
        desc_soup = BeautifulSoup(description, "html.parser")
        img_tag = desc_soup.find("img")
        image_url = img_tag["src"] if img_tag else None

        data.append(
            {
                "title": title,
                "link": link,
                "image_url": image_url,
                "source_logo_url": "logo/vne_logo_rss.png"
            }
        )

    return data
