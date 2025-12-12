from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_db
from ...services.analyzeService import AnalyzeService
from ...models.dto.analyzeDTO import AnalyzeRequestDTO
from ...common.apiResponse import APIResponse

router = APIRouter(prefix="/analyze", tags=["Analyze"])
service = AnalyzeService()


@router.post("/", response_model=APIResponse)
async def analyze(request: AnalyzeRequestDTO):
    try:        
        result = service.analyze(request)
        return APIResponse.success(
            data=result,
            message="Analysis completed successfully",
        )

    except Exception as e:
        return APIResponse.error(
            message=f"Analysis failed: {str(e)}",
            code=500,
        )
