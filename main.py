import os
import sys
import time

# --- 定数 ---
SLEEP_INTERVAL = 5
PUBLIC_INBOX_NAME = '_public'
DONE_FOLDER_NAME = 'done'


def setup():
    """環境変数を読み込み、初期ディレクトリを設定する。"""
    # AGENT_ID を読み込む
    my_agent_id = os.getenv('AGENT_ID')
    if not my_agent_id:
        print("エラー: 環境変数 AGENT_ID が設定されていません。")
        sys.exit(1)

    # メッセージングのルートディレクトリを読み込む
    message_root_dir = os.getenv('AGENT_MESSAGE_DIR')
    if not message_root_dir:
        print("エラー: 環境変数 AGENT_MESSAGE_DIR が設定されていません。")
        sys.exit(1)

    # 自分のホームディレクトリのパスを組み立てる
    target_dir = os.path.join(message_root_dir, my_agent_id)

    try:
        os.makedirs(target_dir, exist_ok=True)
        print(f"エージェント {my_agent_id} のホームディレクトリを確認: {target_dir}")

        public_inbox_dir = os.path.join(target_dir, PUBLIC_INBOX_NAME)
        public_done_path = os.path.join(public_inbox_dir, DONE_FOLDER_NAME)
        os.makedirs(public_done_path, exist_ok=True)
        print(f"標準受信フォルダを確認: {public_inbox_dir}")

    except OSError as e:
        print(f"エラー: ディレクトリの作成に失敗しました - {e}")
        sys.exit(1)

    return target_dir, my_agent_id, message_root_dir


def scan_and_leave_footprints(my_agent_id, message_root_dir):
    """他のエージェントを検出し、足跡を残す。"""
    try:
        for entity_name in os.listdir(message_root_dir):
            if entity_name == my_agent_id:
                continue

            entity_path = os.path.join(message_root_dir, entity_name)
            if os.path.isdir(entity_path):
                footprint_path = os.path.join(
                    entity_path, my_agent_id, DONE_FOLDER_NAME)
                if not os.path.exists(footprint_path):
                    os.makedirs(footprint_path, exist_ok=True)
                    print(f"エージェント {entity_name} を認識。足跡を作成。")
    except Exception as e:
        print(f"警告: 他エージェントのスキャン中にエラー: {e}")


def collect_new_messages(target_dir, processed_files):
    """新しいメッセージを収集し、リストとして返す。"""
    new_messages = []
    try:
        for sender_id in os.listdir(target_dir):
            sender_dir_path = os.path.join(target_dir, sender_id)
            if not os.path.isdir(sender_dir_path):
                continue

            for filename in os.listdir(sender_dir_path):
                # 'done' ディレクトリ自体は処理対象外
                if filename == DONE_FOLDER_NAME:
                    continue

                if not filename.endswith('.md'):
                    continue

                filepath = os.path.join(sender_dir_path, filename)
                if filepath not in (
                    processed_files and os.path.isfile(filepath)
                ):
                    try:
                        mtime = os.path.getmtime(filepath)
                        new_messages.append((filepath, mtime))
                    except FileNotFoundError:
                        continue
    except Exception as e:
        print(f"警告: メッセージ収集中にエラー: {e}")
    return new_messages


def process_message(filepath, mtime):
    """単一のメッセージを処理し、移動する。"""
    try:
        sender_id = os.path.basename(os.path.dirname(filepath))
        filename = os.path.basename(filepath)

        print("\n[処理開始]--------------------------------")
        print(f"  送信者: {sender_id}")
        print(f"  ファイル: {filename}")
        print(f"  受信時刻: {time.ctime(mtime)}")
        print("----------------------------------------")
        with open(filepath, 'r', encoding='utf-8') as f:
            print(f.read())
        print("----------------------------------------[処理完了]")

        # doneディレクトリへ移動
        done_dir = os.path.join(os.path.dirname(filepath), DONE_FOLDER_NAME)
        os.makedirs(done_dir, exist_ok=True)
        new_filepath = os.path.join(done_dir, filename)
        os.rename(filepath, new_filepath)
        print(f"  => 処理済みとして {new_filepath} へ移動しました。")

    except Exception as e:
        print(f"エラー: メッセージ {filepath} の処理中にエラー: {e}")


def main():
    """メインの監視処理を実行します。"""
    target_dir, my_agent_id, message_root_dir = setup()
    processed_files = set()
    print("メッセージングシステムの監視を開始します...")

    try:
        while True:
            scan_and_leave_footprints(my_agent_id, message_root_dir)

            messages_to_process = collect_new_messages(
                target_dir, processed_files)

            if messages_to_process:
                messages_to_process.sort(key=lambda item: item[1])
                print(f"\n--- {len(messages_to_process)}件のメッセージが待機しています ---")

                for filepath, mtime in messages_to_process:
                    process_message(filepath, mtime)
                    processed_files.add(filepath)  # 元のパスを処理済みとして記録

                print("--- 全ての新規メッセージの処理が完了しました ---")

            time.sleep(SLEEP_INTERVAL)
    except KeyboardInterrupt:
        print("\n監視を終了します。")
        sys.exit(0)


if __name__ == "__main__":
    main()
