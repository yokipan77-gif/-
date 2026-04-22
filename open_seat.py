"""
复旦图书馆座位预约 — 到点用默认浏览器打开选座 H5（URL 含日期与 area）。

用法：
  python open_seat.py --tomorrow --area 3
  python open_seat.py --today --area 3
  python open_seat.py --fire-at "2026-04-23 00:00:05" --tomorrow --area 3

若 Chrome 已用插件自动填学号/密码，可不再使用 .env，也不加 --copy-id。

定点打开（推荐）：Windows「任务计划程序」在放座时刻执行本脚本，见 register_daily_task.ps1。
本脚本不自动点击座位、不调图书馆后台接口；抢座仍依赖你在页面里手动选座（插件只帮你登录）。

可选：仍支持 .env + --copy-id / --copy-password（见 config.example.env），勿把密码写进代码或外传。

桌面快捷方式：
  python setup_shortcut.py
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import webbrowser
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

# 预约系统 H5 基址（hash 路由）
BASE = "https://libsrs.fudan.edu.cn/h5/index.html"

# 默认区域 ID：你提供的链接里是 area=3。
# 若打开后不是「文科馆 · 四层」，请在浏览器里手动点一次目标楼层，
# 看地址栏 #/seat-select?...area= 的数字，把 DEFAULT_AREA_ID 改成该值。
DEFAULT_AREA_ID = "3"


def _parse_env_file(path: Path) -> dict[str, str]:
    """读取 KEY=VALUE 行（支持 UTF-8 BOM），不依赖 python-dotenv。"""
    out: dict[str, str] = {}
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except OSError:
        return out
    for line in raw.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if "=" not in s:
            continue
        key, _, val = s.partition("=")
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        if key:
            out[key] = val
    return out


def _load_env() -> None:
    """
    合并多个位置的 .env，后者覆盖前者：
    1) 用户桌面 Desktop 或「桌面」
    2) 本脚本所在目录（fudan_lib_seat）

    很多人把 .env 建在桌面，而旧版只读脚本旁，会导致学号密码读不到。
    """
    root = Path(__file__).resolve().parent
    home = Path.home()
    candidates = [
        home / "Desktop" / ".env",
        home / "桌面" / ".env",
        root / ".env",
    ]
    merged: dict[str, str] = {}
    for p in candidates:
        if p.is_file():
            merged.update(_parse_env_file(p))
    for k, v in merged.items():
        os.environ[k] = v


def build_seat_select_url(d: date, area_id: str) -> str:
    q = urlencode({"date": d.isoformat(), "area": area_id})
    return f"{BASE}#/seat-select?{q}"


def parse_fire_at_local(s: str) -> datetime:
    """解析本机本地时间的触发时刻（naive）。支持 2026-04-23T00:00:05 或 2026-04-23 00:00:05。"""
    t = s.strip().replace("Z", "")
    if "T" not in t and len(t) == 10:
        raise SystemExit("--fire-at 需包含日期和时间，例如 2026-04-23 00:00:05")
    try:
        return datetime.fromisoformat(t)
    except ValueError as e:
        raise SystemExit(f"无法解析 --fire-at: {s!r}，请用 YYYY-MM-DD HH:MM:SS") from e


def sleep_until(target: datetime) -> None:
    """睡到 target（本机 naive 本地时间），末尾用短间隔提高触发精度。"""
    if target.tzinfo is not None:
        raise SystemExit("--fire-at 请使用不带时区的本机时间")
    while True:
        now = datetime.now()
        sec = (target - now).total_seconds()
        if sec <= 0:
            return
        if sec > 5:
            time.sleep(min(30.0, sec - 2.0))
        elif sec > 0.08:
            time.sleep(sec / 2.0)
        else:
            time.sleep(sec)


def open_seat_flow(
    *,
    target: date,
    area_id: str,
    copy_id: bool,
    copy_password: bool,
    copy_id_seconds_before: int,
    fire_at: datetime | None,
) -> int:
    url = build_seat_select_url(target, str(area_id))
    sid = os.environ.get("FUDAN_STUDENT_ID", "").strip()
    pwd = os.environ.get("FUDAN_LIB_PASSWORD", "").strip()

    def copy_id_once() -> None:
        if copy_id and sid:
            if copy_to_clipboard_windows(sid):
                print("已复制学号到剪贴板。")
        elif copy_id and not sid:
            print("未设置 FUDAN_STUDENT_ID（.env），跳过复制学号。", file=sys.stderr)

    def open_browser() -> None:
        opened = webbrowser.open(url)
        if not opened:
            print(url)
            print("未能唤起默认浏览器，请手动复制上方链接。", file=sys.stderr)
        else:
            print(f"已打开: {url}")

    if fire_at is not None:
        pre = max(0, int(copy_id_seconds_before))
        if pre > 0 and copy_id:
            pre_at = fire_at - timedelta(seconds=pre)
            print(f"等待至 {pre_at:%Y-%m-%d %H:%M:%S} 复制学号，{fire_at:%Y-%m-%d %H:%M:%S} 打开页面…")
            sleep_until(pre_at)
            copy_id_once()
            sleep_until(fire_at)
        else:
            print(f"等待至 {fire_at:%Y-%m-%d %H:%M:%S} …")
            sleep_until(fire_at)
            if copy_id:
                copy_id_once()
        open_browser()
    else:
        if copy_id:
            copy_id_once()
        open_browser()

    if copy_password:
        if pwd:
            if copy_to_clipboard_windows(pwd):
                print("已复制密码到剪贴板（请及时粘贴并注意剪贴板安全）。")
        else:
            print("未设置 FUDAN_LIB_PASSWORD，跳过复制密码。", file=sys.stderr)

    return 0


def copy_to_clipboard_windows(text: str) -> bool:
    if not text:
        return False
    # PowerShell 单引号字符串：用 '' 表示字面 '
    safe = str(text).replace("'", "''")
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", f"Set-Clipboard -Value '{safe}'"],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def main() -> int:
    _load_env()

    parser = argparse.ArgumentParser(description="打开复旦图书馆选座 H5")
    when = parser.add_mutually_exclusive_group()
    when.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="预约日期为指定一天",
    )
    when.add_argument(
        "--tomorrow",
        action="store_true",
        help="预约日期为明天（零点抢次日常用）",
    )
    when.add_argument(
        "--today",
        action="store_true",
        help="预约日期为今天（与不加 --date/--tomorrow 等价，便于测试）",
    )
    parser.add_argument(
        "--area",
        default=os.environ.get("FUDAN_SEAT_AREA_ID", DEFAULT_AREA_ID),
        help="区域 ID（URL 中 area=），默认从环境变量 FUDAN_SEAT_AREA_ID 或脚本内常量读取",
    )
    parser.add_argument(
        "--copy-id",
        action="store_true",
        help="打开浏览器前把学号复制到剪贴板（登录页粘贴）",
    )
    parser.add_argument(
        "--copy-password",
        action="store_true",
        help="把密码复制到剪贴板（慎用：剪贴板可被其他程序读取）",
    )
    parser.add_argument(
        "--fire-at",
        metavar="TIME",
        help='到本机该时刻再打开页面，例如 "2026-04-23 00:00:05"（进程会一直保持到该时刻）',
    )
    parser.add_argument(
        "--copy-id-seconds-before",
        type=int,
        default=3,
        metavar="N",
        help="与 --fire-at 和 --copy-id 同用时：提前 N 秒复制学号，默认 3；设为 0 表示与打开页面同一时刻复制",
    )
    args = parser.parse_args()

    if args.date:
        target = date.fromisoformat(args.date)
    elif args.tomorrow:
        target = date.today() + timedelta(days=1)
    else:
        # --today 或未指定：均为「今天」
        target = date.today()

    fire_at: datetime | None = parse_fire_at_local(args.fire_at) if args.fire_at else None

    return open_seat_flow(
        target=target,
        area_id=str(args.area),
        copy_id=bool(args.copy_id),
        copy_password=bool(args.copy_password),
        copy_id_seconds_before=int(args.copy_id_seconds_before),
        fire_at=fire_at,
    )


if __name__ == "__main__":
    raise SystemExit(main())
