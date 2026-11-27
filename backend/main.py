from fastapi import FastAPI
from backend.routes import router
app=FastAPI(title="ReadmissionAI")
app.include_router(router)