from ..ml.modelLoader import predict_emotion
from ..sentiment import index_to_label
from ..models.dto.analyzeDTO import AnalyzeResponseDTO

class AnalyzeService:

    @staticmethod
    def analyze_text(text: str):
        probs = predict_emotion(text)  # returns dict[str, float]

        best_idx = max(probs, key=probs.get)
        label = index_to_label(best_idx)

        return label, probs

    @staticmethod
    def analyze(request):
        text = request.text
        label, probs = AnalyzeService.analyze_text(text)

        return AnalyzeResponseDTO(
            label=label,
            probabilities=probs
        )
