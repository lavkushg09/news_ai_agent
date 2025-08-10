from pydantic import BaseModel

class NewsRequest(BaseModel):
    country:str
    city:str
    summarize:bool=False
    news_category:str = "Technology"

