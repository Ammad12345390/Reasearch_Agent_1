import os
import time
import asyncio
from datetime import datetime, timezone
from typing import TypedDict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langgraph.graph import END, StateGraph
from tavily import TavilyClient
from groq import Groq
import psycopg

load_dotenv()

app = FastAPI(title="Research Summarizer Agent API")

POSTGRESQL_URL = os.getenv("POSTGRESQL_URL")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)


class TopicRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=200)
    user_id: str = Field(..., min_length=1, max_length=100)


class TopicResponse(BaseModel):
    summary: str
    execution_time: float


class AgentState(TypedDict):
    topic: str
    facts: str
    summary: str


async def researcher(state: AgentState):
    topic = state["topic"]

    search_response = await asyncio.to_thread(
        tavily_client.search,
        query=topic,
        max_results=5,
        search_depth="basic",
    )

    results = search_response.get("results", [])

    facts = "\n\n".join(
        [
            f"Title: {item.get('title')}\nURL: {item.get('url')}\nContent: {item.get('content')}"
            for item in results
        ]
    )

    return {"facts": facts}


async def summarizer(state: AgentState):
    prompt = f"""
You are a research summarizer agent.

Topic:
{state["topic"]}

Research facts:
{state["facts"]}

Write a clear, short, useful summary.
Also mention important points.
"""

    completion = await asyncio.to_thread(
        groq_client.chat.completions.create,
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful research assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    summary = completion.choices[0].message.content

    return {"summary": summary}


graph = StateGraph(AgentState)

graph.add_node("researcher", researcher)
graph.add_node("summarizer", summarizer)

graph.set_entry_point("researcher")
graph.add_edge("researcher", "summarizer")
graph.add_edge("summarizer", END)

workflow = graph.compile()


def save_log(user_id: str, topic: str, summary: str, execution_time: float):
    with psycopg.connect(POSTGRESQL_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO agent_logs
                (user_id, topic, summary, execution_time, timestamp)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    topic,
                    summary,
                    execution_time,
                    datetime.now(timezone.utc),
                ),
            )
        conn.commit()


@app.get("/")
async def root():
    return {
        "message": "FastAPI LangGraph PostgreSQL Tavily Groq Agent is running"
    }


@app.post("/generate-summary", response_model=TopicResponse)
async def generate_summary(request: TopicRequest):
    start_time = time.perf_counter()

    try:
        result = await workflow.ainvoke(
            {
                "topic": request.topic,
                "facts": "",
                "summary": "",
            }
        )

        execution_time = round(time.perf_counter() - start_time, 2)

        await asyncio.to_thread(
            save_log,
            request.user_id,
            request.topic,
            result["summary"],
            execution_time,
        )

        return {
            "summary": result["summary"],
            "execution_time": execution_time,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow failed: {str(error)}",
        )