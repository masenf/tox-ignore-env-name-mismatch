import json
from unittest import mock

from tox.tox_env.api import ToxEnv, ToxEnvCreateArgs
import pytest

import tox_ignore_env_name_mismatch


def test_tox_register_tox_env_mock():
    register_mock = mock.Mock()
    tox_ignore_env_name_mismatch.tox_register_tox_env(register_mock)
    register_mock.add_run_env.assert_called_once()
    assert (
        register_mock.default_env_runner
        != tox_ignore_env_name_mismatch.IgnoreEnvNameMismatchVirtualEnvRunner.id()
    )


@pytest.fixture(params=["foo", "bar"])
def env_name(request):
    return request.param


@pytest.fixture
def tox_env(env_name, tmp_path):
    class ConfigMock(dict):
        name = env_name
        add_config = mock.Mock()
        add_constant = mock.Mock()

    cargs = ToxEnvCreateArgs(
        conf=ConfigMock({"env_dir": tmp_path}),
        core=mock.MagicMock(),
        options=mock.Mock(),
        journal=None,
        log_handler=None,
    )
    return tox_ignore_env_name_mismatch.IgnoreEnvNameMismatchVirtualEnvRunner(cargs)


def test_reusable_virtualenv_runner_cache(env_name, tox_env):
    info = tox_env.cache
    assert not info._content
    with info.compare({"name": env_name}, ToxEnv.__name__) as (eq, old):
        assert not eq

    assert info._content
    assert not info._content[ToxEnv.__name__]


SECTION_BLANK = ""
SECTION_FOO = "foo"
TOP_LEVEL_KEY_BLANK = {"empty": None}
TOP_LEVEL_KEY_FOO = {"bar": None}


@pytest.fixture
def cached_info(tmp_path):
    content = {
        SECTION_BLANK: TOP_LEVEL_KEY_BLANK.copy(),
        SECTION_FOO: TOP_LEVEL_KEY_FOO.copy(),
    }
    (tmp_path / ".tox-info.json").write_text(json.dumps(content))
    return content


@pytest.mark.usefixtures("cached_info")
@pytest.mark.parametrize(
    ("filter_keys", "filter_section", "args", "exp_eq", "exp_old"),
    [
        (None, None, ({}, SECTION_BLANK), False, TOP_LEVEL_KEY_BLANK),
        (None, None, (TOP_LEVEL_KEY_BLANK, SECTION_BLANK), True, TOP_LEVEL_KEY_BLANK),
        (
            None,
            None,
            ({"foo": "bar", **TOP_LEVEL_KEY_BLANK}, SECTION_BLANK),
            False,
            TOP_LEVEL_KEY_BLANK,
        ),
        (
            ["foo"],
            None,
            ({"foo": "bar", **TOP_LEVEL_KEY_BLANK}, SECTION_BLANK),
            True,
            TOP_LEVEL_KEY_BLANK,
        ),
        (
            ["foo"],
            None,
            ({"foo": "bar", **TOP_LEVEL_KEY_FOO}, SECTION_FOO),
            True,
            TOP_LEVEL_KEY_FOO,
        ),
        (
            ["foo"],
            SECTION_FOO,
            ({"foo": "bar", **TOP_LEVEL_KEY_BLANK}, SECTION_BLANK),
            False,
            TOP_LEVEL_KEY_BLANK,
        ),
        (
            ["foo"],
            SECTION_FOO,
            ({"foo": "bar", **TOP_LEVEL_KEY_FOO}, SECTION_FOO),
            True,
            TOP_LEVEL_KEY_FOO,
        ),
        (
            ["foo"],
            SECTION_FOO,
            (TOP_LEVEL_KEY_FOO, SECTION_FOO),
            True,
            TOP_LEVEL_KEY_FOO,
        ),
        (
            ["bar"],
            SECTION_FOO,
            (TOP_LEVEL_KEY_FOO, SECTION_FOO),
            False,
            TOP_LEVEL_KEY_FOO,
        ),
    ],
)
def test_filtered_info(tmp_path, filter_keys, filter_section, args, exp_eq, exp_old):
    info = tox_ignore_env_name_mismatch.FilteredInfo(
        tmp_path,
        filter_keys=filter_keys,
        filter_section=filter_section,
    )
    with info.compare(*args) as (eq, old):
        assert eq == exp_eq
        assert old == exp_old
