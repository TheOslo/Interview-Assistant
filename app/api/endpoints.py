import asyncio
from fastapi import APIRouter, HTTPException
from app.models.schemas import EvaluationRequest

router = APIRouter()

@router.post("/api/evaluate")
async def evaluate_code(payload: EvaluationRequest):
    from app.services.queue_worker import task_queue
    loop = asyncio.get_running_loop()
    response_future = loop.create_future()
    
    await task_queue.put((payload, response_future))
    
    try:
        result = await response_future
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))