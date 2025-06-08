from fastapi import APIRouter, BackgroundTasks

from app.crawler.kaiyue_crawler import KYCrawler
from app.logger import get_logger
from app import tools
from app.api.schema.ky_schema import KYRequest

logger = get_logger("run_manual_hyatt")
router = APIRouter()


def run_hyatt_price_crawler(hotel_id: str, cookie: str, user_agent: str, date_duration: int):
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


@router.post("/kyatt-price")
async def hyatt_api(request: KYRequest, background_tasks: BackgroundTasks):
    hotel_id = request.hotel_id
    cookie = request.cookie
    user_agent = request.user_agent
    date_duration = request.date_duration

    try:
        logger.info(
            f"开始手动运行凯悦爬虫，参数: Hotel ID: {hotel_id}, Cookie: {cookie}, User Agent: {user_agent}, Date: {date_duration}")
        background_tasks.add_task(run_hyatt_price_crawler, hotel_id, cookie, user_agent, date_duration)
        return {
            "status": "success",
            "error": "",
            "hotel_id": hotel_id,
        }
    except Exception as e:
        logger.error(f"手动执行凯悦爬虫失败: Error: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "hotel_id": hotel_id,
        }
