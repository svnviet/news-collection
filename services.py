import requests
from bs4 import BeautifulSoup


def get_vn_express(rss_url, is_slide=False):
    # Load RSS feed
    response = requests.get(rss_url)
    soup = BeautifulSoup(response.content, "xml")

    data = []
    next_is_long = 10
    idx_is_long = 0
    # Loop through each item
    for idx, item in enumerate(soup.find_all("item")):
        title = item.title.text
        link = item.link.text
        description = item.description.text

        # Extract image URL from description using BeautifulSoup again (HTML inside CDATA)
        desc_soup = BeautifulSoup(description, "html.parser")
        img_tag = desc_soup.find("img")
        image_url = img_tag["src"] if img_tag else None

        is_long = False
        if len(title) > 10:
            if idx_is_long < (idx - next_is_long):
                is_long = True
                idx_is_long = idx

        row = {
            "title": title,
            "link": link,
            "image_url": image_url,
            "source_logo_url": "logo/vne_logo_rss.png",
            "description": description,
        }
        if is_slide == False:
            row["is_long"] = is_long

        data.append(row)

    return data
