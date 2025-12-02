from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...database import get_db
from ...services.analyzeService import AnalyzeService
from ...models.dto.analyzeDTO import AnalyzeRequestDTO, AnalyzeResponseDTO

router = APIRouter(prefix="/analyze", tags=["analyze"])
service = AnalyzeService()

@router.post("/", response_model=AnalyzeResponseDTO)
async def analyze(request: AnalyzeRequestDTO, db: Session = Depends(get_db)):
    return service.analyze(request)
