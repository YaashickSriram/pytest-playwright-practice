import json
from pathlib import Path

import allure
import pytest

from configs.config import Config
from utils.failure_artifact import failure_artifact_path
from utils.logger import get_logger


# ---------------------------------------------------------------- CLI options
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        default="qa",
        action="store",
        help="Environment to run tests against",
    )


# ---------------------------------------------------------------- Fixtures
@pytest.fixture(scope="session")
def environment(request):
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def config(environment):
    return Config.get_environment(environment)


@pytest.fixture
def app_page(page, config):
    page.set_default_timeout(config["timeout"])
    page.set_default_navigation_timeout(config["navigation_timeout"])
    return page


@pytest.fixture(scope="function")
def browser_context_args(browser_context_args, config, request):
    attempt = getattr(request.node, "execution_count", 1)
    artifact_path = failure_artifact_path(request.node.name, attempt)
    return {
        **browser_context_args,
        "viewport": config["viewport"],
        "record_video_dir": str(artifact_path / "videos"),
    }


# ---------------------------------------------------------------- Lifecycle logging
def pytest_runtest_setup(item):
    attempt = getattr(item, "execution_count", 1)
    get_logger().info(f"TEST START: {item.name} | ATTEMPT : {attempt}")


def pytest_runtest_teardown(item):
    attempt = getattr(item, "execution_count", 1)
    logger = get_logger()
    logger.info("#" * 20)
    logger.info(f"TEST END: {item.name} | ATTEMPT : {attempt}")


# ---------------------------------------------------------------- Result + failure evidence
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield                      # pytest builds the report here
    report = outcome.get_result()        # now we hold the finished report

    if report.when != "call":
        return

    logger = get_logger()
    attempt = getattr(item, "execution_count", 1)
    logger.info(
        f"TEST : {item.name} | ATTEMPT : {attempt} | "
        f"OUTCOME : {report.outcome.upper()} | DURATION : {report.duration:.2f}s"
    )

    if not report.failed:
        return

    logger.error(f"FAILED TEST: {item.name} | ATTEMPT : {attempt}")
    logger.error(f"EXCEPTION: {call.excinfo.value}")

    failure_location = []
    project_root = Path.cwd()
    for entry in call.excinfo.traceback:
        entry_path = Path(entry.path)
        if project_root in entry_path.parents and ".venv" not in entry_path.parts:
            location = {
                "file": str(entry.path),
                "line": entry.lineno + 1,
                "function": entry.name,
                "statement": str(entry.statement).strip(),
            }
            failure_location.append(location)
            logger.error(f"FAILURE LOCATION: {location}")

    artifact_path = failure_artifact_path(item.name, attempt)

    page = item.funcargs.get("app_page")
    if page is not None:
        png_bytes = page.screenshot(path=artifact_path / "screenshot.png")
        allure.attach(
            png_bytes,
            name=f"Failure screenshot - attempt {attempt}",
            attachment_type=allure.attachment_type.PNG,
        )

    failure_data = {
        "test": item.name,
        "attempt": attempt,
        "outcome": "Failed",
        "exception": str(call.excinfo.value),
        "failure_location": failure_location,
    }
    failure_json = json.dumps(failure_data, indent=4)
    (artifact_path / "failure.json").write_text(failure_json, encoding="utf-8")
    allure.attach(
        failure_json,
        name="failure.json",
        attachment_type=allure.attachment_type.JSON,
    )


# ---------------------------------------------------------------- Run-level reporting
def pytest_sessionfinish(session, exitstatus):
    allure_dir = session.config.getoption("--alluredir", default=None)
    if not allure_dir:
        return
    env_file = Path(allure_dir) / "environment.properties"
    env_file.write_text(
        f"Environment={session.config.getoption('--env')}\n",
        encoding="utf-8",
    )


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    stats = terminalreporter.stats
    summary = {
        "environment": config.getoption("--env"),
        "passed": len(stats.get("passed", [])),
        "failed": len(stats.get("failed", [])),
        "errors": len(stats.get("error", [])),
        "skipped": len(stats.get("skipped", [])),
        "reruns": len(stats.get("rerun", [])),
        "exit_status": int(exitstatus),
    }
    summary["total"] = (
        summary["passed"] + summary["failed"] + summary["errors"] + summary["skipped"]
    )

    terminalreporter.write_sep("=", "EXECUTION SUMMARY")
    for key, value in summary.items():
        terminalreporter.write_line(f"{key:<12}: {value}")

    Path("reports").mkdir(exist_ok=True)
    Path("reports/summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")