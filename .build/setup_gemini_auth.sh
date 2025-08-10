#!/bin/bash

# =============================================================================
# Google Cloud & Gemini Code Assist 認証設定スクリプト
# =============================================================================
#
# 概要:
#   このスクリプトは、gcloud CLI を使用して Gemini Code Assist を
#   利用するための認証とプロジェクト設定を対話的に行います。
#
# 使い方:
#   1. このファイルを `setup_gemini_auth.sh` として保存します。
#   2. ターミナルで実行権限を付与します: `chmod +x setup_gemini_auth.sh`
#   3. スクリプトを実行します: `./setup_gemini_auth.sh`
#   4. 画面の指示に従って操作してください。
#
# =============================================================================

# スクリプトの途中でエラーが発生した場合、処理を中断する
set -e

# --- メイン処理 ---

echo "--- Gemini Code Assist 認証設定を開始します ---"
echo ""

# 1. プロジェクトIDの入力を求める
read -p "設定する Google Cloud のプロジェクトIDを入力してください (例: geminicodeassist-467712): " GCP_PROJECT_ID

if [ -z "$GCP_PROJECT_ID" ]; then
  echo "エラー: プロジェクトIDが入力されませんでした。処理を中断します。"
  exit 1
fi

echo ""
echo "------------------------------------------------------------"
echo "ステップ1/4: Googleアカウントでのログイン"
echo "------------------------------------------------------------"
echo "ブラウザが開き、認証が求められます。"
echo "Gemini Code Assist のライセンスが付与されているGoogleアカウントを選択してください。"
read -p "準備ができたらEnterキーを押して次に進んでください..."
gcloud auth login

echo "✅ ステップ1 完了"
echo ""


echo "------------------------------------------------------------"
echo "ステップ2/4: アプリケーションのデフォルト認証情報の設定"
echo "------------------------------------------------------------"
echo "再度ブラウザでの認証が求められる場合があります。"
read -p "準備ができたらEnterキーを押して次に進んでください..."
gcloud auth application-default login

echo "✅ ステップ2 完了"
echo ""


echo "------------------------------------------------------------"
echo "ステップ3/4: CLIの操作対象プロジェクトの設定"
echo "------------------------------------------------------------"
echo "プロジェクト [ $GCP_PROJECT_ID ] を設定します..."
gcloud config set project "$GCP_PROJECT_ID"

echo "✅ ステップ3 完了"
echo ""


echo "------------------------------------------------------------"
echo "ステップ4/4: APIの課金・クォータ用プロジェクトの設定"
echo "------------------------------------------------------------"
echo "プロジェクト [ $GCP_PROJECT_ID ] を設定します..."
gcloud auth application-default set-quota-project "$GCP_PROJECT_ID"

echo "✅ ステップ4 完了"
echo ""


echo "============================================================"
echo "🎉 すべての認証設定が正常に完了しました！"
echo "============================================================"
echo ""
echo "設定内容の確認:"
echo "・アクティブなプロジェクト: $(gcloud config get-value project)"

# ADCファイルのパスを取得（OSによって異なる場合があるため動的に）
ADC_PATH=$(gcloud info --format='value(config.paths.application_default_credentials)')
if [ -f "$ADC_PATH" ]; then
  echo "・クォータプロジェクト:   $(grep 'quota_project_id' "$ADC_PATH" | sed 's/.*: "//;s/".*//')"
else
  echo "・クォータプロジェクト:   確認できませんでした。"
fi
echo ""
echo "これでGeminiを利用する準備が整いました。"