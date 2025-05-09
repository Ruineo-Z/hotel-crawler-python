import requests

from config import settings
from logger import get_logger

logger = get_logger("tool")


def update_hotel_data(hotel_data, hotel_name):
    url = settings.DATABASE_URL

    retry_num = 0
    while retry_num < 3:
        try:
            response = requests.post(url, json=hotel_data)
            response.raise_for_status()
            logger.success(f"上传 {hotel_name} 数据成功, Response code: {response.status_code}")
            break
        except Exception as e:
            logger.warning(f"上传 {hotel_name} 数据失败, 开始第 {retry_num + 1} 次重试, Error: {e}")
            retry_num += 1
    if retry_num == 3:
        logger.error(f"三次上传 {hotel_name} 数据均失败")
