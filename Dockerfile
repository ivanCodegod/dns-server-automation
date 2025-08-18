FROM mcr.microsoft.com/playwright/python:v1.54.0-noble

RUN apt-get update && apt-get install --no-install-recommends -y \
    wget \
    unzip \
    default-jre \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

# Set up the Poetry environment path correctly
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY . .

# Install dependencies with Poetry
RUN poetry config virtualenvs.in-project true && poetry install --no-interaction --no-root

# Install Allure CLI
RUN apt-get update && apt-get install --no-install-recommends -y \
    && curl -Lo /tmp/allure.zip https://github.com/allure-framework/allure2/releases/download/2.34.1/allure-2.34.1.zip?raw=true \
    && unzip /tmp/allure.zip -d /opt/ \
    && ln -s /opt/allure-2.34.1/bin/allure /usr/bin/allure \
    && rm /tmp/allure.zip

# Set up the virtual environment path correctly for the appuser
ENV PATH="/app/.venv/bin:$PATH"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]