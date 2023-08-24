# Semantic Deduplicator

[![PyPI](https://img.shields.io/pypi/v/semantic-deduplicator.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/semantic-deduplicator.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/semantic-deduplicator)][pypi status]
[![License](https://img.shields.io/pypi/l/semantic-deduplicator)][license]

[![Read the documentation at https://semantic-deduplicator.readthedocs.io/](https://img.shields.io/readthedocs/semantic-deduplicator/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/gkamradt/semantic-deduplicator/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/gkamradt/semantic-deduplicator/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/semantic-deduplicator/
[read the docs]: https://semantic-deduplicator.readthedocs.io/
[tests]: https://github.com/gkamradt/semantic-deduplicator/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/gkamradt/semantic-deduplicator
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Overview
One of the most annoying parts of gathering strings for a list is deduplicating them. Let's fix this



    sd = SemanticDeduplicator(similarity_background="You are helping me deduplicate feature requests for a product")

    sd.add_item("Please speed up your app, it is very slow")
    sd.add_item("I want dark mode")
    sd.add_item("I wish there was a darker version of your app")

    # >> Improve application speed, Implement Dark Mode


## Installation

You can install _Semantic Deduplicator_ via [pip] from [PyPI]:

```console
$ pip install semantic-deduplicator
```

## Usage

Please see the [Command-line Reference] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_Semantic Deduplicator_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits


[pypi]: https://pypi.org/
[file an issue]: https://github.com/gkamradt/semantic-deduplicator/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/gkamradt/semantic-deduplicator/blob/main/LICENSE
[contributor guide]: https://github.com/gkamradt/semantic-deduplicator/blob/main/CONTRIBUTING.md
[command-line reference]: https://semantic-deduplicator.readthedocs.io/en/latest/usage.html
