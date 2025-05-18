import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    load_dotenv()
    # 数据库接口地址
    DATABASE_URL: str = "http://craneman.cn/api/hotel/data/loadPrice"

    # User-Agent 配置
    USER_AGENTS: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
    ]

    # 环境变量文件路径
    ENV_FILE_PATH: Path = Path(__file__).resolve().parent / ".env"

    # 万豪集团爬虫参数
    WH_HOTEL_LIST: List[str] = [
        "CTUMJ",  # 成都茂业JW万豪
        "CTUMC",  # 成都首座万豪
        "CTUXR",  # 成都瑞吉酒店
        "CTURZ",  # 成都富丽思卡尔顿酒店
        "CTUWH",  # 成都W酒店
        "CTUUC",  # 成都春熙路福朋喜来登酒店
        "CTULS",  # 成都天府丽都喜来登饭店
        "CTUBR",  # 成都首座万丽酒店
        "CTUPH",  # 成都高新会展中心福朋喜来登酒店
    ]
    GRAPHQL_FORCE_SAFELISTING: str = "true"
    GRAPHQL_OPERATION_SIGNATURE: str = "a1079a703a2d21d82c0c65e4337271c3029c69028c6189830f30882170075756"
    GRAPHQL_OPERATION_NAME: str = "PhoenixBookSearchProductsByProperty"
    GRAPHQL_REQUIRE_SAFELISTING: str = "true"

    # 凯悦酒店数据爬虫参数
    KY_HOTEL_LIST: List[str] = [
        "ctugh",  # 成都群光君悦酒店
        "ctuub",  # 琅珀·凯悦 成都琅珀酒店
        "ctuzc",  # 成都象南里凯悦嘉轩酒店
        "ctuxc",  # 成都象南里凯悦嘉寓酒店
    ]
    KAIYUE_COOKIE: str = os.getenv("KAIYUE_COOKIE", "")


settings = Settings()
