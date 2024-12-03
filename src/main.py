from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import crawl_route as crawl
from db.init_db import init_db

app = FastAPI()

origins = [
    "http://localhost:3000",  # React app running on localhost
    "http://localhost:8000",  # FastAPI running on localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/home")
async def root():
    return {"message": "Testing !"}


# Routers
app.include_router(crawl.router, prefix="/api/v1/crawl", tags=["Crawl"])


@app.on_event("startup")
def on_startup():
    init_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


