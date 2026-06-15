import asyncio
import logging
from datetime import datetime
from fastapi import HTTPException
from app.services.gemini_client import evaluate_with_gemini
from app.services.database import db_manager

logger = logging.getLogger("app.services.queue_worker")
task_queue = asyncio.Queue()

async def evaluation_worker():
    while True:
        payload, response_future = await task_queue.get()
        
        max_retries = 5
        base_delay = 2.0
        success = False
        
        for attempt in range(max_retries):
            try:
                await asyncio.sleep(1)
                
                result_text = evaluate_with_gemini(
                    problem=payload.problemDescription,
                    language=payload.programmingLanguage,
                    code=payload.userCode,
                    skill=payload.skill
                )
                
                submission_doc = {
                    "problem": payload.problemDescription,
                    "language": payload.programmingLanguage,
                    "code": payload.userCode,
                    "skill_level": payload.skill,
                    "ai_evaluation": result_text,
                    "timestamp": datetime.utcnow()
                }
                
                await db_manager.db.submissions.insert_one(submission_doc)
                
                response_future.set_result({"evaluation": result_text})
                success = True
                break
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed. Retrying in {wait_time}s. Error: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Failed after {max_retries} attempts.")
        
        if not success:
            response_future.set_exception(
                HTTPException(status_code=503, detail="Service unavailable.")
            )
        
        task_queue.task_done()

async def start_background_workers(num_workers: int = 3):
    for _ in range(num_workers):
        asyncio.create_task(evaluation_worker())