FROM python:3.13-slim
WORKDIR /artifact
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || ( \
    apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl ca-certificates \
    && curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal \
    && . /root/.cargo/env \
    && pip install --no-cache-dir -r requirements.txt )
COPY pyproject.toml LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir --no-deps .
ENV MPLBACKEND=Agg
ENTRYPOINT ["shining-run-all"]
