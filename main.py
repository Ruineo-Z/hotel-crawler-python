from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

from logger import get_logger
from tasks import wanhao_task

logger = get_logger("main")

# 线程池配置（允许并发执行）
executors = {
    'default': ThreadPoolExecutor(10),
}

scheduler = BlockingScheduler(executors=executors)

# 注册任务（每隔 10 分钟执行一次）
scheduler.add_job(wanhao_task.wanhao_task, 'cron', minute=0, id='wanhao_job')

# 启动调度器
if __name__ == '__main__':
    logger.info("启动定时任务调度器...")
    scheduler.start()
