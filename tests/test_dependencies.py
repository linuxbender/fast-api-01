"""Unit tests for app.config.dependencies module."""

from app.config.dependencies import get_db_session
from sqlmodel import Session


class TestGetDbSession:
    """Tests for get_db_session dependency."""

    def test_get_db_session_returns_generator(self):
        """Test that get_db_session returns a generator."""
        session_gen = get_db_session()
        assert hasattr(session_gen, "__iter__")
        assert hasattr(session_gen, "__next__")

    def test_get_db_session_yields_session(self):
        """Test that get_db_session yields a Session object."""
        session_gen = get_db_session()
        session = next(session_gen)
        assert isinstance(session, Session)
        # Clean up
        try:
            next(session_gen)
        except StopIteration:
            pass

    def test_get_db_session_yields_valid_session(self):
        """Test that yielded session is properly initialized."""
        session_gen = get_db_session()
        session = next(session_gen)
        assert session is not None
        # Session should be usable
        assert hasattr(session, "execute")
        assert hasattr(session, "query")
        # Clean up
        try:
            next(session_gen)
        except StopIteration:
            pass

    def test_get_db_session_cleanup(self):
        """Test that get_db_session properly cleans up resources."""
        session_gen = get_db_session()
        next(session_gen)

        # Finish the generator to trigger cleanup
        try:
            next(session_gen)
        except StopIteration:
            pass
        # If we got here, cleanup executed without error


class TestDependenciesIntegration:
    """Integration tests for dependencies."""

    def test_get_db_session_can_be_used_multiple_times(self):
        """Test that get_db_session can be called multiple times."""
        gen1 = get_db_session()
        gen2 = get_db_session()

        session1 = next(gen1)
        session2 = next(gen2)

        # Each should be a separate session
        assert session1 is not None
        assert session2 is not None
        # They might be different instances
        # (depends on connection pooling)

        # Clean up
        for gen in [gen1, gen2]:
            try:
                next(gen)
            except StopIteration:
                pass

    def test_get_db_session_with_context_manager(self):
        """Test that database session works in dependency injection context."""
        # Simulating FastAPI's dependency injection cleanup
        session_gen = get_db_session()
        try:
            session = next(session_gen)
            assert session is not None
        finally:
            try:
                next(session_gen)
            except StopIteration:
                pass
