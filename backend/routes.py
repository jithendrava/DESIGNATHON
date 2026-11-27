from fastapi import APIRouter
router=APIRouter()
@router.get("/health")
def health(): return {"status":"ok"}
@router.get("/patients")
def patients(): return [{"id":1,"risk":84}]