import libtmux
import yaml
import pathlib
import time
import shutil


def setup_agent_directories(config: dict):
    """
    Sets up agent directories based on the provided configuration.
    It copies template directories to the destination directory.
    """
    print("--- エージェントディレクトリのセットアップを開始します ---")
    agents = config.get("agents", {})
    source_dir_path = config.get("source_dir")
    destination_dir_path = config.get("destination_dir")

    if not source_dir_path or not destination_dir_path:
        print(
            "エラー: 設定ファイルに 'source_dir' または 'destination_dir' が見つかりません。"
        )
        return

    source_dir = pathlib.Path(source_dir_path)
    destination_dir = pathlib.Path(destination_dir_path)

    if not source_dir.is_dir():
        print(f"エラー: ソースディレクトリ '{source_dir}' が見つかりません。")
        return

    if not destination_dir.exists():
        print(f"デスティネーションディレクトリ '{destination_dir}' を作成します。")
        destination_dir.mkdir(parents=True)

    for agent_name, agent_config in agents.items():
        template_name = agent_config.get("template")
        # デフォルトは False（上書きしない）
        overwrite = agent_config.get("overwrite", False)

        if not template_name:
            print(
                f"警告: エージェント '{agent_name}' のテンプレートが指定されていません。スキップします。"
            )
            continue

        destination_path = destination_dir / agent_name

        print(
            f"エージェント '{agent_name}' をセットアップしています... (Overwrite: {overwrite})"
        )

        template_path = None
        try:
            # テンプレート名をディレクトリとして再帰的に検索し、最もパスが短いものを選択します。
            # これにより、トップレベルに近いテンプレートが優先されます。
            found_dirs = [
                p for p in source_dir.rglob(template_name) if p.is_dir()
            ]
            if found_dirs:
                template_path = min(found_dirs, key=lambda p: len(str(p)))
                if len(found_dirs) > 1:
                    print(
                        f"  - 警告: テンプレート '{template_name}' が複数見つかりました。"
                        f"最短パスを選択します: {template_path}"
                    )

        except OSError as e:
            print(f"  - テンプレート検索中にエラーが発生しました: {e}")

        if template_path and template_path.is_dir():
            if destination_path.exists():
                if not overwrite:
                    print(
                        f"  - 既存のディレクトリ '{destination_path}' が存在するためスキップします。"
                    )
                    continue

                print(f"  - 既存のディレクトリ '{destination_path}' を削除します。")
                shutil.rmtree(destination_path)

            print(
                f"  - テンプレート '{template_name}' を '{template_path}' からコピーします。"
            )
            shutil.copytree(template_path, destination_path)
            print(f"  - '{destination_path}' へのコピーが完了しました。"
            )
        else:
            print(
                f"  - 警告: テンプレートディレクトリ '{template_name}' が '{source_dir}' 内に見つかりませんでした。"
            )
    print("--- エージェントディレクトリのセットアップが完了しました ---")


def _find_active_pane(window, active_agent_name, layout_grid, panes_grid):
    for r, row in enumerate(layout_grid):
        for c, agent_name in enumerate(row):
            if agent_name == active_agent_name:
                try:
                    return panes_grid[r][c]
                except IndexError:
                    print(
                        f"警告: panes_gridのインデックス[{r}][{c}]が無効です。"
                        "ペインの結合処理に問題がある可能性があります。"
                    )
                    return None
    return None


def main():
    config_path = pathlib.Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Setup agent directories before creating tmux session
    setup_agent_directories(config)

    session_name = config.get("session_name", "default_session")
    active_agent_name = config.get("active_agent", "")
    layout_grid = config.get("layout_grid", [])
    dest_dir = config.get("destination_dir", "/app/works")

    server = libtmux.Server()
    if server.find_where({"session_name": session_name}):
        server.kill_session(session_name)

    print(f"セッション '{session_name}' をグリッドレイアウトで作成します...")

    # --- 1. Create Even Grid ---
    first_agent_name = layout_grid[0][0]
    start_dir = f"{dest_dir}/{first_agent_name}" \
        if first_agent_name != "blank" else dest_dir
    session = server.new_session(
        session_name=session_name, attach=False,
        window_name="Layout-Grid", start_directory=start_dir
    )
    window = session.windows[0]
    panes_grid = [[window.panes[0]]]

    for col_idx, agent_name in enumerate(layout_grid[0][1:]):
        panes_grid[0][-1].cmd('split-window', '-h', '-c', start_dir)
        panes_grid[0].append(window.panes[-1])

    for row_idx, row_list in enumerate(layout_grid[1:]):
        new_row_panes = []
        for col_idx, agent_name in enumerate(row_list):
            target_pane_above = panes_grid[row_idx][col_idx]
            start_dir = f"{dest_dir}/{agent_name}" \
                if agent_name != "blank" else dest_dir
            target_pane_above.cmd('split-window', '-v', '-c', start_dir)
            new_row_panes.append(window.panes[-1])
        panes_grid.append(new_row_panes)

    # --- 2. Join Panes (Final Attempt) ---
    print("--- ペイン結合デバッグ情報 ---")
    time.sleep(2)

    # Horizontal joins
    for r, row_list in enumerate(layout_grid):
        for c in range(len(row_list) - 1, 0, -1):
            if row_list[c] == row_list[c-1] and row_list[c] != "blank":
                source_pane = panes_grid[r][c-1]
                target_pane = panes_grid[r][c]
                print(
                    f"DEBUG: Joining pane {source_pane.pane_id} into "
                    f"{target_pane.pane_id}"
                )
                session.cmd(
                    'join-pane', '-h', '-s',
                    source_pane.pane_id, '-t', target_pane.pane_id
                )
                time.sleep(0.5)

    print("---------------------------")

    # --- 3. Activate and Attach ---
    if active_agent_name:
        active_pane = _find_active_pane(
            window, active_agent_name, layout_grid, panes_grid
        )
        if active_pane:
            print(
                f"アクティブエージェント '{active_agent_name}' (Pane: "
                f"{active_pane.pane_id}) を選択します。"
            )
            window.select_pane(active_pane.pane_id)
        else:
            print(
                f"警告: アクティブエージェント '{active_agent_name}' がレイアウトに見つかりませんでした。"
            )

    print("セッションの準備ができました。アタッチします...")
    session.attach_session()


if __name__ == "__main__":
    main()