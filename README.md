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

Contributions are very welcome! We value your time and effort to improve our project.

1. **Fork the Repository**: Start by forking the repository and cloning your fork locally.

    ```bash
    git clone https://github.com/YOUR_USERNAME/PROJECT_NAME.git
    ```

2. **Set Up Environment**: Ensure you have all the necessary development dependencies installed. If the project uses Poetry, run:

    ```bash
    poetry install
    ```

3. **Install pre-commit Hooks**: Install pre-commit hooks to ensure code quality.

    ```bash
    pip install pre-commit  # or use 'poetry add --dev pre-commit' if using Poetry
    pre-commit install
    ```

    This will install hooks defined in `.pre-commit-config.yaml`.

4. **Create a Branch**: Always make a new branch for your work.

    ```bash
    git checkout -b feature/your-feature-name
    ```

5. **Write Code**: Write your code and try to adhere to the style guidelines and best practices of the project. Don't forget to add or update tests and documentation.

6. **Run Tests**: Ensure all tests pass.

    ```bash
    # Run this command if the project uses pytest, for example
    pytest
    ```

7. **Commit Your Changes**: Commit your changes with a meaningful commit message.

    ```bash
    git commit -m "Add a feature"
    ```

8. **Push**: Push your changes to your fork.

    ```bash
    git push origin feature/your-feature-name
    ```

9. **Create a Pull Request**: Go to the original project repository and create a new pull request. Provide a meaningful description and request a review.

### Additional Guidelines

- Please make sure your code is well-formatted and adheres to the project's coding standards (typically PEP-8 for Python projects).

- If you're adding a new feature, please also consider writing and running tests to ensure everything is working as expected.

- Make sure you update the documentation to reflect your changes.

- Please be respectful of other contributors and maintainers, keeping discussions polite and sticking to the facts.

### Questions?

If you have any questions or need help with your contributions, feel free to reach out by opening an issue or reaching out to the maintainers.

To learn more about making a contribution, please see the [Contributor Guide](LINK_TO_CONTRIBUTOR_GUIDE).



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
