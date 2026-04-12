import os
import sys


def is_testing_environment() -> bool:
    """
    Detect if we're running in a testing environment.

    This checks multiple indicators:
    1. TESTING environment variable
    2. pytest in sys.modules
    3. unittest in sys.modules
    4. APP_ENV_FILE pointing to test file
    5. Command line contains test-related keywords
    """
    # Check environment variable (support both "true" and "1")
    testing_value = os.getenv("TESTING", "").lower()
    if testing_value in ("true", "1", "yes"):
        return True

    # Check if pytest is running
    if "pytest" in sys.modules:
        return True

    # Check if unittest is running
    if "unittest" in sys.modules and any("test" in arg.lower() for arg in sys.argv):
        return True

    # Check APP_ENV_FILE
    env_file = os.environ.get("APP_ENV_FILE", "")
    if "test" in env_file.lower():
        return True

    # Check command line arguments
    test_keywords = ["test", "pytest", "unittest", "-m unittest", "-m pytest"]
    cmd_line = " ".join(sys.argv).lower()
    if any(keyword in cmd_line for keyword in test_keywords):
        return True

    return False


def is_safe_test_db(database_url: str):
    # Allow sqlite always
    url = database_url.lower()
    if "sqlite" in url:
        return True

    if "db_test" in url:
        return True

    return False
