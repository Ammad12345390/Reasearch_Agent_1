import asyncio
import time
from typing import TypedDict

from fastapi import FastAPI, HTTPException
from langgraph.graph import END, StateGraph

from app.schemas import TopicRequest, TopicResponse


app = FastAPI(title="Research Agent API")


class AgentState(TypedDict):
    topic: str
    facts: str
    summary: str

async def researcher(state: AgentState):
    await asyncio.sleep(1)

    topic = state["topic"]

    facts = f"""
    {topic} is an important and rapidly growing field.
    It has applications in technology, healthcare, education, and business.
    Organizations use {topic} to improve efficiency and decision-making.
    Research and innovation in {topic} continue to expand worldwide.
    Professionals with expertise in {topic} are highly valued in the job market.
    """

    return {"facts": facts}


async def summarizer(state: AgentState):
    await asyncio.sleep(1)

    summary = (
        f"{state['topic']} is a significant field with growing importance across "
        f"multiple industries. It helps organizations improve performance, drives "
        f"innovation, and creates strong career opportunities. Continued research "
        f"and adoption make it a valuable area of study and development."
    )

    return {"summary": summary}


graph = StateGraph(AgentState)

graph.add_node("researcher", researcher)
graph.add_node("summarizer", summarizer)

graph.set_entry_point("researcher")
graph.add_edge("researcher", "summarizer")
graph.add_edge("summarizer", END)

workflow = graph.compile()


@app.get("/")
async def root():
    return {
        "message": "Research Agent API is running"
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

        return {
            "summary": result["summary"],
            "execution_time": execution_time,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow failed: {str(error)}",
        )