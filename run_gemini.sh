#!/bin/bash
# Gemini CLIのセッションを自動的にログに記録するためのラッパースクリプト

# 年月日-時分秒の形式で、セッションごとに一意なログファイル名を生成
LOG_FILE="${GEMINI_LOG}/gemini-session-$(date +'%Y%m%d-%H%M%S').log"

# ユーザーにセッションが記録されることを通知（任意）
echo "Gemini CLI session started. Log will be saved to: ${LOG_FILE}"

# scriptコマンドを使用してセッションを記録する
# -q: 開始・終了メッセージを抑制し、ログをクリーンに保つ
# -c: 指定したコマンド（gemini）を実行し、その終了とともに記録を終了する
# "$@" は、このラッパースクリプトに渡された全ての引数を、そのままgeminiコマンドに渡すための記述
script -q -c "gemini "$@"" "${LOG_FILE}"

# ユーザーにセッションが終了したことを通知（任意）
echo "Gemini CLI session ended."
