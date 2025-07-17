import schedule
import time
from sync.vnexpress import get_rss_list, insert_rss, vn_url
from sync.nld import SyncNLD


def sync_vne():
    print("Syncing VNE..")
    try:
        rss_list = get_rss_list()
        src_ids = []

        for rss_url in rss_list:
            if rss_url == "/rss/tin-moi-nhat.rss":
                continue
            insert_rss(vn_url + rss_url, src_ids)
    except AttributeError as e:
        print(f"Rss Syncing Error. \n Details: {e}")


def sync_nld():
    print("Syncing NLD..")
    m = SyncNLD()
    m.insert_rss_all()


def job():
    sync_vne()
    sync_nld()


# Run every 5 minutes
schedule.every(1).minutes.do(sync_vne)
schedule.every(1).minutes.do(sync_nld)

while True:
    schedule.run_pending()
    time.sleep(10)
