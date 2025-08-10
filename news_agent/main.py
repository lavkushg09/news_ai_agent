from fastapi import FastAPI, Query
from .request_para import NewsRequest
from .news_service import fetch_top_news
from .ai_service import run_news_agent

app = FastAPI(title="Ai agent to get current news")


@app.get("/v1/get_service_info")
def get_basic_service_info():
    return {
        "success": True,
        "status": 200,
        "data": {}
    }


@app.post("/v1/get_news")
def get_top_current_news(req: NewsRequest):
    country = req.country
    news_category = req.news_category
    # return fetch_top_news(country, news_category)
    return run_news_agent(country, news_category)


