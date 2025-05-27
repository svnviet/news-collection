import schedule
import time
from sync.vnexpress import get_rss_list, insert_rss, vn_url


def job():
    print("Job started")
    rss_list = get_rss_list()
    src_ids = []

    for rss_url in rss_list:
        if rss_url == "/rss/tin-moi-nhat.rss":
            continue
        insert_rss(vn_url + rss_url, src_ids)


# Run every 5 minutes
schedule.every(300).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
