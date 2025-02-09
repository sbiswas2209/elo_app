from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.server import router

tags_metadata = [
    {
        "name": "similar",
        "description": "Find similar drugs by name",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

# Add CORS middleware to allow access from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "Ranking API"}

app.include_router(router, prefix="/api")
