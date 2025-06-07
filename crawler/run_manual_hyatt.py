import argparse

from crawler.kaiyue_crawler import KYCrawler
from logger import get_logger
import tools

logger = get_logger("run_manual_hyatt")


def run_manual_hyatt(hotel_id: str, cookie: str, user_agent: str, date_duration: int):
    hyatt_client = KYCrawler(hotel_id=hotel_id, cookie=cookie, user_agent=user_agent)
    try:
        hotel_lowest_price = hyatt_client.batch_room_lowest_room_price(date_duration=date_duration)
    except Exception as e:
        error_msg = f"获取{hotel_id}的房价失败, ERROR: {e}"
        raise Exception(error_msg)

    try:
        tools.update_hotel_data({hotel_id: hotel_lowest_price}, "凯悦")
    except Exception as e:
        error_msg = f"上传凯悦数据失败, Data: {hotel_lowest_price}, ERROR: {e}"
        raise Exception(error_msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="手动运行凯悦爬虫脚本，接受 Hotel ID: str, Cookie: str, User Agent: str, Date Duration: int")
    parser.add_argument("hotel_id", type=str, help="Hotel ID")
    parser.add_argument("cookie", type=str, help="Cookie")
    parser.add_argument("user_agent", type=str, help="User Agent")
    parser.add_argument("date_duration", type=int, help="Date Duration")
    args = parser.parse_args()
    try:
        logger.info(
            f"开始手动运行凯悦爬虫，参数: Hotel ID: {args.hotel_id}, Cookie: {args.cookie}, User Agent: {args.user_agent}, Date: {args.date_duration}")
        run_manual_hyatt(hotel_id=args.hotel_id, cookie=args.cookie, user_agent=args.user_agent,
                         date_duration=args.date_duration)
    except Exception as e:
        logger.error(f"手动执行凯悦爬虫失败: Error: {e}")
