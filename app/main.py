import os
import time
import asyncio
from datetime import datetime, timezone
from typing import TypedDict
import certifi
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from langgraph.graph import END, StateGraph
from tavily import TavilyClient
from groq import Groq
from motor.motor_asyncio import AsyncIOMotorClient

from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
)

load_dotenv()

app = FastAPI(title="Research Summarizer Agent API")

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "research_agent_db")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not MONGODB_URL:
    raise ValueError("MONGODB_URL is missing in .env file")

mongo_client = AsyncIOMotorClient(
    MONGODB_URL,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=30000
)
db = mongo_client[DATABASE_NAME]

users_collection = db["users"]
research_logs_collection = db["research_logs"]

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TopicRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=200)


class TopicResponse(BaseModel):
    summary: str
    execution_time: float


class AgentState(TypedDict):
    topic: str
    facts: str
    summary: str


@app.get("/")
async def root():
    return {
        "message": "FastAPI LangGraph MongoDB Atlas Tavily Groq Agent is running"
    }


@app.get("/test-db")
async def test_db():
    await mongo_client.admin.command("ping")
    return {"message": "MongoDB Atlas connected successfully"}


@app.post("/signup")
async def signup(request: SignupRequest):
    existing_email = await users_collection.find_one({"email": request.email})

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    existing_username = await users_collection.find_one(
        {"username": request.username}
    )

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )

    user = {
        "username": request.username,
        "email": request.email,
        "hashed_password": hash_password(request.password),
        "created_at": datetime.now(timezone.utc)
    }

    result = await users_collection.insert_one(user)

    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id)
    }


@app.post("/login")
async def login(request: LoginRequest):
    user = await users_collection.find_one({"email": request.email})

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token({
        "sub": str(user["_id"]),
        "email": user["email"]
    })

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user_id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"]
    }


@app.post("/logout")
async def logout():
    return {
        "message": "Logout successful. Please remove token from frontend/session."
    }


async def researcher(state: AgentState):
    search_response = await asyncio.to_thread(
        tavily_client.search,
        query=state["topic"],
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
            {
                "role": "system",
                "content": "You are a helpful research assistant."
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        temperature=0.3,
    )

    return {"summary": completion.choices[0].message.content}


graph = StateGraph(AgentState)

graph.add_node("researcher", researcher)
graph.add_node("summarizer", summarizer)

graph.set_entry_point("researcher")
graph.add_edge("researcher", "summarizer")
graph.add_edge("summarizer", END)

workflow = graph.compile()


async def save_log(
    user_id: str,
    topic: str,
    summary: str,
    execution_time: float
):
    log = {
        "user_id": user_id,
        "topic": topic,
        "summary": summary,
        "execution_time": execution_time,
        "created_at": datetime.now(timezone.utc),
    }

    result = await research_logs_collection.insert_one(log)

    return str(result.inserted_id)


@app.post("/generate-summary", response_model=TopicResponse)
async def generate_summary(
    request: TopicRequest,
    current_user=Depends(verify_access_token)
):
    start_time = time.perf_counter()

    user_id = current_user["user_id"]

    user = await users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    try:
        result = await workflow.ainvoke(
            {
                "topic": request.topic,
                "facts": "",
                "summary": "",
            }
        )

        execution_time = round(time.perf_counter() - start_time, 2)

        await save_log(
            user_id=user_id,
            topic=request.topic,
            summary=result["summary"],
            execution_time=execution_time,
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