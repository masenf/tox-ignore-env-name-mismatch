# tox-ignore-env-name-mismatch

[![main branch test status](https://github.com/masenf/tox-ignore-env-name-mismatch/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/masenf/tox-ignore-env-name-mismatch/actions/workflows/test.yml?query=branch%3Amain)
[![Coverage Status](https://coveralls.io/repos/github/masenf/tox-ignore-env-name-mismatch/badge.svg?branch=main)](https://coveralls.io/github/masenf/tox-ignore-env-name-mismatch?branch=main)
[![PyPI version](https://badge.fury.io/py/tox-ignore-env-name-mismatch.svg)](https://pypi.org/project/tox-ignore-env-name-mismatch)
![tox v4 support](https://img.shields.io/badge/tox-v4-green)

Reuse virtualenvs with multiple `tox` test environments.

If two environments have compatible specifications (basically, same `deps`) and
use the same `env_dir`, installing this plugin and setting
`runner = ignore_env_name_mismatch` will allow tox to use the same underlying
virtualenv for each test environment.

Development status: **EXPRIMENTAL** - The API is evolving and things are breaking.
Please vendor the plugin as described below, or you _will_ get broken.

## Usage

1. Install `tox-ignore-env-name-mismatch` in the same environment as `tox`.
2. Set `runner = ignore_env_name_mismatch` in a testenv to opt-out of recreating the virtualenv when the env name changes.

### To always use this plugin:

#### Vendor

* copy `src/tox_ignore_env_name_mismatch.py` to the root of your project
  directory as `toxfile.py`

This uses the tox4's new ["inline
plugin"](https://tox.wiki/en/latest/plugins.html#module-tox.plugin) approach
instead of relying on the provisioning system (which [can be disabled via
CLI](https://tox.wiki/en/latest/cli_interface.html#tox---no-provision)).

#### Install/provision

```
[tox]
min_version = 4.3.3
requires =
    tox-ignore-env-name-mismatch ~= 0.2.0
```

This will cause `tox` to provision a new virtualenv for `tox` itself and other
dependencies named in the
[`requires`](https://tox.wiki/en/latest/config.html#requires) key if the current
environment does not meet the specification.

Pinning the plugin to a minor version is _highly recommended_ to avoid breaking
changes.

NOTE: tox < 4.3.3 had [a bug](https://github.com/tox-dev/tox/issues/2862) which
prevented this type of installation.

## Example

```
[tox]
envlist = py39,py310,py311,lint,format,types
min_version = 4.3.3
requires =
    tox-ignore-env-name-mismatch ~= 0.2.0

[testenv]
deps = pytest
commands = pytest {posargs}

[testenv:{lint,format,types}]
env_dir = {toxworkdir}{/}static
runner = ignore_env_name_mismatch
deps =
    black
    flake8
    mypy
commands =
    lint: flake8 src tests
    format: black --check src tests
    types: mypy --strict src
```

see [`./examples`](./examples) directory for a working example including the tox configuration above.

## Why??

Typically this usage pattern is seen with "auxillary" environments that
perform project operations, like linting, generating docs, or publishing
packages. Using different `testenv` sections is a nice way to separate `commands`
and `passenv` / `setenv`, but creating separate virtualenv that would otherwise
use identical dependencies is both a waste of time and space.

In tox 3, it was possible to achieve this behavior (with a bug and some caveats)
by simply having testenvs share an `env_dir`. In tox 4, this hackaround was
properly fixed and now tox checks a cached `{envdir}/.tox-info.json` and
recreates the virtualenv if the current testenv doesn't match what is cached.

**This plugin allows a test environment to specifically opt-out of recreating
the virtualenv when only the `env_name` differs.**

This plugin only supports tox 4.

## Motivation

People have been asking for this for at least 7 years and the core `tox` project
is specifically not interested in supporting this use case in tox 4 (which is
_fine_, that's what plugins are for).

* [[tox-dev/tox#2788] Re-use of virtual environments across envs in tox4](https://github.com/tox-dev/tox/issues/2788) [2022, Github]
* [Reuse environment on Tox 4](https://stackoverflow.com/questions/74938816/reuse-environment-on-tox-4) [2022, StackOverflow]
* [tox multiple tests, re-using tox environment](https://stackoverflow.com/questions/57222212/tox-multiple-tests-re-using-tox-environment) [2019, StackOverflow]
* [[tox-dev/tox#425] Ability to share tox environments within a project](https://github.com/tox-dev/tox/issues/425) [2016, Github]
* [Tox tricks and patterns#Environment reuse](https://blog.ionelmc.ro/2015/04/14/tox-tricks-and-patterns/#environment-reuse) [2015, Blog]

## Changelog

### v0.2 - 2023-01-15

**[BREAKING]** [#3](https://github.com/masenf/tox-ignore-env-name-mismatch/issues/3) Rewrite plugin to use Public API

To upgrade to v0.2, change `ignore_env_name_mismatch = true` to `runner = ignore_env_name_mismatch`.

### v0.1 - 2023-01-14

Initial Release
