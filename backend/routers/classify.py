import io
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image, UnidentifiedImageError

from model import classifier
from schemas import ClassificationResponse, BatchClassificationResponse, BatchItemResult
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_BATCH_SIZE = 10


@router.post("/classify", response_model=ClassificationResponse)
async def classify(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, f"Unsupported file type: {file.content_type}")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(413, f"File exceeds {settings.max_upload_size_mb} MB limit")

    try:
        img = Image.open(io.BytesIO(contents)).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(400, "Could not read image file")

    try:
        return classifier.predict(img)
    except Exception:
        logger.exception("Inference failed")
        raise HTTPException(500, "Inference failed")


@router.post("/classify-batch", response_model=BatchClassificationResponse)
async def classify_batch(files: list[UploadFile] = File(...)):
    if len(files) > MAX_BATCH_SIZE:
        raise HTTPException(413, f"Max {MAX_BATCH_SIZE} images per batch")

    images = []
    filenames = []
    results = []

    for file in files:
        if file.content_type not in ALLOWED_TYPES:
            results.append(BatchItemResult(filename=file.filename, error=f"Unsupported type: {file.content_type}"))
            continue

        contents = await file.read()
        size_mb = len(contents) / (1024 * 1024)
        if size_mb > settings.max_upload_size_mb:
            results.append(BatchItemResult(filename=file.filename, error="File too large"))
            continue

        try:
            img = Image.open(io.BytesIO(contents)).convert("RGB")
            images.append(img)
            filenames.append(file.filename)
        except UnidentifiedImageError:
            results.append(BatchItemResult(filename=file.filename, error="Could not read image"))

    if images:
        try:
            predictions = classifier.predict_batch(images)
            for filename, pred in zip(filenames, predictions):
                results.append(BatchItemResult(filename=filename, **pred))
        except Exception:
            logger.exception("Batch inference failed")
            for filename in filenames:
                results.append(BatchItemResult(filename=filename, error="Inference failed"))

    return BatchClassificationResponse(results=results)