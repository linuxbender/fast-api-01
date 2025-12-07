from fastapi import APIRouter, FastAPI
from sqlmodel import Session

from app.config.correlation_id_middleware import CorrelationIdMiddleware
from app.config.logger import get_logger, setup_logging
from app.config.routes import get_route_config
from app.config.settings import get_settings, has_ssl_certificates
from app.config.ssl_generator import SSLCertificateGenerator
from app.controller.v1.post_controller import PostController
from app.data.database import engine
from app.data.v1.model.post import Post
from app.data.v1.post_repository import PostRepository
from app.security.cors_config import setup_cors
from app.service.v1.post_service import PostService

# Setup logging with correlation ID support
setup_logging()
logger = get_logger(__name__)

# Load settings from environment
settings = get_settings()
logger.info(f"Environment: {settings.environment}")

# Ensure SSL certificates exist (auto-generate if needed)
if not has_ssl_certificates():
    logger.info("SSL certificates not found, generating self-signed certificates...")
    generator = SSLCertificateGenerator(cert_dir=str(settings.ssl_keyfile.rsplit('/', 1)[0]))
    generator.create_certificate_directory()
    generator.generate(days_valid=365)
    logger.info(f"✅ Self-signed certificates generated in {generator.cert_dir}")
else:
    logger.debug(f"✅ SSL certificates found: {settings.ssl_keyfile}")

logger.debug("HTTPS enabled (required for all environments)")

# Create database tables
def create_db_and_tables():
    """Create all database tables."""
    Post.metadata.create_all(engine)


# Initialize FastAPI app
app = FastAPI(
    title="Generic CRUD API",
    description=(
        "FastAPI with generic CRUD operations using Repository, "
        "Service, and Controller pattern"
    ),
    version="1.0.0",
)

# Add correlation ID middleware (must be added before other middlewares)
app.add_middleware(CorrelationIdMiddleware)

# Setup CORS
setup_cors(app)

# Create database tables on startup
@app.on_event("startup")
def on_startup():
    logger.info("Application startup: Creating database tables")
    create_db_and_tables()
    logger.info("Application startup completed")


# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "OK"}


# Setup Post routes
def setup_posts_router() -> APIRouter:
    """Create and configure the posts router with centralized route configuration."""
    # Get route configuration from central config
    route_config = get_route_config("posts")
    logger.debug(f"Setting up posts router with prefix: {route_config.prefix}")

    # Create router with centralized configuration
    router = APIRouter(prefix=route_config.prefix, tags=route_config.tags)

    # Create service and controller
    session = Session(engine)
    repository = PostRepository(session)
    service = PostService(repository)

    # Initialize controller which registers routes
    PostController(router, service)
    logger.debug("Posts router setup completed")

    return router


# Include routers
app.include_router(setup_posts_router())


# Home endpoint
@app.get("/", tags=["Root"])
def hello():
    """Welcome endpoint."""
    return {
        "message": "Hello FastAPI",
        "docs": "/docs",
        "health": "/health",
    }
