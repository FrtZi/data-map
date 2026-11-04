"""The git hooks and CI driver (tools/hooks.py): what a push is refused for."""

import os
import subprocess
import time

import pytest

import hooks


def fake_run(status: str = "", files: str = "", on_tests=None):  # noqa: ANN001, ANN201
    """Replaces running a command: `git status` prints status, `git ls-files` files; the tests call on_tests."""

    def run(command, **options):  # noqa: ANN001, ANN202, ARG001
        line = " ".join(map(str, command))
        if "pytest" in line and on_tests:
            on_tests()
        out = status if "status" in line else files if "ls-files" in line else ""
        return subprocess.CompletedProcess(command, 0, stdout=out, stderr="")

    return run


@pytest.fixture(autouse=True)
def no_failure_yet(monkeypatch):
    monkeypatch.setattr(hooks, "failed", [])


@pytest.mark.feature("MAINT-02")
def test_a_push_from_a_folder_that_differs_from_its_commit_is_refused(monkeypatch):
    monkeypatch.setattr(hooks, "run", fake_run(status=" M data_map/build.py"))
    hooks.pre_push()
    assert hooks.failed == ["uncommitted changes"]


@pytest.mark.feature("MAINT-02")
def test_a_push_whose_file_was_edited_then_undone_during_the_checks_is_refused(monkeypatch, tmp_path):
    """An edit undone before the end leaves the folder clean, yet the checks may have read it."""
    (tmp_path / "x.py").write_text("")

    def edit_and_undo():
        (tmp_path / "x.py").write_text("")
        later = time.time() + 1  # the file clock ticks coarser than time.time(): the checks run for minutes
        os.utime(tmp_path / "x.py", (later, later))

    monkeypatch.setattr(hooks, "ROOT", tmp_path)
    monkeypatch.setattr(hooks, "CHECKS", [])
    monkeypatch.setattr(hooks, "run", fake_run(files="x.py", on_tests=edit_and_undo))
    hooks.pre_push()
    assert hooks.failed == ["folder changed during the checks"]


@pytest.mark.feature("MAINT-02")
def test_a_push_from_a_clean_folder_untouched_during_its_checks_passes(monkeypatch):
    monkeypatch.setattr(hooks, "CHECKS", [])
    monkeypatch.setattr(hooks, "run", fake_run())
    hooks.pre_push()
    assert hooks.failed == []
