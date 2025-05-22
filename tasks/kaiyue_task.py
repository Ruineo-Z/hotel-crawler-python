import os

from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

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


def kaiyue_temporary_task():
    """
    凯悦的临时任务
    """
    hotel_list = settings.KY_HOTEL_LIST
    logger.info(f"开始爬取凯悦的最低房价")

    for hotel_id in hotel_list:
        logger.info(f"Hotel ID: {hotel_id}")
        all_hotel_room_lowest_price = {}

        init_cookie = os.getenv("KAIYUE_COOKIE")
        client = KYCrawler(hotel_id=hotel_id, x_kpsdk_ct=init_cookie)
        data = client.batch_lowest_room_price_temporary()
        cookie = client.cookie
        if cookie:
            tools.update_env_value("KAIYUE_COOKIE", cookie)
        all_hotel_room_lowest_price[hotel_id] = data
        tools.update_hotel_data(all_hotel_room_lowest_price, "凯悦")


def kaiyue_temporary_task_with_timeout():
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(kaiyue_temporary_task)
            # 8.5小时 = 8*60*60 + 30*60 = 30600秒
            return future.result(timeout=30600)
    except TimeoutError:
        logger.error("凯悦定时任务执行超时（超过8.5小时）")
        raise TimeoutError("凯悦定时任务超时")


def update_kaiyue_cookie():
    """定时刷新凯悦Cookie"""
    logger.info("开始刷新凯悦的Cookie")
    cookie = os.getenv("KAIYUE_COOKIE", "")
    hotel_id = settings.KY_HOTEL_LIST[0]
    client = KYCrawler(hotel_id=hotel_id, x_kpsdk_ct=cookie)
    client.get_new_cookie()
    new_cookie = client.cookie
    logger.info(f"凯悦Cookie，刷新前: {cookie}, 刷新后: {new_cookie}")
    tools.update_env_value("KAIYUE_COOKIE", new_cookie)
    logger.info(f"更新凯悦Cookie成功")


if __name__ == "__main__":
    kaiyue_task()
