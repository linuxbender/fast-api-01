from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI) -> None:
    """
    Setup CORS middleware for the FastAPI app.
    
    Args:
        app: The FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins (configure for production)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
