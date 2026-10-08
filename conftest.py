import pytest
from configs.config import Config
from utils.logger import get_logger
from pathlib import Path
import json

from utils.failure_artifact import failure_artifact_path

#from playwright.sync_api import Page

#CLI options
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        default = "qa",
        action = "store",
        help = "Environments to run test against"
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

#Hook - pytest setup hook before execution
def pytest_runtest_setup(item):
    logger = get_logger()
    attempt = getattr(item, "execution_count", 1)

    logger.info(f"TEST START: {item.name} | ATTEMPT : {attempt}")


#Hook - pytest hooks for test reports on call - Loggings and observability
def pytest_runtest_makereport(item, call):
    logger = get_logger()
    attempt = getattr(item, "execution_count", 1)
    failure_location = []


    if call.when == "call":
        logger.info(
        f"TEST : {item.name} | ATTEMPT : {attempt} "
        f"OUTCOME: {call.excinfo is None}"
    )

    if call.when == "call" and call.excinfo is not None:

        logger.error(f"FAILED TEST: {item.name} | ATTEMPT : {attempt} ")
        logger.error(f"EXCEPTION: {call.excinfo.value}")
        
        project_root = Path.cwd()
        
        for entry in call.excinfo.traceback:
            entry_path = Path(entry.path)

            if project_root in entry_path.parents and ".venv" not in entry_path.parts:

                failure_location.append({
                    "file" : str(entry.path),
                    "line" : entry.lineno + 1,
                    "function" : entry.name,
                    "statement" : entry.statement
                })

                logger.error(
                f"FAILURE LOCATION: "
                f"{entry.path}:{entry.lineno + 1} | "
                f"{entry.name} | "
                f"{entry.statement}")

        page = item.funcargs["app_page"]

        artifact_path = failure_artifact_path(item.name, attempt)

        page.screenshot(path=artifact_path / "screenshot.png")

        failure_data = {
            "test" : str(item.name),
            "attempt" : attempt,
            "outcome" : "Failed",
            "exception" : str(call.excinfo.value),
            "failure_location" : str(failure_location)
        }

        with open(artifact_path /"faliure.json", "w", encoding="utf-8") as file:
            json.dump(failure_data, file, indent=4)

#Hook - pytest teardown hook after call (execution)
def pytest_runtest_teardown(item):
    logger = get_logger()
    attempt = getattr(item, "execution_count", 1)

    logger.info("#"*20)
    logger.info(f"TEST END: {item.name} | ATTEMPT : {attempt}")
        

#sets the browser context configs and view port settings at the POM
@pytest.fixture(scope="function")
def browser_context_args(browser_context_args, config, request):
    attempt = getattr(request.node, "execution_count", 1)

    artificat_path = failure_artifact_path(request.node.name, attempt)

    return {
        **browser_context_args,
        "viewport": config["viewport"],
        "record_video_dir": str(artificat_path/"videos")
    }
   