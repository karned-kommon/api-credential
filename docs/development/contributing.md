# Contributing Guidelines

Thank you for your interest in contributing to the API Credential service! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment as described in the [Setup Guide](setup.md)
4. Create a new branch for your feature or bug fix

## Development Workflow

1. Create a new branch from `main` for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure they follow the project's coding standards
3. Write or update tests for your changes
4. Run the tests to ensure they pass
   ```bash
   pytest
   ```

5. Format your code
   ```bash
   black .
   isort .
   ```

6. Commit your changes with a descriptive commit message
   ```bash
   git commit -m "Add feature: your feature description"
   ```

7. Push your branch to your fork
   ```bash
   git push origin feature/your-feature-name
   ```

8. Create a pull request from your fork to the main repository

## Pull Request Guidelines

When submitting a pull request, please ensure:

1. Your code follows the project's coding standards
2. All tests pass
3. Your changes are well-documented
4. Your pull request has a descriptive title and detailed description
5. Your pull request addresses only one issue or adds one feature

## Coding Standards

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all functions, classes, and modules
- Keep functions small and focused on a single responsibility
- Use meaningful variable and function names

## Testing

- Write unit tests for all new functionality
- Ensure all tests pass before submitting a pull request
- Aim for high test coverage

## Documentation

- Update documentation for any changes to the API or functionality
- Document all new features, endpoints, and configuration options
- Keep the README and other documentation up to date

## Versioning

We follow [Semantic Versioning](https://semver.org/) for this project:

- MAJOR version for incompatible API changes
- MINOR version for new functionality in a backward-compatible manner
- PATCH version for backward-compatible bug fixes

## Issue Reporting

If you find a bug or have a feature request, please create an issue on GitHub:

1. Check if the issue already exists
2. Use a clear and descriptive title
3. Provide detailed steps to reproduce the issue
4. Include relevant logs, error messages, and screenshots
5. Describe the expected behavior and the actual behavior

## Code Review Process

All submissions require review. We use GitHub pull requests for this purpose:

1. A maintainer will review your pull request
2. They may request changes or improvements
3. Once approved, a maintainer will merge your pull request

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [LICENSE](https://github.com/Karned/Kommon/blob/main/LICENSE).

## Questions?

If you have any questions or need help, please reach out to the maintainers or create an issue on GitHub.

Thank you for contributing to the API Credential service!