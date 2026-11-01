"""
FastAPI main application — NSE/BSE Custom Screener
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import asyncio

from backend.database.db import init_db
from backend.services.data_fetcher import load_screener_from_db, run_full_screener_sync
from backend.routers import screener, industries, companies, tracker

app = FastAPI(
    title="NSE/BSE Custom Screener",
    description="Powerful stock screener for NSE and BSE with RS Rating, sector tracking, and entry/exit alerts",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(screener.router)
app.include_router(industries.router)
app.include_router(companies.router)
app.include_router(tracker.router)
app.add_api_route("/api/search", screener.search_stocks, methods=["GET"])

# Serve frontend static files
frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(frontend_dir / "index.html"))

    @app.get("/{path:path}")
    async def serve_spa(path: str):
        # Serve index.html for all non-API routes (SPA routing)
        index = frontend_dir / "index.html"
        return FileResponse(str(index))


@app.on_event("startup")
async def startup():
    init_db()
    load_screener_from_db()
    # Automatically run background sync for all stocks on startup
    asyncio.create_task(run_full_screener_sync())
    print("[App] NSE/BSE Screener started!")
    print("[App] Background sync initiated for all universe stocks.")
    print("[App] Open http://localhost:8000 in your browser")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
