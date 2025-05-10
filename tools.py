from datetime import datetime, timedelta

import requests
import pytz

from config import settings
from logger import get_logger

logger = get_logger("tool")


def update_hotel_data(hotel_data_dict, hotel_type):
    url = settings.DATABASE_URL

    retry_num = 0
    for hotel_name, hotel_data in hotel_data_dict.items():
        while retry_num < 3:
            try:
                payload = {
                    "reqData": {hotel_name: hotel_data},
                }
                response = requests.post(url, json=payload)
                response.raise_for_status()
                logger.success(f"上传{hotel_type} {hotel_name} 数据成功, Response code: {response.status_code}, Text: {response.text}")
                break
            except Exception as e:
                logger.warning(f"上传{hotel_type} {hotel_name} 数据失败, 开始第 {retry_num + 1} 次重试, Error: {e}")
                retry_num += 1
        if retry_num == 3:
            logger.error(f"三次上传{hotel_type} {hotel_name} 数据均失败")


def get_date_list(date_duration: int = 60):
        """获取日期"""
        date_list = []
        timezone = pytz.timezone("Asia/Shanghai")
        now = datetime.now(tz=timezone)
        for i in range(date_duration):
            start_date = (now + timedelta(days=i)).strftime("%Y-%m-%d")
            end_date = (now + timedelta(days=i + 1)).strftime("%Y-%m-%d")
            date_list.append(
                {
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
        return date_list