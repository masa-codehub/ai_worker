# Python環境とgemini-cliを含むDockerfile
FROM python:3.13.3-slim-bullseye

# 作業ディレクトリを作成・設定
WORKDIR /app

# RUN命令を一つにまとめることでDockerイメージのレイヤー数を削減
RUN apt-get update && \
    apt-get install -y git && \
    apt-get install -y tmux && \
    apt-get install -y gpg && \
    apt-get install -y wget && \
    apt-get install -y curl && \
    apt-get install -y gnupg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# github CLIのリポジトリを追加し、GitHub CLIをインストール
RUN apt-get update \
    && mkdir -p -m 755 /etc/apt/keyrings \
    && wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh \
    # 最後に、インストールにのみ使用したwgetと不要なキャッシュを削除してイメージサイズを削減
    && apt-get purge -y --auto-remove wget \
    && rm -rf /var/lib/apt/lists/*

# gcloud CLIのリポジトリを追加し、Google Cloud CLIをインストール
RUN apt-get update
# RUN apt-get install -y apt-transport-https ca-certificates
# RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
# RUN apt-get update && apt-get install google-cloud-cli
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && apt-get update -y && apt-get install google-cloud-cli -y
# RUN gcloud init

# node.jsのリポジトリを追加し、Node.jsをインストール
RUN curl -sSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# gemini-cliをグローバルにインストール
RUN npm install -g @google/gemini-cli

# 必要なPythonパッケージのインストール
RUN pip install --upgrade pip
COPY requirements.in .
RUN pip install pip-tools
RUN pip-compile requirements.in
RUN pip install --no-cache-dir -r requirements.txt


# # 開発モード
# COPY pyproject.toml .
# RUN pip install -e .

# Pythonが.pycファイルを生成しないようにします。
ENV PYTHONDONTWRITEBYTECODE=1
# Pythonの出力がバッファリングされないようにします。
ENV PYTHONUNBUFFERED=1
