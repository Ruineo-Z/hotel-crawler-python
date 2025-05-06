import time

import pytz
from apscheduler.schedulers.background import BackgroundScheduler

from hotel_crawler import HotelCrawler
from logger import get_logger

logger = get_logger("main")

HOTEL_LIST = [
    "https://www.marriott.com.cn/hotels/ctuwh-w-chengdu/overview/",
    "https://www.marriott.com.cn/hotels/ctumc-chengdu-marriott-hotel-financial-centre/overview/",
    "https://www.marriott.com.cn/hotels/ctuph-four-points-chengdu-high-tech-zone-exhibition-center/overview/",
    "https://www.marriott.com.cn/hotels/ctubr-renaissance-chengdu-hotel/overview/",
    "https://www.marriott.com.cn/hotels/ctuph-four-points-chengdu-high-tech-zone-exhibition-center/overview/"
]


def main():
    crawler_client = HotelCrawler()
    crawler_client.batch_crawl(HOTEL_LIST)


if __name__ == '__main__':
    timezone = pytz.timezone('Asia/Shanghai')
    scheduler = BackgroundScheduler(timezone=timezone)
    # scheduler.add_job(main, id="job", trigger="cron", minute='*/5')
    scheduler.add_job(main, id="job", trigger="cron", hour=16, minute=0)
    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
