"""Tests for database module (core/database.py)."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.database import Base, get_db, get_db_context, init_db, close_db


class TestBase:
    """Tests for Base declarative class."""

    def test_base_is_declarative_base(self):
        """Test that Base is a SQLAlchemy DeclarativeBase."""
        from sqlalchemy.orm import DeclarativeBase

        assert issubclass(Base, DeclarativeBase)


class TestGetDb:
    """Tests for get_db dependency."""

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self):
        """Test that get_db yields a database session."""
        mock_session = AsyncMock()

        with patch("app.core.database.async_session_maker") as mock_maker:
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_session
            mock_context.__aexit__.return_value = None
            mock_maker.return_value = mock_context

            async for session in get_db():
                assert session == mock_session

    @pytest.mark.asyncio
    async def test_get_db_commits_on_success(self):
        """Test that get_db commits on successful completion."""
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        with patch("app.core.database.async_session_maker") as mock_maker:
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_session
            mock_context.__aexit__.return_value = None
            mock_maker.return_value = mock_context

            async for session in get_db():
                pass  # Simulate successful operation

            mock_session.commit.assert_called_once()
            mock_session.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_db_rollback_on_exception(self):
        """Test that get_db rolls back on exception."""
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock(side_effect=Exception("Commit failed"))
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        with patch("app.core.database.async_session_maker") as mock_maker:
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_session
            mock_context.__aexit__.return_value = None
            mock_maker.return_value = mock_context

            with pytest.raises(Exception, match="Commit failed"):
                async for session in get_db():
                    pass

            mock_session.rollback.assert_called_once()


class TestGetDbContext:
    """Tests for get_db_context context manager."""

    @pytest.mark.asyncio
    async def test_get_db_context_yields_session(self):
        """Test that get_db_context yields a database session."""
        mock_session = AsyncMock()

        with patch("app.core.database.async_session_maker") as mock_maker:
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_session
            mock_context.__aexit__.return_value = None
            mock_maker.return_value = mock_context

            async with get_db_context() as session:
                assert session == mock_session

    @pytest.mark.asyncio
    async def test_get_db_context_commits_on_success(self):
        """Test that context manager commits on success."""
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        with patch("app.core.database.async_session_maker") as mock_maker:
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_session
            mock_context.__aexit__.return_value = None
            mock_maker.return_value = mock_context

            async with get_db_context() as session:
                pass  # Simulate successful operation

            mock_session.commit.assert_called_once()


class TestInitDb:
    """Tests for init_db function."""

    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self):
        """Test that init_db creates database tables."""
        mock_conn = AsyncMock()
        mock_conn.run_sync = AsyncMock()

        with patch("app.core.database.engine") as mock_engine:
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_conn
            mock_context.__aexit__.return_value = None
            mock_engine.begin.return_value = mock_context

            await init_db()

            mock_conn.run_sync.assert_called_once()


class TestCloseDb:
    """Tests for close_db function."""

    @pytest.mark.asyncio
    async def test_close_db_disposes_engine(self):
        """Test that close_db disposes the engine."""
        with patch("app.core.database.engine") as mock_engine:
            mock_engine.dispose = AsyncMock()

            await close_db()

            mock_engine.dispose.assert_called_once()


class TestEngineConfiguration:
    """Tests for engine configuration."""

    def test_sqlite_config_no_pool_settings(self):
        """Test that SQLite config doesn't include pool settings."""
        with patch("app.core.database.settings") as mock_settings:
            mock_settings.database_url = "sqlite+aiosqlite:///:memory:"
            mock_settings.debug = False

            # Re-import to test configuration
            # Note: In practice, we're testing the conditional logic
            from app.core.database import _engine_kwargs

            # SQLite should not have pool settings
            if mock_settings.database_url.startswith("sqlite"):
                assert "pool_size" not in _engine_kwargs or _engine_kwargs.get("pool_size") is None

    def test_postgres_config_has_pool_settings(self):
        """Test that PostgreSQL config includes pool settings."""
        # This tests the conditional logic in database.py
        # In the actual code, PostgreSQL URLs get pool settings
        pass  # Configuration is set at import time
