import json
import os
import time
import logging
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from openai import OpenAI
from .news_service import fetch_top_news  
logging.basicConfig(
    filename="news_agent.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

load_dotenv()

client = OpenAI(api_key=os.getenv('OPEN_AI_AGENT_KEY'))


# ---------- Pydantic Model ----------
class NewsSummary(BaseModel):
    title: str = Field(description="Title of the news article")
    title_in_hindi:str = Field(description="Title of the news article")
    summary_in_english: str = Field(description="A concise 50-word summary of the article in english")
    summary_in_hindi: str = Field(description="A concise 50-word summary of the article in hindi")
    url: str = Field(description="URL to the full news article")

class NewsSummariesResponse(BaseModel):
    summaries: List[NewsSummary]


# ---------- Tool function ----------
def get_top_news_with_summaries(country: str, category: str, limit: int = 5):
    """Fetch latest news and summarize each into 50 words."""
    news_data = fetch_top_news(country, category, limit)
    if not news_data or "data" not in news_data:
        return []

    summaries = []
    for article in news_data["data"]:
        title = article.get("title", "")
        url = article.get("url", "")
        description = article.get("description", "")

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful news summarizer."},
                {"role": "user", "content": f"Summarize this news in exactly 50 words in english and 100 words in hindi language:\n\nTitle: {title}\nDescription: {description} \nlink: {url}"}
            ],
            temperature=0.3
        )
        summary_text = completion.choices[0].message.content.strip()

        summaries.append({
            "title": title,
            "summary": summary_text,
            "url": url
        })
        # print(summaries)
        time.sleep(20)

    return summaries


# ---------- Main execution wrapper ----------
def run_news_agent(country="us", category="business", limit=5):
    system_prompt = "You are a helpful assistant that provides latest news summaries."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Get top {limit} {category} news from {country.upper()} and summarize them in 50 words each."}
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_top_news_with_summaries",
                "description": "Fetch latest news for given country & category and summarize each into 50 to 100 words.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "country": {"type": "string"},
                        "category": {"type": "string"}
                    },
                    "required": ["country", "category"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )
    time.sleep(20)
    for tool_call in completion.choices[0].message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        messages.append(completion.choices[0].message)
        result = get_top_news_with_summaries(**args)
        time.sleep(20)
        print(result)
        messages.append(
            {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)}
        )
        print(messages)
    time.sleep(20)
    completion_2 = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        response_format=NewsSummariesResponse
    )
    reply = completion_2.choices[0].message.parsed
    return reply
