from pydantic import BaseModel


class KYRequest(BaseModel):
    hotel_id: str  # 需要爬取的酒店id，参考酒店映射
    cookie: str  # 通过浏览器获取到的cookie
    user_agent: str  # 获取cookie使用的浏览器对应的User-Agent，可以在接口请求头中获取
    date_duration: int  # 需要获取未来房价的天数
