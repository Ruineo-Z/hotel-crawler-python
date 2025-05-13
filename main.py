import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from logger import get_logger
from tasks import wanhao_task

logger = get_logger("main")

scheduler = BlockingScheduler(
    executors={'default': ThreadPoolExecutor(10)},
    timezone=pytz.timezone("Asia/Shanghai")
)

# 每小时的第 0 分钟和第 30 分钟各执行一次（即每半小时）
scheduler.add_job(wanhao_task.wanhao_task, 'cron', minute='0,30', id='wanhao_price_job')
scheduler.add_job(wanhao_task.get_cookie, 'cron', hour=23, minute=59, id='wanhao_cookie_job', timezone='Asia/Shanghai')

# 启动调度器
if __name__ == '__main__':
    logger.info("启动定时任务调度器...")
    scheduler.start()
