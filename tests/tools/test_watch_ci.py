"""Following the CI run of the pushed commit (tools/watch_ci.py)."""

import pytest

import watch_ci


@pytest.mark.feature("MAINT-02")
def test_the_run_is_awaited_until_github_creates_it():
    answers = iter(["", "", "12345"])
    pauses = []
    assert watch_ci.wait_for_run("abc1234", find=lambda commit: next(answers), pause=pauses.append) == "12345"
    assert len(pauses) == 2


@pytest.mark.feature("MAINT-02")
def test_a_run_that_never_appears_fails_instead_of_watching_nothing():
    with pytest.raises(TimeoutError):
        watch_ci.wait_for_run("abc1234", find=lambda commit: "", pause=lambda seconds: None)
