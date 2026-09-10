# Contributing to AutoSender

Thank you for your interest in contributing to **AutoSender**! We welcome contributions from the community to help make automated scheduling seamless, reliable, and secure.

---

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## How Can I Contribute?

### 1. Reporting Bugs

- Search existing [Issues](../../issues) before submitting a new bug report.
- Use our [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.yml) and include:
  - Clear summary and steps to reproduce.
  - Expected vs. actual behavior.
  - OS version, Python version, and browser version.
  - Relevant logs without sensitive personal info (sanitize phone numbers/messages).

### 2. Suggesting Enhancements

- Check if your idea has already been proposed in [Issues](../../issues).
- Use our [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.yml) and explain:
  - The problem or use-case you are trying to solve.
  - Proposed solution or user experience.

### 3. Submitting Pull Requests

1. **Fork** the repository and create a new feature branch from `main`:

   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Install dependencies**:

   ```bash
   pnpm install
   pip install -r src/backend/requirements.txt
   ```

3. **Run Linters and Code Quality checks**:

   ```bash
   pnpm run lint
   python -m ruff check src/backend/ tests/
   ```

4. **Run the Full Test Suite**:

   ```bash
   pnpm run test:all
   ```

   Ensure all unit, integration, and end-to-end tests pass with 100% coverage where applicable.

5. **Commit your changes**:
   - Use standard **Conventional Commits** in **English** (e.g. `feat: add retry mechanism`, `fix: handle edge case in scheduler`).

6. **Push to your fork** and open a Pull Request against the `main` branch.

---

## Coding Standards

- **Frontend**: React + Vite with modern Vanilla CSS design tokens. No inline hardcoded secrets or arbitrary unstyled components. Linted with `oxlint`.
- **Backend**: Python 3.10+ Eel + Selenium with robust type hints and clean docstrings. Linted and formatted with `ruff`.
- **Tests**: Pytest (`pytest-cov`) and Vitest (`@vitest/coverage-v8`). All mocks must isolate Selenium drivers and Eel WebSocket connections.

---

## Security

Please refer to our [Security Policy](SECURITY.md) for vulnerability disclosure procedures. Never commit credentials, sessions, or personal user data.
