# Contributing to Python Pest

Hi. Your contributions and questions are always welcome. Feel free to ask questions, report bugs or request features on the [issue tracker](https://github.com/jg-rp/python-pest/issues) or on [Github Discussions](https://github.com/jg-rp/python-pest/discussions). Pull requests are welcome too.

**Table of contents**

- [Development](#development)
- [Style Guides](#style-guides)

## Development

The JSONPath example in `examples/jsonpath/` and its accompanying test suite are an important part of our Pest tests. The [JSONPath Compliance Test Suite](https://github.com/jsonpath-standard/jsonpath-compliance-test-suite) is included in this repository as Git a [submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

Clone this project and **initialize the submodules** with something like:

```shell
$ git clone git@github.com:jg-rp/python-pest.git
$ cd python-pest
$ git submodule update --init
```

We use [uv](https://docs.astral.sh/uv/) to to manage project dependencies and development environments.

Run tests with pytest.

```shell
$ uv run pytest
```

Ling with [ruff](https://beta.ruff.rs/docs/).

```shell
$ uv run ruff check src tests
```

Typecheck with [Mypy](https://mypy.readthedocs.io/en/stable/).

```shell
$ uv run mypy
```

## Style Guides

### Git Commit Messages

There are no hard rules for git commit messages, although you might like to indicate the type of commit by starting the message with `docs:`, `chore:`, `feat:`, `fix:` or `refactor:`, for example.

### Python Style

We use [Ruff](https://docs.astral.sh/ruff/) to lint and format all Python files.

Ruff is configured to:

- follow [Black](https://github.com/psf/black), with its default configuration.
- expect [Google style docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).
- enforce Python imports according to [isort](https://pycqa.github.io/isort/) with `force-single-line = true`.
