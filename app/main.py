import pytz
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from fastapi import APIRouter, FastAPI
import uvicorn
import asyncio
from concurrent.futures import ThreadPoolExecutor as ConcurrentThreadPoolExecutor

from app.logger import get_logger
from app.tasks import wanhao_task
from app.tasks import kaiyue_task
from app.api.endpoint.kyatt import router as kyatt_router

logger = get_logger("main")

# 全局调度器变量
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    global scheduler
    logger.info("启动定时任务调度器...")

    scheduler = AsyncIOScheduler(
        executors={'default': ThreadPoolExecutor(10)},
        timezone=pytz.timezone("Asia/Shanghai")
    )

    # 万豪爬虫 每小时的第 0 分钟和第 30 分钟各执行一次（即每半小时）
    scheduler.add_job(wanhao_task.wanhao_task, 'cron', minute="0, 30", id='wanhao_price_job')
    # 万豪爬虫 定时更新万豪的Cookie
    scheduler.add_job(wanhao_task.get_cookie, 'cron', hour='11,23', minute=59, id='wanhao_cookie_job',
                      timezone='Asia/Shanghai')

    # 凯悦爬虫 每天执行一次，执行爬虫任务
    scheduler.add_job(kaiyue_task.kaiyue_temporary_task_with_timeout, 'interval', hours=4, id='kaiyue_price_job',
                      timezone='Asia/Shanghai')

    # 启动调度器
    scheduler.start()

    # 在线程池中初始化万豪Cookie，避免在asyncio事件循环中使用同步playwright
    loop = asyncio.get_event_loop()
    with ConcurrentThreadPoolExecutor() as executor:
        await loop.run_in_executor(executor, wanhao_task.get_cookie)

    yield

    # 关闭时执行
    logger.info("关闭定时任务调度器...")
    if scheduler:
        scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

# 注册路由
app.include_router(kyatt_router, prefix="/api", tags=["kyatt"])

# 启动FastAPI服务
if __name__ == '__main__':
    logger.info("启动FastAPI服务器...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
