from fastapi import APIRouter, HTTPException

from app.schemas.parser import DocumentParseRequest, DocumentParseResponse
from app.services.parser_service import ParserService

router = APIRouter(prefix="/parser", tags=["parser"])

parser_service = ParserService()


@router.post("/pdf", response_model=DocumentParseResponse)
async def parse_pdf(request: DocumentParseRequest):
    try:
        return parser_service.parse_document(request.document_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(exc)}")