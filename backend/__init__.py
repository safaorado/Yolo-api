from pydantic import BaseModel


class ClassPrediction(BaseModel):
    label: str
    confidence: float


class ClassificationResponse(BaseModel):
    label: str
    confidence: float
    top3: list[ClassPrediction]


class HealthResponse(BaseModel):
    status: str
    classes: list[str]