import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--run-tests",
        action="store_true",
        default=False,
        help="Run all tests; if not specified, tests will be skipped"
    )

@pytest.fixture(scope="session", autouse=True)
def check_run_flag(request):
    if not request.config.getoption("--run-tests"):
        pytest.skip("Tests skipped because --run-tests was not specified")
