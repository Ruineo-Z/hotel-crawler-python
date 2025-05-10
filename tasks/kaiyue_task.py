import os

from concurrent.futures import ThreadPoolExecutor, as_completed

import tools
from crawler.kaiyue_crawler import KYCrawler
from config import settings
from logger import get_logger

logger = get_logger("kaiyue-task")


def fetch_lowest_price(hotel_id):
    init_cookie = os.getenv("KAIYUE_COOKIE")
    client = KYCrawler(hotel_id=hotel_id, x_kpsdk_ct=init_cookie)

    try:
        hotel_room_lowest_price = client.batch_room_lowest_room_price()
        cookie = client.cookie
        return hotel_room_lowest_price, cookie, hotel_id
    except Exception as e:
        logger.error(f"获取 凯悦 {hotel_id} 的最低房价失败, Error: {e}")

    return None, None, hotel_id


def kaiyue_task():
    all_hotel_room_lowest_price = {}

    hotel_list = settings.KY_HOTEL_LIST
    worker_num = len(hotel_list)
    with ThreadPoolExecutor(max_workers=worker_num) as executor:
        future_to_hotel = {executor.submit(fetch_lowest_price, hotel_id): hotel_id for hotel_id in hotel_list}

        for future in as_completed(future_to_hotel):
            price, cookie, hotel_id = future.result()
            if price:
                all_hotel_room_lowest_price[hotel_id] = price

    # 通过接口上传数据
    # tools.update_hotel_data(all_hotel_room_lowest_price, "凯悦")

    # 修改环境变量中的KAIYUE_COOKIE
    if cookie:
        tools.update_env_value("KAIYUE_COOKIE", cookie)

    return all_hotel_room_lowest_price, cookie


if __name__ == "__main__":
    kaiyue_task()