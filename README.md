# 🚀 DNS Server Automation

A repository destined to check current network capabilities using different DNS servers.  

This README describes project goals, architecture, installation, configuration, testing, and reporting workflows.

---

## ⚙️ Installation & Setup

Follow these steps to get the framework up and running locally:

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/dns-server-automation.git
```

### 2. Navigate to Project Directory
```bash
cd dns-server-automation
```

### 3. Install Dependencies with Poetry
This project uses Poetry for dependency management and environment isolation.

If Poetry is not installed:

```bash
pip install poetry
```

or 

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Then install dependencies:
```bash
poetry install
```

This will:
- Create a virtual environment for the project (if not already existing).
- Install all dependencies listed in pyproject.toml.

### 4. Activate the Poetry Environment
```bash
poetry shell
```

Alternatively, you can run commands inside the environment without activating it:
```bash
poetry run pytest
```

### 5. Install Playwright Browsers
Playwright requires browser binaries (Chromium, Firefox, WebKit).
Run once after setup:

```bash
poetry run playwright install
```

✅ At this point the framework is ready to run tests.

## 🧪 Running Tests
There are three main ways to run tests in this framework:
- Locally (on your machine, using your system DNS and local Playwright browsers).
- With Docker Compose (spins up test container + supporting services, e.g., DNS mocks).
- Inside a Docker container (build once, run in a containerized environment).

---

### 1. Running Locally

You can run the tests directly on your local machine.

This mode will use your system DNS servers unless explicitly overridden.

#### Default Configuration

The framework loads test settings from YAML config files located in `configs/`.
Example: `configs/default.yaml`.

#### Running Pytest

```bash
poetry run pytest tests/e2e/test_web_page_network_properties.py
```

By default, it will pick up `configs/default.yaml`.

You can override the config:
```bash
poetry run pytest --taf-config=configs/custom.yaml
```

Or override the DNS server for tests:
```bash
poetry run pytest --dns-server=8.8.8.8
```

#### 💡 Under the hood:
- Configs are loaded via `src/taf_core/config/loader.py`.
- `pytest_addoption` in `tests/conftest.py` wires CLI flags into the config model (`src/taf_core/config/model.py`).
- Config is injected into tests via the `taf_config` fixture.

####  Running with Docker Compose

Use this when you want an isolated test environment that includes the framework container plus additional services (e.g., mock DNS resolver, test web apps).

Typical workflow:
```bash
docker-compose up --build
```

This will:
- Build the framework image.
- Start services defined in `docker-compose.yaml`.
- Execute the test suite inside the container, producing `allure/allure-results` in mounted volumes.

Config can still be overridden:
```bash
docker-compose run --rm taf pytest --taf-config=configs/custom.yaml
```

#### Running Inside a Docker Container
You can also build and run the test framework in a standalone Docker container.

Build the image:
```bash
docker build -t pytest-dns-server-automation .
```

Run tests:
```bash
docker run --rm \           
    -e DNS_SERVERS="8.8.8.8" \
    -v $(pwd)allure/allure-results:/app/allure-results \
    -v $(pwd)allure/allure-report:/app/allure-report \
    pytest-dns-server-automation
```

✅ Summary:
- Local: fast iteration, uses host DNS.
- Docker Compose: isolated system with supporting services.
- Docker: portable, consistent execution environment.

## 📸 Artifacts & Reports

The framework provides built-in support for collecting **videos, screenshots, traces**, and generating **Allure reports**.  
Artifacts are useful for debugging failed tests and analyzing test runs in detail.

---

### 🔹 Configuration (artifacts section in `configs/default.yaml`)

You can configure which artifacts to collect in your YAML config:

```yaml
artifacts:
  video:
    enabled: true
    mode: retain-on-failure  # ["retain-on-failure", "on", "off"]
    dir: artifacts/video
    context_level: true      # if true, one video per browser context
  screenshots_dir: artifacts/screenshots
  trace:
    enabled: false
    mode: retain-on-failure  # ["retain-on-failure", "on", "off"]
    dir: artifacts/trace
```

### 🔹 Video Recording

- If `enabled: true`, tests will capture **browser video recordings**.  
- `mode` defines when to record:
  - `retain-on-failure`: keeps video only if the test fails (recommended)
  - `on`: always record
  - `off`: disable video
- `context_level: true` → one video file per test **context** (not per page)

Videos are stored under: `artifacts/video/`

### 🔹 Screenshots
Screenshots are taken automatically on failures.

They are stored under: `artifacts/screenshots/`

### 🔹 Traces

Traces are Playwright’s detailed timeline recording of all browser actions.
Enable it in config:

```yaml
trace:
  enabled: true
  mode: retain-on-failure
  dir: artifacts/trace
```

Stored under: `artifacts/trace/`

You can later open them with:
`npx playwright show-trace artifacts/trace/<trace-file>.zip`

### 📊 Allure Reporting

Allure provides a **clean UI** for exploring test results, artifacts, and logs.

#### Configuration

The framework is already integrated with the **Allure Pytest plugin**.  
In `pyproject.toml`, the results directory is defined:

```toml
[tool.pytest.ini_options]
addopts = [
    "--alluredir", "allure/allure-results",
]
```

#### Generating Reports

After running tests:

```bash
allure generate ./allure/allure-results/1.1.1.1 --clean -o allure/allure-report/1.1.1.1
```

or 

```bash
allure generate ./allure/allure-results/ --clean -o allure/allure-report
```

#### Opening Reports

To open the interactive Allure report in a browser:

```bash
allure open allure/allure-report
```

This report will include:
- Test results (passed/failed/skipped).
- Linked artifacts (videos, screenshots, traces).
- Timing, steps, and logs.
