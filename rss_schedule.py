import schedule
import time
from sync.vnexpress import get_rss_list, insert_rss, vn_url
from sync.nld import SyncNLD


def sync_vne():
    print("Syncing VNE..")
    rss_list = get_rss_list()
    src_ids = []

    for rss_url in rss_list:
        if rss_url == "/rss/tin-moi-nhat.rss":
            continue
        insert_rss(vn_url + rss_url, src_ids)


def sync_nld():
    print("Syncing NLD..")
    m = SyncNLD()
    m.insert_rss_all()


def job():
    sync_vne()
    sync_nld()


# Run every 5 minutes
schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(10)
