# testflow-pytest

PyTest automation suite for [TestFlow](https://github.com/qaschoolbr/testflow) — mirror of the Cypress and Playwright suites in `testflow-cypress` and `testflow-playwright`.

## Prerequisites

- Python 3.11+
- TestFlow app running locally on port `5050`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the app

```bash
docker run --rm -p 5050:5050 qaschool/testflow:latest
```

Or clone and start TestFlow from source — see the [TestFlow repo](https://github.com/qaschoolbr/testflow).

## Running tests

```bash
pytest
```

## Project structure

```
testflow-pytest/
├── tests/           # PyTest specs by feature
├── pages/           # Page Object Model
├── fixtures/        # Test data
├── support/         # Helpers, factories, API clients
└── conftest.py      # Shared fixtures and hooks
```

## Technologies

- [PyTest](https://pytest.org/)
- [Playwright for Python](https://playwright.dev/python/) or [Selenium](https://www.selenium.dev/) (TBD)
- Page Object Model with `data-testid` selectors

## License

Same as TestFlow / parent automation projects.
