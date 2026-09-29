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


class BatchItemResult(BaseModel):
    filename: str
    label: str | None = None
    confidence: float | None = None
    top3: list[ClassPrediction] | None = None
    error: str | None = None


class BatchClassificationResponse(BaseModel):
    results: list[BatchItemResult]