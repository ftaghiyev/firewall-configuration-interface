from pydantic import BaseModel

class PolicyTranslationRequest(BaseModel):
    message: str
    context: str | dict