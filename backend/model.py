import logging
from ultralytics import YOLO
from config import settings

logger = logging.getLogger(__name__)


class ClassifierModel:
    def __init__(self, path: str):
        logger.info(f"Loading model from {path}")
        self.model = YOLO(path)
        self.names = self.model.names
        logger.info(f"Model ready with {len(self.names)} classes")

    def predict(self, image) -> dict:
        result = self.model(image, verbose=False)[0]
        top3_idx = result.probs.top5[:3]
        top3_conf = result.probs.top5conf[:3].tolist()
        return {
            "label": self.names[result.probs.top1],
            "confidence": float(result.probs.top1conf),
            "top3": [
                {"label": self.names[i], "confidence": round(c, 4)}
                for i, c in zip(top3_idx, top3_conf)
            ],
        }

    def predict_batch(self, images: list) -> list[dict]:
        results = self.model(images, verbose=False)
        output = []
        for result in results:
            top3_idx = result.probs.top5[:3]
            top3_conf = result.probs.top5conf[:3].tolist()
            output.append({
                "label": self.names[result.probs.top1],
                "confidence": float(result.probs.top1conf),
                "top3": [
                    {"label": self.names[i], "confidence": round(c, 4)}
                    for i, c in zip(top3_idx, top3_conf)
                ],
            })
        return output


classifier = ClassifierModel(settings.model_path)