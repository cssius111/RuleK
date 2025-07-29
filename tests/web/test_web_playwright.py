import os
import shutil
import subprocess
import time

import pytest
from playwright.sync_api import sync_playwright, Error


@pytest.fixture(scope="session")
def backend_server():
    proc = subprocess.Popen(["python", "web/backend/run_server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3)
    yield
    proc.terminate()
    proc.wait()

@pytest.fixture(scope="session")
def frontend_server():
    if shutil.which("npm") is None:
        pytest.skip("npm not available")
    if not os.path.isdir("web/frontend/node_modules"):
        pytest.skip("frontend dependencies not installed")
    proc = subprocess.Popen(["npm", "run", "dev", "--", "--port", "5173"], cwd="web/frontend", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)
    yield
    proc.terminate()
    proc.wait()

@pytest.mark.slow
def test_frontend_homepage(backend_server, frontend_server):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("http://localhost:5173")
            assert "RuleK" in page.title()
            browser.close()
    except Error as e:
        pytest.skip(f"Playwright not fully installed: {e}")
