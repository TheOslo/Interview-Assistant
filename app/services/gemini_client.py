from google import genai
from app.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

PROMPTS = {
    "interviewer": "You are an expert technical interviewer evaluating a Data Structures and Algorithms solution.\nProblem: {problem}\nLanguage: {language}\nCode: {code}",
    "caveman": "Me caveman. Code work? Bug where? Fix how? No big words. Short answer.\nProblem: {problem}\nLanguage: {language}\nCode: {code}",
    "direct": "Evaluate this code strictly. 1. Time/Space Complexity. 2. Critical Bugs. 3. Max 3 bullet points.\nProblem: {problem}\nLanguage: {language}\nCode: {code}"
}

def evaluate_with_gemini(problem: str, language: str, code: str, skill: str = "interviewer") -> str:
    prompt_template = PROMPTS.get(skill, PROMPTS["interviewer"])
    prompt = prompt_template.format(problem=problem, language=language, code=code)
    
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=prompt,
    )
    return response.text