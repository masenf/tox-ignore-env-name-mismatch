from unittest import mock

from tox.tox_env.api import ToxEnv, ToxEnvCreateArgs
from tox.tox_env.info import Info
from tox.tox_env.python.virtual_env.runner import VirtualEnvRunner
import pytest

import tox_ignore_env_name_mismatch


def test_tox_register_tox_env_mock():
    register_mock = mock.Mock()
    tox_ignore_env_name_mismatch.tox_register_tox_env(register_mock)
    register_mock.add_run_env.assert_called_once()
    assert (
        register_mock.default_env_runner
        == tox_ignore_env_name_mismatch.ReusableVirtualEnvRunner.id()
    )


def test_tox_add_env_config_mock():
    env_conf_mock = mock.Mock()
    tox_ignore_env_name_mismatch.tox_add_env_config(env_conf_mock)
    env_conf_mock.add_config.assert_called_once_with(
        keys=["ignore_env_name_mismatch", "ignore_envname_mismatch"],
        default=False,
        of_type=bool,
        desc="Do not recreate venv when the testenv name differs.",
    )


@pytest.fixture(params=["foo", "bar"])
def env_name(request):
    return request.param


@pytest.fixture(params=["foo", "bar"])
def cached_env_name(request):
    return request.param


@pytest.fixture(params=[True, False], ids=["ToxEnv-cache", "missing-cache"])
def env_is_cached(request, tmp_path, monkeypatch, cached_env_name):
    def mock_cache(*args, **kwargs):
        info = Info(tmp_path)
        info._content = (
            {ToxEnv.__name__: {"name": cached_env_name}} if request.param else {}
        )
        return info

    monkeypatch.setattr(VirtualEnvRunner, "cache", property(mock_cache))
    return request.param


@pytest.fixture(params=[True, False], ids=["ignore_env_name_mismatch", "default"])
def ignore_env_name_mismatch(request):
    return request.param


@pytest.fixture
def tox_env(env_name, ignore_env_name_mismatch, env_is_cached):
    class ConfigMock(dict):
        name = env_name
        add_config = mock.Mock()
        add_constant = mock.Mock()

    cargs = ToxEnvCreateArgs(
        conf=ConfigMock(
            {
                tox_ignore_env_name_mismatch.IGNORE_ENV_NAME_MISMATCH_KEY: ignore_env_name_mismatch
            }
        ),
        core=mock.MagicMock(),
        options=mock.Mock(),
        journal=None,
        log_handler=None,
    )
    return tox_ignore_env_name_mismatch.ReusableVirtualEnvRunner(cargs)


def test_reusable_virtualenv_runner_cache(
    env_name, tox_env, cached_env_name, env_is_cached, ignore_env_name_mismatch
):
    info = tox_env.cache
    env_name_from_info = info._content.get(ToxEnv.__name__, {}).get("name", None)

    if env_is_cached:
        if ignore_env_name_mismatch:
            assert env_name_from_info == env_name
        else:
            assert env_name_from_info == cached_env_name
    else:
        assert env_name_from_info is None
