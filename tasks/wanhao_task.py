import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from crawler.wanhao_crawler import WHCrawler
from logger import get_logger
from config import settings
import tools

logger = get_logger("tasks")


def fetch_lowest_price(hotel):
    client = WHCrawler()
    client.get_hotel_cookie()
    try:
        hotel_rooms_lowest_price = client.batch_get_room_price(hotel_property_id=hotel)
        logger.success(f"完成 万豪集团 {hotel} 的最低房价")
        return hotel, hotel_rooms_lowest_price
    except Exception as e:
        logger.error(f"获取 万豪集团 {hotel} 的最低房价失败, Error: {e}")
        return hotel, None


def wanhao_task():
    all_hotel_rooms_lowest_price = {}

    # 并发获取万豪集团房价数据
    hotel_list = settings.WH_HOTEL_LIST
    worker_num = len(hotel_list)
    with ThreadPoolExecutor(max_workers=worker_num) as executor:
        future_to_hotel = {executor.submit(fetch_lowest_price, hotel): hotel for hotel in hotel_list}

        for future in as_completed(future_to_hotel):
            hotel, price = future.result()
            if price is not None:
                all_hotel_rooms_lowest_price[hotel] = price

    # 调用接口上传数据
    tools.update_hotel_data(all_hotel_rooms_lowest_price, "万豪")

    return all_hotel_rooms_lowest_price


if __name__ == '__main__':
    data = wanhao_task()
    print(data)
    with open("../test.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
