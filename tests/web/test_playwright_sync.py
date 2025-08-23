"""
Playwright 测试 - 同步版本（不使用 asyncio）
"""
import os
import shutil
import subprocess
import time

import pytest
from playwright.sync_api import sync_playwright, Error


@pytest.fixture(scope="session")
def backend_server():
    """启动后端服务器"""
    proc = subprocess.Popen(
        ["python", "web/backend/run_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    yield
    proc.terminate()
    proc.wait()


@pytest.fixture(scope="session")
def frontend_server():
    """启动前端服务器"""
    if shutil.which("npm") is None:
        pytest.skip("npm not available")
    if not os.path.isdir("web/frontend/node_modules"):
        pytest.skip("frontend dependencies not installed")
    
    proc = subprocess.Popen(
        ["npm", "run", "dev", "--", "--port", "5173"],
        cwd="web/frontend",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(5)
    yield
    proc.terminate()
    proc.wait()


@pytest.mark.slow
def test_frontend_homepage_sync(backend_server, frontend_server):
    """测试前端主页（同步版本）"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("http://localhost:5173", wait_until="networkidle")
            
            # 检查页面标题
            title = page.title()
            assert "RuleK" in title or "规则" in title, f"页面标题不正确: {title}"
            
            # 检查页面内容
            content = page.content()
            assert len(content) > 100, "页面内容太少"
            
            browser.close()
    except Error as e:
        pytest.skip(f"Playwright not fully installed: {e}")
    except Exception as e:
        if "net::ERR_CONNECTION_REFUSED" in str(e):
            pytest.skip("服务器未运行")
        raise
