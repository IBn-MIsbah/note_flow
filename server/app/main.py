from fastapi import FastAPI

from app.api.v1.api import api_router

# =========== main app instance =============

app = FastAPI(title="Note flow api", description="Note flow api", version="1.0.0")


# ======= Route registery =======
app.include_router(api_router)


# ========== Health status check ========
@app.get("/health")
async def health_check():
    return {
        "success": True,
        "message": "Health check passed",
    }
