import random
import time
from datetime import datetime, timedelta
from typing import List

from playwright.sync_api import sync_playwright
import requests
import pytz

from logger import get_logger
from config import settings

logger = get_logger("wanhao-crawler")


class WHCrawler:
    def __init__(self, date_duration: int = 60):
        self.room_list_xpath = '//*[@id="main-content"]/div/div[6]/div/div[3]/section'
        self.database_url = "https://eoo14fnitgkpcxu.m.pipedream.net"
        self.date_duration = date_duration

        self.cookie_url = "https://www.marriott.com.cn/search/default.mi"
        self.price_url = "https://www.marriott.com.cn/mi/query/PhoenixBookSearchProductsByProperty"
        self.cookie = ""
        self.rate_request_types_list = [
            [
                {
                    "value": "",
                    "type": "STANDARD"
                },
                {
                    "value": "",
                    "type": "PREPAY"
                },
                {
                    "value": "",
                    "type": "PACKAGES"
                },
                {
                    "value": "MRM",
                    "type": "CLUSTER"
                },
                {
                    "value": "",
                    "type": "REGULAR"
                }
            ],
            [{"value": "", "type": "MEMBER"}]
        ]

    def get_hotel_cookie(self):
        """打开万豪指定酒店网站，获取对应cookie"""
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[f'--user-agent={random.choice(settings.USER_AGENTS)}']
            )
            context = browser.new_context()
            page = context.new_page()
            page.goto(self.cookie_url, timeout=60 * 1000)

            # 🔑 获取当前页面 cookie
            cookies = context.cookies()
            self.cookie = "; ".join([f"{c['name']}={c['value']}" for c in cookies])

            browser.close()

        logger.info(f"Cookie: {self.cookie}")

    def batch_get_room_price(self, hotel_property_id: str = "CTUBR"):
        """搜索指定酒店的房价"""
        date_list = self.get_date_list()
        all_date_lowest_room_price = []

        base_body = {
            "operationName": "PhoenixBookSearchProductsByProperty",
            "variables": {
                "search": {
                    "options": {
                        # "startDate": "2025-05-08",
                        # "endDate": "2025-05-09",
                        "quantity": 1,
                        "numberInParty": 1,
                        "childAges": [],
                        "productRoomType": [
                            "ALL"
                        ],
                        "productStatusType": [
                            "AVAILABLE"
                        ],
                        # "rateRequestTypes": [
                        #     {
                        #         "value": "",
                        #         "type": "STANDARD"
                        #     },
                        #     {
                        #         "value": "",
                        #         "type": "PREPAY"
                        #     },
                        #     {
                        #         "value": "",
                        #         "type": "PACKAGES"
                        #     },
                        #     {
                        #         "value": "MRM",
                        #         "type": "CLUSTER"
                        #     },
                        #     {
                        #         "value": "",
                        #         "type": "REGULAR"
                        #     }
                        # ],
                        "isErsProperty": True
                    },
                    "propertyId": hotel_property_id
                },
                "offset": 0,
                "limit": None
            },
            "query": "query PhoenixBookSearchProductsByProperty($search: ProductByPropertySearchInput, $offset: Int, $limit: Int) {\n  searchProductsByProperty(search: $search, offset: $offset, limit: $limit) {\n    edges {\n      node {\n        ... on HotelRoom {\n          availabilityAttributes {\n            rateCategory {\n              type {\n                code\n                __typename\n              }\n              value\n              __typename\n            }\n            isNearSellout\n            __typename\n          }\n          rates {\n            name\n            description\n            rateAmounts {\n              amount {\n                origin {\n                  amount\n                  currency\n                  valueDecimalPoint\n                  __typename\n                }\n                __typename\n              }\n              points\n              pointsSaved\n              pointsToPurchase\n              __typename\n            }\n            localizedDescription {\n              translatedText\n              sourceText\n              __typename\n            }\n            localizedName {\n              translatedText\n              sourceText\n              __typename\n            }\n            rateAmountsByMode {\n              averageNightlyRatePerUnit {\n                amount {\n                  origin {\n                    amount\n                    currency\n                    valueDecimalPoint\n                    __typename\n                  }\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          basicInformation {\n            type\n            name\n            localizedName {\n              translatedText\n              __typename\n            }\n            description\n            localizedDescription {\n              translatedText\n              __typename\n            }\n            membersOnly\n            oldRates\n            representativeRoom\n            housingProtected\n            actualRoomsAvailable\n            depositRequired\n            roomsAvailable\n            roomsRequested\n            ratePlan {\n              ratePlanType\n              ratePlanCode\n              __typename\n            }\n            freeCancellationUntil\n            __typename\n          }\n          roomAttributes {\n            attributes {\n              id\n              description\n              groupID\n              category {\n                code\n                description\n                __typename\n              }\n              accommodationCategory {\n                code\n                description\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          totalPricing {\n            quantity\n            rateAmountsByMode {\n              grandTotal {\n                amount {\n                  origin {\n                    value: amount\n                    valueDecimalPoint\n                    __typename\n                  }\n                  __typename\n                }\n                __typename\n              }\n              subtotalPerQuantity {\n                amount {\n                  origin {\n                    currency\n                    value: amount\n                    valueDecimalPoint\n                    __typename\n                  }\n                  __typename\n                }\n                __typename\n              }\n              totalMandatoryFeesPerQuantity {\n                amount {\n                  origin {\n                    currency\n                    value: amount\n                    valueDecimalPoint\n                    __typename\n                  }\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          id\n          __typename\n        }\n        id\n        __typename\n      }\n      __typename\n    }\n    total\n    status {\n      ... on UserInputError {\n        httpStatus\n        messages {\n          user {\n            message\n            field\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      ... on DateRangeTooLongError {\n        httpStatus\n        messages {\n          user {\n            message\n            field\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
        }

        for date in date_list:
            # 遍历未来60天，获取每天每个房型的最低价格
            # 设置请求体的基础配置
            start_date = date["start_date"]
            end_date = date["end_date"]
            base_body["variables"]["search"]["options"]["startDate"] = start_date
            base_body["variables"]["search"]["options"]["endDate"] = end_date

            room_data_list = []
            for rate_request_types in self.rate_request_types_list:
                headers = {
                    "cookie": self.cookie,
                    "graphql-force-safelisting": settings.GRAPHQL_FORCE_SAFELISTING,
                    "graphql-operation-name": settings.GRAPHQL_OPERATION_NAME,
                    "graphql-operation-signature": settings.GRAPHQL_OPERATION_SIGNATURE,
                    "graphql-require-safelisting": settings.GRAPHQL_REQUIRE_SAFELISTING,
                    "User-Agent": random.choice(settings.USER_AGENTS),
                    "Accept-language": "zh-CN",
                    "Accept-encoding": "gzip, deflate, br, zstd"
                }

                base_body["variables"]["search"]["options"]["rateRequestTypes"] = rate_request_types

                room_data_list.extend(self.get_room_price(base_body, headers, date, hotel_property_id))

            lowest_price = self.get_lowest_room_price(room_data_list)
            all_date_lowest_room_price.append(
                {
                    "date": date,
                    "lowest_price": lowest_price
                }
            )
            logger.debug(f"万豪集团 {hotel_property_id} {date} 最低房价获取成功")

        return all_date_lowest_room_price

    def get_date_list(self):
        """获取日期"""
        date_list = []
        timezone = pytz.timezone("Asia/Shanghai")
        now = datetime.now(tz=timezone)
        for i in range(self.date_duration):
            start_date = (now + timedelta(days=i)).strftime("%Y-%m-%d")
            end_date = (now + timedelta(days=i + 1)).strftime("%Y-%m-%d")
            date_list.append(
                {
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
        return date_list

    def get_room_price(self, request_body, request_headers, date, hotel_id):
        retry_num = 0
        while retry_num < 3:
            try:
                r = requests.post(self.price_url, headers=request_headers, json=request_body)
                r.raise_for_status()
                logger.debug(f"调用 {hotel_id} 酒店房价接口结果: {r.status_code}")
                room_data_list = r.json()["data"]["searchProductsByProperty"]["edges"]
                return room_data_list
            except Exception as e:
                logger.warning(f"调用 {hotel_id} 房价接口失败，随机延时(1~5s)，开始第{retry_num + 1}次重试, Warning: {e}")
                delay_time = random.choice(range(1, 6))
                time.sleep(delay_time)
                retry_num += 1
        if retry_num == 3:
            logger.error(f"重试3次，获取 {hotel_id} {date}房价失败")
            return []

    @staticmethod
    def get_lowest_room_price(room_data_list: List[dict]):
        """解析房价接口响应内容"""
        room_price_dict = {}
        for room_data in room_data_list:
            # 获取房间全名
            room_name = room_data["node"]["basicInformation"]["name"]
            room_description = room_data["node"]["basicInformation"]["description"]
            room_full_name = room_name if not room_description else f"{room_name}, {room_description}"
            room_price_dict.setdefault(room_full_name, {})

            # 获取房间每单位夜间平均价格
            room_price_info = room_data["node"]["rates"]["rateAmountsByMode"]["averageNightlyRatePerUnit"]["amount"][
                "origin"]
            room_price_currency = room_price_info["currency"]
            room_price_value = room_price_info["amount"]
            room_price_decimal_point = room_price_info["valueDecimalPoint"]
            room_price = room_price_value / 10 ** room_price_decimal_point

            # 筛选出房价的最低价
            existing_room_price = room_price_dict[room_full_name].get("price", 0.0)
            room_price_dict[room_full_name]["price"] = existing_room_price \
                if existing_room_price <= room_price and existing_room_price != 0.0 else room_price

        return room_price_dict
