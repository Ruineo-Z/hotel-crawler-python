import playwright.sync_api
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import requests

from logger import get_logger

logger = get_logger("crawler")


class HotelCrawler:
    def __init__(self):
        self.room_list_xpath = '//*[@id="main-content"]/div/div[6]/div/div[3]/section'
        self.room_block_class = "room-rate-wrapper"
        self.room_name_class = "standard room-name mb-3 mb-md-0"
        self.room_price_class = "room-rate mr-2"
        self.database_url = "https://eoo14fnitgkpcxu.m.pipedream.net"

    def crawler(self, hotel_url: str, page: playwright.sync_api.Page):
        """爬取单个酒店网站的html"""
        logger.info(f"打开新的标签页")
        with page.expect_popup() as new_page_info:
            logger.info(f"导航至: {hotel_url}")
            page.goto(hotel_url, timeout=60 * 1000)
            logger.info(f"等待`查看房价`按钮加载...")
            check_price_button = page.wait_for_selector('button:has-text("查看房价")', timeout=60 * 1000)
            logger.info(f"点击`查看房价`按钮")
            check_price_button.click()

        new_page = new_page_info.value
        logger.info(f"等待房价页面加载")
        new_page.wait_for_selector(self.room_list_xpath, timeout=60 * 1000)
        logger.info(f"向下滚动页面，保证全部加载，每次滚动间隔500ms")
        for i in range(5):
            new_page.keyboard.press("PageDown")
            new_page.wait_for_timeout(0.5 * 1000)
        logger.info(f"获取房价页面的html")
        page_html = new_page.content()

        page.close()
        return page_html

    def extract_prices_from_html(self, page_html):
        """解析网站html获取房价"""
        soup = BeautifulSoup(page_html, "html.parser")
        room_blocks = soup.find_all("div", class_=self.room_block_class)
        room_prices = []
        for room in room_blocks:
            room_name = room.find("h3", class_=self.room_name_class).text.strip()
            room_price_blocks = room.find_all("span", class_=self.room_price_class)
            room_lowest_price = 0
            for room_price_block in room_price_blocks:
                room_price_string = room_price_block.text.strip()
                room_price = self.parse_price_to_float(room_price_string)
                room_lowest_price = room_price if room_price <= room_lowest_price or not room_lowest_price else room_lowest_price
            room_prices.append(
                {
                    "room_name": room_name,
                    "room_lowest_price": room_lowest_price
                }
            )
        return room_prices

    def batch_crawl(self, hotel_url_list):
        """任务入口"""
        logger.info(f"开始爬取酒店房价，共需爬取{len(hotel_url_list)}个酒店")
        success_num = 0
        with sync_playwright() as p:
            logger.info(f"初始化浏览器")
            browser = p.chromium.launch(headless=True)
            for url in hotel_url_list:
                page = browser.new_page()
                try:
                    page_html = self.crawler(url, page)
                except Exception as e:
                    logger.error(f"获取{url}网站Html失败, Error: {e}")
                    continue
                try:
                    room_prices = self.extract_prices_from_html(page_html)
                except Exception as e:
                    logger.error(f"获取{url}房价失败, Error: {e}")
                    continue

                update_result = self.update_database_price(room_prices, url)
                if update_result:
                    success_num += 1
        logger.success(f"完成酒店房价爬取任务，成功数：{success_num}，失败数：{len(hotel_url_list) - success_num}")

    def update_database_price(self, hotel_room_price_list, hotel_url):
        """上传爬取结果至数据库"""
        retry_num = 0
        while retry_num < 3:
            try:
                payload = {
                    "hotel": hotel_url,
                    "room_price": hotel_room_price_list
                }
                r = requests.post(url=self.database_url, json=payload)
                r.raise_for_status()
                return True
            except Exception as e:
                logger.warning(f"上传房价至数据库失败, Error: {e}")
                logger.warning(f"开始第{retry_num + 1}次重试上传")
                retry_num += 1
            if retry_num == 3:
                logger.error(f"上传房价至数据库3次均失败")
                break
        return False

    @staticmethod
    def parse_price_to_float(price_str: str):
        """将酒店房价从字符串转为浮点数"""
        return float(price_str.replace(",", ""))
