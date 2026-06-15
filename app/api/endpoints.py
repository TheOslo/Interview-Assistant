import asyncio
import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import EvaluationRequest


from app.services.queue_worker import task_queue 

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/api/evaluate")
async def evaluate_code(payload: EvaluationRequest):
    loop = asyncio.get_running_loop()
    response_future = loop.create_future()
    
    await task_queue.put((payload, response_future))
    
    try:

        result = await asyncio.wait_for(response_future, timeout=25.0)
        return result
        
    except asyncio.TimeoutError:
        logger.error("Evaluation timed out. The worker took too long or crashed.")
        raise HTTPException(
            status_code=504, 
            detail="The AI evaluation is taking too long. Please try again later."
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected endpoint error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="An internal server error occurred during evaluation."
        )