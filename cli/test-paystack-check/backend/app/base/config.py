"""Base configuration shared by production and test settings."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class BaseAppSettings(BaseSettings):
    """Base configuration class shared by production and test settings."""

    @property
    def project_root(self) -> Path:
        """
        Get project root directory (backend/).

        This works from anywhere in the project by calculating relative to this file.
        app/base/config.py -> ../../ -> backend/
        """
        current_file = Path(__file__).resolve()
        return current_file.parent.parent.parent

    @property
    def app_dir(self) -> Path:
        """Get app directory path."""
        return self.project_root / "app"

    @property
    def tests_dir(self) -> Path:
        """Get tests directory path."""
        return self.project_root / "tests"

    @property
    def migrations_dir(self) -> Path:
        """Get migrations directory path."""
        return self.project_root / "migrations"

    @property
    def frontend_dir(self) -> Optional[Path]:
        """Get frontend directory path if it exists."""
        frontend_path = self.project_root.parent / "frontend"
        return frontend_path if frontend_path.exists() else None

    def validate_project_structure(self) -> None:
        """Validate that critical project directories exist."""
        if not self.project_root.exists():
            raise RuntimeError(f"Project root not found: {self.project_root}")

        if not self.app_dir.exists():
            raise RuntimeError(f"App directory not found: {self.app_dir}")

        # Tests directory is optional (might not exist in production)
        if not self.migrations_dir.exists():
            # Migrations directory is optional for some setups
            pass

    def debug_paths(self) -> None:
        """Debug helper for path resolution."""
        print("\n=== Project Structure Debug ===")
        print(f"Project root: {self.project_root}")
        print(f"App dir: {self.app_dir} (exists: {self.app_dir.exists()})")
        print(f"Tests dir: {self.tests_dir} (exists: {self.tests_dir.exists()})")
        print(f"Migrations dir: {self.migrations_dir} (exists: {self.migrations_dir.exists()})")
        if self.frontend_dir:
            print(f"Frontend dir: {self.frontend_dir} (exists: {self.frontend_dir.exists()})")
        else:
            print("Frontend dir: Not found")
        print("==============================\n")

    def get_env_file_path(self, env_file_name: str = ".env") -> Path:
        """
        Get environment file path relative to project root.

        Args:
            env_file_name: Name of the environment file (default: .env)

        Returns:
            Path to the environment file
        """
        return self.project_root / env_file_name

    def list_project_files(self, pattern: str = "*") -> list[Path]:
        """
        List files in project root matching pattern.

        Args:
            pattern: Glob pattern to match files (default: all files)

        Returns:
            List of matching file paths
        """
        return list(self.project_root.glob(pattern))
