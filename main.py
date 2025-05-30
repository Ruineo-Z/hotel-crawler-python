import os
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.interval import IntervalTrigger

from logger import get_logger
from tasks import wanhao_task
from tasks import kaiyue_task

logger = get_logger("main")

scheduler = BlockingScheduler(
    executors={'default': ThreadPoolExecutor(10)},
    timezone=pytz.timezone("Asia/Shanghai")
)

# 万豪爬虫 每小时的第 0 分钟和第 30 分钟各执行一次（即每半小时）
scheduler.add_job(wanhao_task.wanhao_task, 'cron', minute="0, 30", id='wanhao_price_job')
# 万豪爬虫 定时更新万豪的Cookie
scheduler.add_job(wanhao_task.get_cookie, 'cron', hour='11,23', minute=59, id='wanhao_cookie_job', timezone='Asia/Shanghai')

# 凯悦爬虫 每天执行一次，执行爬虫任务
scheduler.add_job(kaiyue_task.kaiyue_temporary_task_with_timeout, 'cron', hour=2, minute=00, id='kaiyue_price_job',
                  timezone='Asia/Shanghai')
# 凯悦爬虫 定时更新凯悦的Cookie，每50分钟执行一次（凯悦Cookie存活时间为1h）
scheduler.add_job(kaiyue_task.update_kaiyue_cookie, trigger=IntervalTrigger(minutes=50))

# 启动调度器
if __name__ == '__main__':
    wanhao_task.get_cookie()
    logger.info("启动定时任务调度器...")
    scheduler.start()
