import random
import time

import requests

import tools
from config import settings
from logger import get_logger

logger = get_logger("kaiyue-crawler")


class KYCrawler:
    def __init__(self, hotel_id: str, x_kpsdk_ct: str):
        self.hotel_base_url = "https://www.hyatt.com/zh-CN/shop/service/rooms/roomrates"
        self.hotel_id = hotel_id
        self.cookie = f"tkrm_alpekz_s1.3={x_kpsdk_ct}"
        self.set_cookie = ""

    def get_new_cookie(self):
        """单独调一次接口，获取凯悦的Cookie"""
        date_duration = tools.get_date_list()
        date = date_duration[0]
        self.refresh_cookie(date)

    def refresh_cookie(self, response_headers):
        x_kpsdk_ct = response_headers.get("X-Kpsdk-Ct")
        set_cookie = response_headers.get("Set-Cookie")
        self.set_cookie = set_cookie
        cookie = f"tkrm_alpekz_s1.3={x_kpsdk_ct}; "
        self.cookie = cookie

    def get_room_info(self, date):
        url = f"{self.hotel_base_url}/{self.hotel_id}"
        start_date = date["start_date"]
        end_date = date["end_date"]
        params = {
            "spiritCode": self.hotel_id,
            "rooms": 1,
            "adults": 1,
            "checkinDate": start_date,
            "checkoutDate": end_date,
            "kids": 0,
            "rate": "Standard",
            "suiteUpgrade": True
        }

        headers = {
            "Cookie": self.cookie,
            "User-Agent": random.choice(settings.USER_AGENTS),
            "Priority": "u=1, i",
            "Accept-language": "zh-CN,zh;q=0.9",
        }
        retry_num = 0
        while retry_num < 3:
            try:
                r = requests.get(url, params=params, headers=headers)
                logger.info(f"调用凯悦 {self.hotel_id} 房间信息接口结果: {r.status_code}")
                r.raise_for_status()
                room_info = r.json()["roomRates"]
                self.refresh_cookie(r.headers)
                return room_info
            except Exception as e:
                logger.warning(
                    f"获取 {self.hotel_id} {date} 的房间信息失败, 延时 5s, 开始第 {retry_num + 1}次重试 Error: {e}")
                time.sleep(5)
                retry_num += 1
        return None

    def get_lowest_room_price(self, all_room_info, date):
        all_room_lowest_price = {}
        for room_id, room_info in all_room_info.items():
            room_lowest_price = 0
            room_name = room_info["roomType"]["title"]
            room_plans = room_info["ratePlans"]

            for room_plan in room_plans:
                room_rate = room_plan["rate"]
                room_lowest_price = room_rate if room_rate <= room_lowest_price or room_lowest_price == 0 else room_lowest_price
            all_room_lowest_price[room_name] = room_lowest_price
        logger.info(f"凯悦 {self.hotel_id} {date} 最低房价获取成功")
        return all_room_lowest_price

    def batch_room_lowest_room_price(self):
        date_duration = tools.get_date_list()
        all_room_lowest_price = []
        for date in date_duration:
            room_info = self.get_room_info(date)
            room_lowest_price = self.get_lowest_room_price(room_info, date)
            all_room_lowest_price.append(
                {
                    "date": date,
                    "lowest_price": room_lowest_price,
                }
            )

        return all_room_lowest_price

    def batch_lowest_room_price_temporary(self):
        """凯悦酒店不并发的临时方案，每次接口调用完后暂停1分钟"""
        date_duration = tools.get_date_list()
        all_room_lowest_price = []
        for date in date_duration:
            room_info = self.get_room_info(date)
            room_lowest_price = self.get_lowest_room_price(room_info, date)
            all_room_lowest_price.append(
                {
                    "date": date,
                    "lowest_price": room_lowest_price,
                }
            )
            time.sleep(60)
        return all_room_lowest_price
