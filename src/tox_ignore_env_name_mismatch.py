from tox.config.sets import EnvConfigSet
from tox.plugin import impl
from tox.tox_env.api import ToxEnv
from tox.tox_env.info import Info
from tox.tox_env.python.virtual_env.runner import VirtualEnvRunner
from tox.tox_env.register import ToxEnvRegister


IGNORE_ENV_NAME_MISMATCH_KEY = "ignore_env_name_mismatch"
IGNORE_ENV_NAME_MISMATCH_KEY_ALT = "ignore_envname_mismatch"


class ReusableVirtualEnvRunner(VirtualEnvRunner):
    """EnvRunner that optionall ignores name mismatch."""

    @staticmethod
    def id() -> str:
        return "virtualenv-reusable"

    @property
    def cache(self) -> Info:
        """Ignore changes in the "name" if env has `ignore_env_name_mismatch = true`."""
        info = super().cache
        toxenv_info = info._content.get(ToxEnv.__name__, {})
        if self.conf[IGNORE_ENV_NAME_MISMATCH_KEY] and toxenv_info:
            toxenv_info["name"] = self.conf.name
        return info


@impl
def tox_add_env_config(env_conf: EnvConfigSet) -> None:
    """tox4 entry point: add ignore_env_name_config env config."""
    env_conf.add_config(
        keys=[IGNORE_ENV_NAME_MISMATCH_KEY, IGNORE_ENV_NAME_MISMATCH_KEY_ALT],
        default=False,
        of_type=bool,
        desc="Do not recreate venv when the testenv name differs.",
    )


@impl
def tox_register_tox_env(register: ToxEnvRegister) -> None:
    """tox4 entry point: set ReuseVirtualEnvRunner as default_env_runner."""
    register.add_run_env(ReusableVirtualEnvRunner)
    register.default_env_runner = ReusableVirtualEnvRunner.id()
