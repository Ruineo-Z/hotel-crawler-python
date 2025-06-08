from pydantic import BaseModel


class KYRequest(BaseModel):
    hotel_id: str
    cookie: str
    user_agent: str
    date_duration: int