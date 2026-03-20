from __future__ import annotations

import os
import sys
import time
import mimetypes
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
sys.path.insert(0, str(WORKSPACE / ".vendor"))

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


EDGE_PATH = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
DEFAULT_EDGE_PROFILE = WORKSPACE / "edge_automation_profile"


def ensure_path(path: Path, description: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{description} not found: {path}")


def create_repo(page, repo_name: str) -> str:
    page.goto("https://github.com/new", wait_until="domcontentloaded", timeout=120000)
    page.wait_for_timeout(3000)

    if "login" in page.url.lower():
        raise RuntimeError("GitHub session is not signed in.")

    owner_button = page.locator("#owner-dropdown-header-button")
    if owner_button.count():
        owner = owner_button.first.inner_text().strip()
    else:
        owner = ""

    visibility_button = page.locator("#visibility-anchor-button")
    if visibility_button.count():
        current_visibility = visibility_button.first.inner_text().strip().lower()
        if current_visibility != "public":
            visibility_button.first.click()
            public_option = page.get_by_role("menuitemradio", name="Public")
            if public_option.count():
                public_option.first.click()

    repo_input = page.locator("#repository-name-input")
    repo_input.wait_for(timeout=120000)

    candidates = [repo_name, f"{repo_name}-1", f"{repo_name}-2", f"{repo_name}-{int(time.time())}"]
    last_url = page.url

    for candidate in candidates:
        repo_input.fill("")
        repo_input.fill(candidate)
        page.wait_for_timeout(1500)

        create_button = page.get_by_role("button", name="Create repository")
        if create_button.count() == 0:
            create_button = page.locator("button[type='submit']").filter(has_text="Create repository")
        create_button.first.click()

        page.wait_for_timeout(4000)
        if page.url != last_url and "/new" not in page.url:
            return f"https://github.com/{owner}/{candidate}"

    raise RuntimeError("Could not create repository from the available candidate names.")


def upload_files(page, repo_url: str) -> None:
    upload_url = f"{repo_url}/upload"
    page.goto(upload_url, wait_until="domcontentloaded", timeout=120000)
    page.wait_for_timeout(3000)

    file_input = page.locator("input[type='file']")
    file_input.wait_for(timeout=120000)

    payloads = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        mime_type = mimetypes.guess_type(path.name)[0] or "text/plain"
        payloads.append(
            {
                "name": path.relative_to(ROOT).as_posix(),
                "mimeType": mime_type,
                "buffer": path.read_bytes(),
            }
        )

    file_input.set_input_files(payloads)

    manifest_input = page.locator("form.file-commit-form input[name='manifest_id']")
    manifest_input.wait_for(state="attached", timeout=120000)
    start = time.time()
    while not manifest_input.input_value():
        if time.time() - start > 120:
            raise RuntimeError("Manifest id was not generated after file upload.")
        page.wait_for_timeout(1000)

    message_input = page.locator('input[name="message"]')
    if message_input.count():
        message_input.fill("init: add llm data workflow demo")

    commit_button = page.get_by_role("button", name="Commit changes")
    if commit_button.count() == 0:
        commit_button = page.locator("button[type='submit']").filter(has_text="Commit changes")
    commit_button.first.click()

    page.wait_for_load_state("domcontentloaded", timeout=120000)
    page.wait_for_timeout(5000)


def main() -> None:
    repo_name = os.getenv("GITHUB_REPO_NAME", "llm-data-workflow-demo")
    existing_repo_url = os.getenv("GITHUB_REPO_URL", "").strip()
    edge_profile = Path(
        os.getenv(
            "EDGE_USER_DATA_DIR",
            str(DEFAULT_EDGE_PROFILE),
        )
    )

    ensure_path(EDGE_PATH, "Edge executable")
    ensure_path(edge_profile, "Edge automation profile")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(edge_profile),
            executable_path=str(EDGE_PATH),
            headless=False,
            args=["--start-maximized"],
            no_viewport=True,
        )
        page = context.pages[0] if context.pages else context.new_page()

        try:
            repo_url = existing_repo_url or create_repo(page, repo_name)
            upload_files(page, repo_url)
            print(repo_url)
        except PlaywrightTimeoutError as exc:
            print(f"TIMEOUT: {exc}")
            raise
        finally:
            time.sleep(3)
            context.close()


if __name__ == "__main__":
    main()
