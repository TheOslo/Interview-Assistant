import asyncio
import logging
from datetime import datetime, timezone
from fastapi import HTTPException
from app.services.gemini_client import evaluate_with_gemini
from app.services.database import db_manager

logger = logging.getLogger("app.services.queue_worker")
task_queue = asyncio.Queue()

async def evaluation_worker():
    while True:
        try:
            payload, response_future = await task_queue.get()
            
            max_retries = 3
            base_delay = 2.0
            success = False
            
            for attempt in range(max_retries):
                try:
                    result_text = await evaluate_with_gemini(
                        problem=payload.problem_description,
                        language=payload.programming_language,
                        code=payload.user_code,
                        skill=payload.skill
                    )
                    
                    submission_doc = {
                        "problem": payload.problem_description,
                        "language": payload.programming_language,
                        "code": payload.user_code,
                        "skill_level": payload.skill,
                        "ai_evaluation": result_text,
                        "timestamp": datetime.now(timezone.utc)
                    }
                    
                    await db_manager.db.submissions.insert_one(submission_doc)
                    
                    if not response_future.done():
                        response_future.set_result({"evaluation": result_text})
                        
                    success = True
                    break
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = base_delay * (2 ** attempt)
                        logger.warning(f"Worker attempt {attempt + 1} failed. Retrying in {wait_time}s. Error: {e}")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Worker failed after {max_retries} attempts. Final error: {e}")
            
            if not success and not response_future.done():
                response_future.set_exception(
                    HTTPException(status_code=503, detail="AI evaluation service is currently unavailable.")
                )
                
        except Exception as e:
            logger.critical(f"Critical worker loop error: {e}")
            
        finally:
            task_queue.task_done()

async def start_background_workers(num_workers: int = 3):
    logger.info(f"Starting {num_workers} background evaluation workers.")
    for _ in range(num_workers):
        asyncio.create_task(evaluation_worker())