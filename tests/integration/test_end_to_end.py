import sys
from textwrap import dedent

import pytest


pytest_plugins = ["pytester"]


TOUCH_SCRIPT = (
    "{envpython} -c "
    """'from pathlib import Path; (Path("{envdir}") / "{envname}.txt").touch()'"""
)


@pytest.mark.parametrize(
    "ignore_env_name_mismatch_spec, exp_reuse",
    [
        ["runner = ignore_env_name_mismatch", True],
        ["", False],
    ],
)
def test_testenv_reuse(pytester, monkeypatch, ignore_env_name_mismatch_spec, exp_reuse):
    """Environment should not be recreated if runner is ignore_env_name_mismatch."""
    envlist = ["foo", "bar", "baz"]
    monkeypatch.delenv(
        "TOX_WORK_DIR", raising=False
    )  # don't use the calling environment's workdir
    pytester.makeini(
        dedent(
            """
            [testenv]
            env_dir = {toxworkdir}{/}shared
            %s
            commands = %s
            """
            % (ignore_env_name_mismatch_spec, TOUCH_SCRIPT)
        ),
    )
    pytester.run(sys.executable, "-m", "tox", "-e", ",".join(envlist))
    names_in_shared = [p.name for p in (pytester.path / ".tox" / "shared").iterdir()]
    if exp_reuse:
        exp_in_dir = envlist[:]
        exp_not_in_dir = []
    else:
        exp_in_dir = envlist[-1:]
        exp_not_in_dir = envlist[:-1]
    for env in exp_in_dir:
        assert f"{env}.txt" in names_in_shared
    for env in exp_not_in_dir:
        assert f"{env}.txt" not in names_in_shared


def test_testenv_no_reuse(pytester, monkeypatch):
    """Although ignore_env_name_mismatch = true, the env can be recreated for other reasons."""
    monkeypatch.delenv("TOX_WORK_DIR", raising=False)
    pytester.makeini(
        dedent(
            """
            [tox]
            envlist = foo, bar

            [testenv]
            env_dir = {toxworkdir}{/}shared
            runner = ignore_env_name_mismatch
            deps = wheel
            commands = %s

            [testenv:bar]
            deps = wheel < 38.4
            """
            % TOUCH_SCRIPT
        )
    )
    resp = pytester.run(sys.executable, "-m", "tox")
    names_in_shared = [p.name for p in (pytester.path / ".tox" / "shared").iterdir()]
    assert "bar.txt" in names_in_shared
    assert "foo.txt" not in names_in_shared
    resp.stdout.fnmatch_lines(["bar: recreate env because requirements removed: wheel"])
