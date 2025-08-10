#!/bin/sh

# 外部モジュールのインストール
pip install -U -r .build/repositories.txt && pip install -e .

# ファイルの存在を確認
if [ -f "main.py" ]; then
    echo "main process start"
    python "main.py"
fi
echo "main process done"
