import logging
from google import genai
from google.genai import types
from google.genai.errors import APIError
from app.config import settings

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)

SYSTEM_INSTRUCTIONS = {
    "interviewer": "You are an expert technical interviewer evaluating a Data Structures and Algorithms solution. Evaluate time/space complexity and correctness. If providing code examples, do not use comments and avoid standard libraries, focusing on manual logic.",
    "reviewer": "You are a strict senior engineer reviewing a pull request. Point out bad practices, suggest more efficient syntax, and demand clean code. Any corrected code must be provided completely without comments.",
    "tutor": "You are a patient, encouraging coding tutor. Give hints and guide the student to understand their mistakes. Encourage manual implementation logic over relying on built-in standard libraries."
}

async def evaluate_with_gemini(problem: str, language: str, code: str, skill: str = "interviewer") -> str:
    system_instruction = SYSTEM_INSTRUCTIONS.get(skill, SYSTEM_INSTRUCTIONS["interviewer"])
    
    user_payload = f"Problem: {problem}\nLanguage: {language}\nCode to evaluate:\n```\n{code}\n```"
    
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=user_payload,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            )
        )
        
        if not response.text:
            logger.warning("Gemini returned an empty response (possible safety block).")
            return "Evaluation failed: The model could not generate a response for this input."
            
        return response.text

    except APIError as e:
        logger.error(f"Gemini API Error: {e}")
        return "Evaluation service is currently unavailable."
    except Exception as e:
        logger.error(f"Unexpected error during evaluation: {e}")
        return "An unexpected internal error occurred."