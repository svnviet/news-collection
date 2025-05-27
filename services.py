import requests
from bs4 import BeautifulSoup
from sync.vnexpress import collection

vn_url = "https://vnexpress.net/"
base_url = "http://127.0.0.1:5000/"
detail_url = "http://127.0.0.1:5000/vn-vi/news/"


def is_media_content(article_url):
    response = requests.get(article_url)
    soup = BeautifulSoup(response.content, "html.parser")
    soup = soup.find_all("div", {"class": "media_content"})
    return True if len(soup) > 0 else False


def get_vn_express(rss_url, is_slide=False):
    # Load RSS feed
    response = requests.get(rss_url)
    soup = BeautifulSoup(response.content, "xml")

    data = []
    slide_count = 0
    max_slide_count = 10
    idx_is_long = 0
    next_is_long = 10
    # Loop through each item
    for idx, item in enumerate(soup.find_all("item")):
        title = item.title.text
        link = item.link.text.replace(vn_url, "")
        description = item.description.text

        # Extract image URL from description using BeautifulSoup again (HTML inside CDATA)
        desc_soup = BeautifulSoup(description, "html.parser")
        img_tag = desc_soup.find("img")
        image_url = img_tag["src"] if img_tag else None

        is_long = False
        if len(title) > 50:
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

        if is_slide:
            if not image_url:
                continue
            slide_count += 1
            if slide_count > max_slide_count:
                break

        data.append(row)

    return data


def get_article_detail(link):
    resp = requests.get(link)
    soup = BeautifulSoup(resp.text, 'html.parser')

    title = soup.find("h1").get_text(strip=True)
    article_end = soup.find('span', id='article-end')
    if article_end is None:
        author = None
    else:
        p_tag = article_end.find_previous_sibling('p')
        author = p_tag.decode_contents() if p_tag else None

    description = soup.find("p", class_="description")
    content_div = soup.select_one(".fck_detail")

    slide_show_tag = soup.find_all("div", class_="item_slide_show")
    video_show_tag = soup.find_all("div", class_="wrap_video")
    for slide in slide_show_tag:
        slide.decompose()
    for video in video_show_tag:
        video.decompose()

    for tag in content_div.find_all(True):  # True means find all tags
        if tag.name == 'figure':
            try:
                new_tag = make_picture(soup, tag)
                tag.insert_before(new_tag)
                tag.decompose()  # Removes the tag from the tree
            except Exception as e:
                tag.decompose()
        if tag.name == 'a':
            tag['target'] = "_blank"
            tag['href'] = tag['href'].replace(vn_url, detail_url)

    content_html = str(content_div) if content_div else ""

    published_at_tag = soup.find("span", class_="date")
    published_at = published_at_tag.text.strip() if published_at_tag else ""

    return {
        "title": title,
        "author": author,
        "description": description,
        "content": content_html,
        "published_at": published_at,
    }


def get_element_text(element):
    try:
        return element.get_text(strip=True)
    except AttributeError:
        return ""


def make_picture(soup, tag):
    # Create <figure>
    figure = soup.new_tag('figure', attrs={
        'data-size': 'true',
        'itemprop': 'associatedMedia image',
        'itemscope': '',
        'itemtype': 'http://schema.org/ImageObject',
        'class': 'tplCaption action_thumb_added'
    })

    meta_image_url = tag.find('meta', itemprop='url')
    meta_width = tag.find('meta', itemprop='width')
    meta_height = tag.find('meta', itemprop='height')
    meta_caption = tag.find('figcaption', itemprop='description')
    image_url = meta_image_url['content'].replace("amp;", "") if meta_image_url else ""
    width = meta_width['content'] if meta_height else 0
    height = meta_height['content'] if meta_width else 0
    caption = meta_caption.text if meta_caption else ""

    # Add <meta> tags
    for prop, val in [
        ('url', image_url),
        ('width', width),
        ('height', height),
        ('href', '')
    ]:
        meta = soup.new_tag('meta', itemprop=prop, content=val)
        figure.append(meta)

    # fig-picture
    fig_div = tag.find('div', class_='fig-picture')
    fig_picture = soup.new_tag('div', attrs={
        'class': 'fig-picture el_valid',
        'style': save_get_bs(fig_div, 'style'),
        'data-src': image_url,
        'data-sub-html': f'<div class="ss-wrapper"><div class="ss-content"><p class="Image">{caption}</p></div></div>'
    })

    # <picture> with <source> and <img>
    picture = soup.new_tag('picture')
    source = soup.new_tag('source', attrs={
        'data-srcset': f'{image_url} 1x'
    })
    fig_img_src = fig_div.find('img', itemprop="contentUrl")
    intrinsicsize = fig_img_src['intrinsicsize']
    fig_img_style = fig_img_src['style']

    img = soup.new_tag('img', attrs={
        'itemprop': 'contentUrl',
        'src': image_url,
        'alt': caption,
        'class': 'lazy lazied',
        'loading': 'lazy',
        'intrinsicsize': intrinsicsize,
        'style': fig_img_style,
    })
    picture.append(source)
    picture.append(img)
    fig_picture.append(picture)
    figure.append(fig_picture)

    # figcaption
    figcaption = soup.new_tag('figcaption', itemprop='description')
    p_caption = soup.new_tag('p', attrs={'class': 'Image'})
    p_caption.string = caption
    figcaption.append(p_caption)
    figure.append(figcaption)

    return figure


def make_video(soup, tag):
    # Create <figure>
    figure = soup.new_tag('figure', attrs={
        'data-size': 'true',
        'itemprop': 'associatedMedia video',
        'itemscope': '',
        'itemtype': 'http://schema.org/VideoObject',
        'class': 'tplCaption action_thumb_added'
    })

    # Locate embed container
    embed_div = tag.find('div', class_='embed-container')
    video_parent = tag.find('div', class_='box_embed_video_parent')

    # Get data attributes
    video_id = video_parent['data-vid'] if video_parent else ''
    video_url = f'https://example.com/embed/{video_id}' if video_id else ''  # Adjust to your actual embed URL pattern
    width = video_parent.get('data-width', '100%')
    height = video_parent.get('data-height', '382.5px')

    # Caption
    figcaption_div = tag.find('figcaption', class_='desc_cation')
    caption_p = figcaption_div.find('p', class_='Image') if figcaption_div else None
    caption = caption_p.get_text(strip=True) if caption_p else ''

    # Add <meta> tags
    for prop, val in [
        ('contentUrl', video_url),
        ('width', width),
        ('height', height),
        ('href', '')
    ]:
        meta = soup.new_tag('meta', itemprop=prop, content=val)
        figure.append(meta)

    # fig-video
    fig_video = soup.new_tag('div', attrs={
        'class': 'fig-video el_valid',
        'style': save_get_bs(embed_div, 'style'),
        'data-src': video_url,
        'data-sub-html': f'<div class="ss-wrapper"><div class="ss-content"><p class="Video">{caption}</p></div></div>'
    })

    # Reuse the embed container as-is
    if embed_div:
        # Clone the embed container and insert into fig_video
        fig_video.append(embed_div)

    figure.append(fig_video)

    # figcaption
    figcaption = soup.new_tag('figcaption', itemprop='description')
    p_caption = soup.new_tag('p', attrs={'class': 'Video'})
    p_caption.string = caption
    figcaption.append(p_caption)
    figure.append(figcaption)

    return figure


def save_get_bs(content, attribute):
    try:
        return content.get(attribute)
    except AttributeError:
        return ""


def get_item(id=None, link=None):
    if id:
        item = collection.find_one({'_id': id})
    elif link:
        item = collection.find_one({'link': link})
    else:
        item = collection.aggregate([{'$sample': {'size': 1}}]).next()

    item['_id'] = str(item['_id'])
    return item


def get_items(page=1, per_page=14):
    # Get paginated data
    cursor = collection.find().sort("_id", -1).skip((page - 1) * per_page).limit(per_page)

    # Convert cursor to list of dicts (MongoDB documents aren't JSON-serializable by default)
    items = []
    for item in cursor:
        item['_id'] = str(item['_id'])  # convert ObjectId to string
        items.append(item)

    return items


def get_related_items(page=None, per_page=14):
    cursor = collection.aggregate([
        {"$sample": {"size": per_page}}
    ])
    items = []
    for item in cursor:
        item['_id'] = str(item['_id'])  # convert ObjectId to string
        items.append(item)

    return items


def get_related_hot_items(page=None, per_page=20):
    hot_items = get_related_items(per_page=per_page)
    items = []
    slide_count = 1
    max_slide_count = 10
    for item in hot_items:
        item['_id'] = str(item['_id'])  # convert ObjectId to string
        if not item['image_url']:
            continue
        slide_count += 1
        items.append(item)

        if slide_count > max_slide_count:
            break

    return items