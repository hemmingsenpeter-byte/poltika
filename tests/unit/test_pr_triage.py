"""The review cap includes pilot work, but not the separate decision table."""

import subprocess
from pathlib import Path

import pytest


@pytest.mark.parametrize("cap_suspended", [False, True])
def test_triage_counts_pilot_implementation_rows(tmp_path: Path, cap_suspended: bool) -> None:
    script = Path(__file__).resolve().parents[2] / ".claude/skills/pr-review/scripts/pr_triage.sh"
    remote = tmp_path / "remote.git"
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
    subprocess.run(["git", "clone", str(remote), str(repo)], check=True, capture_output=True)

    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)

    git("config", "user.name", "Review test")
    git("config", "user.email", "review@example.invalid")
    packet = repo / "review_packets"
    packet.mkdir()
    (packet / "review_queue.md").write_text(
        "| PR | Release | Scope | Touches | Risk | Status |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        "| #124 | pilot | Hosting | API | Medium | open |\n"
        + "".join(f"| #{n} | v0.3 | Work | API | Medium | open |\n" for n in range(125, 129))
        + "| #121 | v0.3 | Planner | API | Medium | reviewed (record) |\n"
        "\n## Plan and decision PRs (not counted against the cap)\n"
        "| PR | Scope | Status |\n"
        "| #129 | Plan | open |\n",
        encoding="utf-8",
    )
    if cap_suspended:
        doctrine = repo / "doctrine"
        doctrine.mkdir()
        (doctrine / "development-doctrine.md").write_text(
            "- Review debt is recorded but not capped.\n", encoding="utf-8",
        )
    git("add", ".")
    git("commit", "-m", "Queue fixture")
    git("push", "origin", "HEAD:refs/heads/main", "HEAD:refs/pull/123/head")
    result = subprocess.run(
        ["bash", str(script), "123"], cwd=repo, check=True, capture_output=True, text=True,
    )
    assert "5 (#124 #125 #126 #127 #128)" in result.stdout
    if cap_suspended:
        assert "Review-debt cap is suspended" in result.stdout
        assert "At or over the cap of five" not in result.stdout
    else:
        assert "At or over the cap of five" in result.stdout
