from pydantic import BaseModel

class Observation(BaseModel):
    decision_text: str
    context: str

class Action(BaseModel):
    decision: str
    corrected_output: str