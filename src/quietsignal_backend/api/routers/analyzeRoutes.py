from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_db
from ...services.analyzeService import AnalyzeService
from ...models.dto.analyzeDTO import AnalyzeRequestDTO, AnalyzeResponseDTO

router = APIRouter(prefix="/analyze", tags=["Analyze"])
service = AnalyzeService()


@router.post("/", response_model=dict)
async def analyze(request: AnalyzeRequestDTO, db: Session = Depends(get_db)):
    try:
        result = service.analyze(request)

        # result is expected: { "label": str, "probabilities": dict }
        return {
            "success": True,
            "status_code": 200,
            "message": "Analysis completed successfully",
            "data": result,
        }

    except Exception as e:
        return {
            "success": False,
            "status_code": 500,
            "message": "Analysis failed",
            "errors": str(e),
        }
