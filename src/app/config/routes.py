"""
Central routing configuration for API endpoints.

This module defines all API routes in one place for easy management
and consistent URL structure as the application grows.
"""

from dataclasses import dataclass


@dataclass
class RouteConfig:
    """Configuration for an API route."""

    prefix: str
    tags: list[str]
    description: str


# API Version
API_VERSION = "v1"
API_BASE_PREFIX = f"/{API_VERSION}"

# Route configurations
ROUTES = {
    "posts": RouteConfig(
        prefix=f"{API_BASE_PREFIX}/post",
        tags=["Posts"],
        description="Post management endpoints",
    ),
    # Add more routes as needed:
    # "users": RouteConfig(
    #     prefix=f"{API_BASE_PREFIX}/user",
    #     tags=["Users"],
    #     description="User management endpoints",
    # ),
    # "comments": RouteConfig(
    #     prefix=f"{API_BASE_PREFIX}/comment",
    #     tags=["Comments"],
    #     description="Comment management endpoints",
    # ),
}


def get_route_config(route_name: str) -> RouteConfig:
    """
    Get route configuration by name.

    Args:
        route_name: The name of the route (key in ROUTES)

    Returns:
        RouteConfig for the specified route

    Raises:
        KeyError: If route_name not found
    """
    if route_name not in ROUTES:
        raise KeyError(f"Route '{route_name}' not found. Available routes: {list(ROUTES.keys())}")
    return ROUTES[route_name]


def get_all_routes() -> dict[str, RouteConfig]:
    """Get all route configurations."""
    return ROUTES.copy()


def list_routes() -> list[str]:
    """Get list of all available route names."""
    return list(ROUTES.keys())
