"""
Test suite for app.config.routes module.

Tests the centralized route configuration system.
"""

import pytest
from app.config.routes import (
    API_BASE_PREFIX,
    API_VERSION,
    ROUTES,
    RouteConfig,
    get_all_routes,
    get_route_config,
    list_routes,
)


class TestRouteConfig:
    """Test RouteConfig dataclass."""

    def test_route_config_creation(self):
        """Test creating a RouteConfig instance."""
        config = RouteConfig(
            prefix="/api/v1/posts",
            tags=["Posts"],
            description="Post management endpoints",
        )

        assert config.prefix == "/api/v1/posts"
        assert config.tags == ["Posts"]
        assert config.description == "Post management endpoints"

    def test_route_config_with_multiple_tags(self):
        """Test RouteConfig with multiple tags."""
        config = RouteConfig(
            prefix="/api/v1/posts",
            tags=["Posts", "Content"],
            description="Post management",
        )

        assert len(config.tags) == 2
        assert "Posts" in config.tags
        assert "Content" in config.tags

    def test_route_config_attributes(self):
        """Test RouteConfig has all required attributes."""
        config = RouteConfig(
            prefix="/test",
            tags=["Test"],
            description="Test route",
        )

        assert hasattr(config, "prefix")
        assert hasattr(config, "tags")
        assert hasattr(config, "description")


class TestApiVersionAndPrefix:
    """Test API version and base prefix constants."""

    def test_api_version_is_string(self):
        """Test API_VERSION is a string."""
        assert isinstance(API_VERSION, str)
        assert len(API_VERSION) > 0

    def test_api_version_value(self):
        """Test API_VERSION has expected value."""
        assert API_VERSION == "v1"

    def test_api_base_prefix_includes_version(self):
        """Test API_BASE_PREFIX includes the version."""
        assert API_VERSION in API_BASE_PREFIX

    def test_api_base_prefix_starts_with_slash(self):
        """Test API_BASE_PREFIX starts with /."""
        assert API_BASE_PREFIX.startswith("/")

    def test_api_base_prefix_value(self):
        """Test API_BASE_PREFIX has expected value."""
        assert API_BASE_PREFIX == "/v1"


class TestRoutesRegistry:
    """Test the ROUTES registry."""

    def test_routes_is_dictionary(self):
        """Test ROUTES is a dictionary."""
        assert isinstance(ROUTES, dict)

    def test_routes_not_empty(self):
        """Test ROUTES registry is not empty."""
        assert len(ROUTES) > 0

    def test_routes_has_posts_entry(self):
        """Test ROUTES has posts entry."""
        assert "posts" in ROUTES

    def test_posts_route_is_route_config(self):
        """Test posts route is a RouteConfig instance."""
        assert isinstance(ROUTES["posts"], RouteConfig)

    def test_posts_route_configuration(self):
        """Test posts route has correct configuration."""
        config = ROUTES["posts"]

        assert config.prefix == "/v1/post"
        assert "Posts" in config.tags
        assert "description" in config.__dict__

    def test_routes_values_are_route_configs(self):
        """Test all routes are RouteConfig instances."""
        for _name, config in ROUTES.items():
            assert isinstance(config, RouteConfig)
            assert hasattr(config, "prefix")
            assert hasattr(config, "tags")
            assert hasattr(config, "description")


class TestGetRouteConfig:
    """Test get_route_config function."""

    def test_get_route_config_existing_route(self):
        """Test getting an existing route configuration."""
        config = get_route_config("posts")

        assert isinstance(config, RouteConfig)
        assert config.prefix == "/v1/post"

    def test_get_route_config_returns_same_instance(self):
        """Test that get_route_config returns the registered instance."""
        config1 = get_route_config("posts")
        config2 = get_route_config("posts")

        assert config1 is config2

    def test_get_route_config_nonexistent_raises_key_error(self):
        """Test getting non-existent route raises KeyError."""
        with pytest.raises(KeyError):
            get_route_config("nonexistent")

    def test_get_route_config_case_sensitive(self):
        """Test that route names are case-sensitive."""
        get_route_config("posts")  # Should work

        with pytest.raises(KeyError):
            get_route_config("Posts")  # Should fail

    def test_get_route_config_returns_route_config_type(self):
        """Test that get_route_config always returns RouteConfig."""
        config = get_route_config("posts")
        assert type(config).__name__ == "RouteConfig"


class TestGetAllRoutes:
    """Test get_all_routes function."""

    def test_get_all_routes_returns_dictionary(self):
        """Test get_all_routes returns a dictionary."""
        routes = get_all_routes()
        assert isinstance(routes, dict)

    def test_get_all_routes_not_empty(self):
        """Test get_all_routes returns non-empty dictionary."""
        routes = get_all_routes()
        assert len(routes) > 0

    def test_get_all_routes_contains_posts(self):
        """Test get_all_routes includes posts route."""
        routes = get_all_routes()
        assert "posts" in routes

    def test_get_all_routes_values_are_route_configs(self):
        """Test all values in get_all_routes are RouteConfig."""
        routes = get_all_routes()

        for _name, config in routes.items():
            assert isinstance(config, RouteConfig)

    def test_get_all_routes_keys_are_strings(self):
        """Test all keys in get_all_routes are strings."""
        routes = get_all_routes()

        for name in routes.keys():
            assert isinstance(name, str)

    def test_get_all_routes_same_as_routes_constant(self):
        """Test get_all_routes returns same data as ROUTES constant."""
        all_routes = get_all_routes()

        for name in ROUTES:
            assert name in all_routes
            assert all_routes[name] is ROUTES[name]


class TestListRoutes:
    """Test list_routes function."""

    def test_list_routes_returns_list(self):
        """Test list_routes returns a list."""
        routes = list_routes()
        assert isinstance(routes, list)

    def test_list_routes_not_empty(self):
        """Test list_routes returns non-empty list."""
        routes = list_routes()
        assert len(routes) > 0

    def test_list_routes_contains_strings(self):
        """Test all items in list_routes are strings."""
        routes = list_routes()

        for route_name in routes:
            assert isinstance(route_name, str)

    def test_list_routes_contains_posts(self):
        """Test list_routes includes 'posts'."""
        routes = list_routes()
        assert "posts" in routes

    def test_list_routes_same_as_routes_keys(self):
        """Test list_routes returns same names as ROUTES keys."""
        route_names = list_routes()

        for name in ROUTES:
            assert name in route_names

        assert len(route_names) == len(ROUTES)

    def test_list_routes_names_are_lowercase(self):
        """Test all route names in list are lowercase."""
        routes = list_routes()

        for name in routes:
            assert name.islower()


class TestRouteConfigProperties:
    """Test RouteConfig properties and behavior."""

    def test_route_config_prefix_is_string(self):
        """Test RouteConfig prefix is a string."""
        config = ROUTES["posts"]
        assert isinstance(config.prefix, str)

    def test_route_config_tags_is_list(self):
        """Test RouteConfig tags is a list."""
        config = ROUTES["posts"]
        assert isinstance(config.tags, list)

    def test_route_config_description_is_string(self):
        """Test RouteConfig description is a string."""
        config = ROUTES["posts"]
        assert isinstance(config.description, str)

    def test_route_config_prefix_starts_with_slash(self):
        """Test RouteConfig prefix starts with /."""
        config = ROUTES["posts"]
        assert config.prefix.startswith("/")

    def test_route_config_tags_not_empty(self):
        """Test RouteConfig tags list is not empty."""
        config = ROUTES["posts"]
        assert len(config.tags) > 0

    def test_route_config_description_not_empty(self):
        """Test RouteConfig description is not empty."""
        config = ROUTES["posts"]
        assert len(config.description) > 0


class TestRoutesUsage:
    """Test practical usage of routes configuration."""

    def test_can_construct_full_endpoint_path(self):
        """Test constructing full endpoint paths from route config."""
        config = get_route_config("posts")
        full_path = f"{config.prefix}/"

        assert full_path == "/v1/post/"

    def test_can_extract_route_tags(self):
        """Test extracting tags for OpenAPI documentation."""
        config = get_route_config("posts")
        tags = config.tags

        assert len(tags) > 0
        assert all(isinstance(tag, str) for tag in tags)

    def test_route_config_immutable_after_creation(self):
        """Test that RouteConfig instances behave consistently."""
        config1 = get_route_config("posts")
        config2 = get_route_config("posts")

        # Should be the same instance
        assert config1 is config2
