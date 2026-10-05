import pytest
from configs.config import Config
from utils.logger import get_logger
from pathlib import Path

#from playwright.sync_api import Page

#CLI options
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        default = "qa",
        action = "store",
        help = "Environments to run test against"
    )

def pytest_addoption(parser):
    parser.addoption(
        "---headed",
        default = "qa",
        action = "store",
        help = "Browser launch in headed mode"
    )

#Session Scoped fixtures
#Reads the CLI and resolves the environment value
@pytest.fixture(scope="session")
def environment(request):
    return request.config.getoption("--env")

#Gets the env value from the config file
@pytest.fixture(scope="session")
def config(environment):
    return Config.get_environment(environment)

#provides the page object to the POM classes
@pytest.fixture
def app_page(page, config):
    page.set_default_timeout(config["timeout"])
    page.set_default_navigation_timeout(config["navigation_timeout"])
    return page

#Hook - pytest hooks for test reports - Loggings and observability
def pytest_runtest_makereport(item, call):
    logger = get_logger()

    if call.when == "call":
        logger.info(
        f"TEST ATTEMPT RESULT: {item.name} | "
        f"OUTCOME: {call.excinfo is None}"
    )

    if call.when == "call" and call.excinfo is not None:

        logger.error(f"TEST FAILED: {item.name}")
        logger.error(f"EXCEPTION: {call.excinfo.value}")

        
        
        project_root = Path.cwd()
        
        for entry in call.excinfo.traceback:
            entry_path = Path(entry.path)

            if project_root in entry_path.parents and ".venv" not in entry_path.parts:
                logger.error(
                f"FAILURE LOCATION: "
                f"{entry.path}:{entry.lineno + 1} | "
                f"{entry.name} | "
                f"{entry.statement}")

        page = item.funcargs["app_page"]

        page.screenshot(path ="test-results/test-failure.png")     

#sets the browser context configs and view port settings at the POM
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, config):
    return {
        **browser_context_args,
        "viewport": config["viewport"]
    }




















































#conftest.py currently owns framework configuration, while pytest-playwright owns the browser/page lifecycle.

# conftest.py
# ├── Environment selection
# └── Application configuration

# pytest-playwright
# ├── Browser
# ├── Context
# └── Page

