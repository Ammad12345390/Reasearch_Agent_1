from datetime import datetime, timezone

from app.database import research_logs_collection


async def save_log(data: dict):
    """
    Save agent execution logs to MongoDB.
    """

    log = {
        "user_id": data.get("user_id"),
        "topic": data.get("topic"),
        "summary": data.get("summary"),
        "execution_time": data.get("execution_time"),
        "timestamp": datetime.now(timezone.utc)
    }

    result = await research_logs_collection.insert_one(log)

    return {
        "message": "Log saved successfully",
        "log_id": str(result.inserted_id)
    }