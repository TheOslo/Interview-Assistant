from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel

class EvaluationRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    problem_description: str = Field(..., min_length=10, max_length=2000, strip_whitespace=True)
    
    programming_language: Literal["python", "javascript", "java", "cpp", "c"] = Field(...)
    
    user_code: str = Field(..., min_length=1, max_length=5000, strip_whitespace=True)
    

    skill: Literal["interviewer", "reviewer", "tutor"] = Field(default="interviewer")