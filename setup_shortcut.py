"""
在 Windows 当前用户桌面创建「复旦图书馆选座」快捷方式，双击即运行 open_seat.py。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    launcher = script_dir / "open_seat.py"
    desktop = Path.home() / "Desktop"
    if not desktop.is_dir():
        # 中文系统常见「桌面」文件夹名
        desktop_cn = Path.home() / "桌面"
        desktop = desktop_cn if desktop_cn.is_dir() else desktop

    lnk = desktop / "复旦图书馆选座.lnk"
    py = Path(sys.executable)
    pythonw = py.with_name("pythonw.exe")
    target = pythonw if pythonw.is_file() else py

    # 默认：打开页面；需要一键复制学号时把下面改成：f'\\"{launcher}\\" --copy-id'
    arguments = f'"{launcher}"'
    ps = f"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{lnk.as_posix().replace("'", "''")}')
$s.TargetPath = '{target.as_posix().replace("'", "''")}'
$s.Arguments = '{arguments.replace("'", "''")}'
$s.WorkingDirectory = '{script_dir.as_posix().replace("'", "''")}'
$s.WindowStyle = 7
$s.Description = '复旦图书馆座位预约 H5'
$s.Save()
"""
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
        check=True,
    )
    print(f"已创建快捷方式: {lnk}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
