import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.crawler.wanhao_crawler import WHCrawler
from app.logger import get_logger
from app.config import settings
from app import tools

logger = get_logger("wanhao-tasks")


def get_cookie():
    """用于定时更新 万豪集团 Cookie 的方法，将Cookie保存再环境变量中"""
    client = WHCrawler()
    logger.info(f"开始获取用于 万豪 的Cookie")
    client.get_hotel_cookie()
    logger.info(f"用于 万豪 的Cookie获取完成")

    cookie = client.cookie

    os.environ["WANHAO_COOKIE"] = cookie


def fetch_lowest_price(hotel):
    """执行万豪单个酒店的最低房价获取任务"""
    client = WHCrawler()
    client.cookie = os.getenv("WANHAO_COOKIE", "")
    try:
        hotel_rooms_lowest_price = client.batch_get_room_price(hotel_property_id=hotel)
        logger.success(f"完成 万豪集团 {hotel} 的最低房价")
        return hotel, hotel_rooms_lowest_price
    except Exception as e:
        logger.error(f"获取 万豪集团 {hotel} 的最低房价失败, Error: {e}")
        return hotel, None


def wanhao_task():
    """并发获取万豪酒店的最低房价任务"""

    start_time = time.time()
    logger.info(f"开始执行 万豪 最低房价任务")
    all_hotel_rooms_lowest_price = {}

    # 并发获取万豪集团房价数据
    hotel_list = settings.WH_HOTEL_LIST
    worker_num = len(hotel_list)
    with ThreadPoolExecutor(max_workers=worker_num) as executor:
        future_to_hotel = {executor.submit(fetch_lowest_price, hotel): hotel for hotel in hotel_list}

        try:
            for future in as_completed(future_to_hotel, timeout=25 * 60):
                hotel, price = future.result()
                if price is not None:
                    all_hotel_rooms_lowest_price[hotel] = price
        except TimeoutError as e:
            logger.error(f"万豪任务执行超过25分钟，强制终止, Error: {e}")
        except Exception as e:
            logger.error(f"万豪任务执行异常, Error: {e}")

    # 调用接口上传数据
    tools.update_hotel_data(all_hotel_rooms_lowest_price, "万豪")

    logger.info(f"结束执行 万豪 最低房价任务, 耗时: {time.time() - start_time} 秒")
    return all_hotel_rooms_lowest_price



if __name__ == '__main__':
    # Get Cookie
    get_cookie()
    # Run Task
    data = wanhao_task()
    logger.debug(data)
