import os
import time
import webbrowser
import subprocess
import shutil

import sqlite3
import psutil
import requests
import browser_cookie3

import tools
from config import settings
from logger import get_logger

logger = get_logger("kaiyue-crawler")


class KYCrawler:
    def __init__(self, hotel_id: str):
        self.hotel_base_url = "https://www.hyatt.com/zh-CN/shop/service/rooms/roomrates"
        self.hotel_id = hotel_id
        self.cookie = ""

    def get_cookie(self):
        """
        通过webbrowser获取cookie
        1. 获取cookie
        2. 关闭系统中chrome的进程
        3. 删除chrome中凯悦的cookie
        """

        def close_chrome():
            """关闭Chrome浏览器进程"""
            try:
                # 检测是否在Docker环境中运行
                in_docker = os.path.exists("/.dockerenv")

                if in_docker:
                    # Docker环境中使用更通用的方法关闭Chrome
                    try:
                        subprocess.run(["killall", "chrome"], check=False)
                    except:
                        pass
                else:
                    # macOS系统
                    subprocess.run(["pkill", "-f", "Google Chrome"], check=False)

                # 使用psutil更精确地控制
                for proc in psutil.process_iter(["pid", "name"]):
                    if "chrome" in proc.info["name"].lower():
                        try:
                            proc.kill()
                        except:
                            pass

                logger.info("Chrome浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭Chrome失败: {e}")

        def delete_hyatt_cookies():
            """删除Chrome中Hyatt网站的所有cookie"""
            try:
                # 检测是否在Docker环境中运行
                in_docker = os.path.exists("/.dockerenv")

                # 根据环境选择不同的Chrome cookie路径
                if in_docker:
                    # Docker环境中，跳过文件操作，仅使用browser_cookie3获取cookie
                    logger.info("在Docker环境中运行，跳过本地Cookie文件操作")
                    return
                else:
                    # 本地macOS环境
                    db_path = os.path.join(
                        os.path.expanduser("~"),
                        "Library/Application Support/Google/Chrome/Default/Cookies",
                    )

                    # 检查文件是否存在
                    if not os.path.exists(db_path):
                        logger.warning(f"Cookie文件不存在: {db_path}")
                        return

                    # 复制数据库文件（避免锁定问题）
                    temp_db = "temp_cookies.db"
                    shutil.copyfile(db_path, temp_db)

                    # 连接数据库
                    conn = sqlite3.connect(temp_db)
                    cursor = conn.cursor()

                    # 删除Hyatt相关的cookie
                    cursor.execute(
                        "DELETE FROM cookies WHERE host_key LIKE '%hyatt.com%'"
                    )

                    conn.commit()
                    conn.close()

                    # 将修改后的数据库复制回原位置
                    shutil.copyfile(temp_db, db_path)
                    os.remove(temp_db)

                    logger.info("Hyatt网站cookie已删除")
            except Exception as e:
                logger.error(f"删除cookie失败: {e}")

        def get_hyatt_cookie_via_browser():
            """通过webbrowser打开Chrome并获取cookie"""
            try:
                # 检测是否在Docker环境中运行
                in_docker = os.path.exists('/.dockerenv')
                
                # 使用webbrowser打开Chrome访问Hyatt网站
                url = 'https://www.hyatt.com/zh-CN/home'
                
                # if in_docker:
                #     # 在Docker环境中，使用环境变量方式直接返回cookie
                #     # 如果环境变量中有cookie，直接使用
                #     env_cookie = os.environ.get('KAIYUE_COOKIE')
                #     if env_cookie:
                #         logger.info("从环境变量获取cookie")
                #         return env_cookie
                    
                #     logger.info("Docker环境中无法打开浏览器，尝试使用requests直接获取")
                #     try:
                #         # 使用requests直接访问网站获取cookie
                #         headers = {
                #             'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
                #             'accept': '*/*',
                #             'accept-language': 'zh-CN,zh;q=0.9',
                #         }
                #         session = requests.Session()
                #         response = session.get(url, headers=headers)
                        
                #         # 检查是否获取到特定cookie
                #         for cookie in session.cookies:
                #             if cookie.name == 'tkrm_alpekz_s1.3':
                #                 return cookie.value
                        
                #         logger.warning("未能通过requests获取到所需cookie")
                #     except Exception as e:
                #         logger.warning(f"通过requests获取cookie失败: {e}")
                # else:
                #     # 本地环境使用webbrowser
                #     webbrowser.open(url)
                webbrowser.open(url)
                time.sleep(5)
                
                # 从Chrome中读取cookie
                try:
                    cj = browser_cookie3.chrome(domain_name='hyatt.com')
                    for cookie in cj:
                        if cookie.name == 'tkrm_alpekz_s1.3':
                            return cookie.value
                except Exception as e:
                    logger.info(f"获取cookie失败: {e}")
                
                return None
            except Exception as e:
                logger.error(f"获取cookie过程中出错: {e}")
                return None

        retry_num = 0
        while retry_num < 3:
            cookie = get_hyatt_cookie_via_browser()
            close_chrome()
            delete_hyatt_cookies()
            if not cookie:
                retry_num += 1
            self.cookie = cookie
            break
        if retry_num == 3:
            logger.error(f"3次获取凯悦的cookie均失败")
        logger.info(f"获取凯悦的cookie, Cookie: {self.cookie}")

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
            "suiteUpgrade": True,
        }

        headers = {
            "Cookie": self.cookie,
            # user agent必须使用与chrome一致的版本(cookie的加密应该是使用了user agent)
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }
        retry_num = 0
        while retry_num < 3:
            try:
                r = requests.get(url, params=params, headers=headers)
                logger.info(
                    f"调用凯悦 {self.hotel_id} 房间信息接口结果: {r.status_code}"
                )
                r.raise_for_status()
                if not r.text:
                    retry_num += 1
                    logger.info(
                        f"查询 {self.hotel_id} - {date} 的房价无响应,重新获取cookie"
                    )
                    self.get_cookie()
                    continue

                room_info = r.json()["roomRates"]
                return room_info
            except Exception as e:
                logger.warning(
                    f"获取 {self.hotel_id} {date} 的房间信息失败, 延时 5s, 开始第 {retry_num + 1}次重试 Error: {e}"
                )
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
                room_lowest_price = (
                    room_rate
                    if room_rate <= room_lowest_price or room_lowest_price == 0
                    else room_lowest_price
                )
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


if __name__ == "__main__":
    client = KYCrawler("")
    client.get_cookie()
