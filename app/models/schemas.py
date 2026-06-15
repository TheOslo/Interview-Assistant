from pydantic import BaseModel, Field

class EvaluationRequest(BaseModel):
    problemDescription: str = Field(..., max_length=2000)
    programmingLanguage: str = Field(..., max_length=50)
    userCode: str = Field(..., max_length=5000)
    skill: str = Field(default="interviewer")