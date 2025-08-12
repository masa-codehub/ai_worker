import libtmux
import yaml
import pathlib
import time


def main():
    config_path = pathlib.Path(__file__).parent / "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

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
    start_dir = f"{dest_dir}/{first_agent_name}" if first_agent_name != "blank" else dest_dir
    session = server.new_session(session_name=session_name, attach=False,
                                 window_name="Layout-Grid", start_directory=start_dir)
    window = session.windows[0]
    panes_grid = [[window.panes[0]]]

    for col_idx, agent_name in enumerate(layout_grid[0][1:]):
        panes_grid[0][-1].cmd('split-window', '-h', '-c', start_dir)
        panes_grid[0].append(window.panes[-1])

    for row_idx, row_list in enumerate(layout_grid[1:]):
        new_row_panes = []
        for col_idx, agent_name in enumerate(row_list):
            target_pane_above = panes_grid[row_idx][col_idx]
            start_dir = f"{dest_dir}/{agent_name}" if agent_name != "blank" else dest_dir
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
                # Join c-1 into c, then the layout logic might be simpler.
                source_pane = panes_grid[r][c-1]
                target_pane = panes_grid[r][c]
                print(
                    f"DEBUG: Joining pane {source_pane.pane_id} into {target_pane.pane_id}")
                # Use session.cmd and reversed source/target as a final attempt
                session.cmd('join-pane', '-h', '-s',
                            source_pane.pane_id, '-t', target_pane.pane_id)
                time.sleep(0.5)

    print("---------------------------")

    # --- 3. Activate and Attach ---
    if active_agent_name:
        # ... (omitted for brevity, same as before)
        pass

    print("セッションの準備ができました。アタッチします...")
    session.attach_session()


if __name__ == "__main__":
    main()
