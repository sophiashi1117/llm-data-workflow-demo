from __future__ import annotations

import os
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
sys.path.insert(0, str(WORKSPACE / ".vendor"))

from playwright.sync_api import sync_playwright


EDGE_PATH = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def iter_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.name == "README.md":
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())


def create_file(page, repo_url: str, rel_path: str, content: str) -> None:
    page.goto(f"{repo_url}/new/main", wait_until="domcontentloaded", timeout=120000)
    page.wait_for_timeout(2500)

    filename_input = page.locator('input[aria-label="File name"]')
    filename_input.fill(rel_path)

    editor = page.locator(".cm-content").first
    editor.click()
    page.keyboard.insert_text(content)
    page.wait_for_timeout(500)

    page.get_by_role("button", name="Commit changes...").first.click()
    page.wait_for_timeout(800)

    commit_input = page.locator('[role="dialog"] #commit-message-input')
    commit_input.fill(f"Add {rel_path}")
    page.locator('[role="dialog"] button').filter(has_text="Commit changes").first.click(force=True)
    page.wait_for_timeout(3500)


def main() -> None:
    repo_url = os.getenv("GITHUB_REPO_URL", "").strip()
    edge_profile = Path(os.getenv("EDGE_USER_DATA_DIR", ""))
    if not repo_url:
        raise RuntimeError("GITHUB_REPO_URL is required.")
    if not edge_profile.exists():
        raise RuntimeError(f"Edge profile not found: {edge_profile}")

    files = iter_files()
    print(f"total_files={len(files)}")

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
            for index, path in enumerate(files, 1):
                rel_path = path.relative_to(ROOT).as_posix()
                content = path.read_text(encoding="utf-8")
                print(f"[{index}/{len(files)}] {rel_path}")
                create_file(page, repo_url, rel_path, content)
            print(repo_url)
        finally:
            time.sleep(2)
            context.close()


if __name__ == "__main__":
    main()
