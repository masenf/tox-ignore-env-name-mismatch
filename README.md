# tox-ignore-env-name-mismatch

[![main branch test status](https://github.com/masenf/tox-ignore-env-name-mismatch/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/masenf/tox-ignore-env-name-mismatch/actions/workflows/test.yml?query=branch%3Amain)
[![Coverage Status](https://coveralls.io/repos/github/masenf/tox-ignore-env-name-mismatch/badge.svg?branch=main)](https://coveralls.io/github/masenf/tox-ignore-env-name-mismatch?branch=main)
[![PyPI version](https://badge.fury.io/py/tox-ignore-env-name-mismatch.svg)](https://pypi.org/project/tox-ignore-env-name-mismatch)
![tox v4 support](https://img.shields.io/badge/tox-v4-green)

Reuse virtualenvs with multiple `tox` test environments.

If two environments have compatible specifications (basically, same `deps`) and
use the same `env_dir`, installing this plugin and setting
`ignore_env_name_mismatch = true` will allow tox to use the same underlying
virtualenv for each test environment.

## Usage

1. Install `tox-ignore-env-name-mismatch` in the same environment as `tox`.
2. Set `ignore_env_name_mismatch = true` to opt-out of recreating the virtualenv when the cached name differs from the current env name.
* To always use this plugin, specify `requires = tox-ignore-env-name-mismatch` in the `[tox]` section
  of `tox.ini`

## Example

```
[tox]
envlist = py39,py310,py311,lint,format,types
requires = tox-ignore-env-name-mismatch

[testenv]
deps = pytest
commands = pytest {posargs}

[testenv:{lint,format,types}]
env_dir = {toxworkdir}{/}static
ignore_env_name_mismatch = true
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

This plugin allows a test environment to specifically opt-out of recreating the
virtualenv when only the `env_name`.

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
