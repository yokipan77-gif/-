# fudan_lib_seat

在指定时间用系统默认浏览器打开复旦大学图书馆座位预约 H5（`libsrs.fudan.edu.cn`）的选座页，支持 Windows 桌面快捷方式与「任务计划程序」定时触发。

**说明**：本项目为个人学习/便利工具，与复旦大学官方无关；不调用图书馆后台接口，不自动占座；请遵守图书馆使用规则，预约座位后请按时签到学习。

## 功能

- 按「今天 / 明天 / 指定日期」与 `area` 拼接选座链接并打开
- 可选 `--fire-at` 在本机时刻再打开（进程会等待到该时刻）
- 可选从 `.env` 读学号并复制到剪贴板（若你更习惯用 Chrome 插件登录，可不用 `.env`）
- `setup_shortcut.py`：生成桌面快捷方式
- `register_daily_task.ps1`：注册 Windows 每日计划任务（需自行修改时间与参数）
## 运行示例
<img width="900" height="900" alt="ScreenShot_2026-04-22_135632_812" src="https://github.com/user-attachments/assets/468282cb-133b-4923-ab66-d86644a3df92" />




## 环境

- Windows（剪贴板与计划任务脚本针对 PowerShell）
- Python 3.9+（标准库即可；未使用第三方依赖）

## 快速使用

```bat
cd fudan_lib_seat
python open_seat.py --tomorrow --area 3
python open_seat.py --today --area 3
python open_seat.py --tomorrow --area 3 --fire-at "2026-04-23 00:00:05"
```

复制 `config.example.env` 为 `.env` 仅在需要 `--copy-id` / `--copy-password` 时使用。**切勿**将 `.env` 提交到 Git（已在 `.gitignore` 中忽略）。

## 许可证

MIT（见 `LICENSE`）。你可按需要改为其它许可证。
"# -" 

# fudan_lib_seat

[![Release](https://img.shields.io/github/v/release/yokipan77-gif/fudan-lib-seat?sort=semver)](https://github.com/yokipan77-gif/fudan-lib-seat/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/yokipan77-gif/fudan-lib-seat/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Repo](https://img.shields.io/badge/GitHub-fudan--lib--seat-black?logo=github)](https://github.com/yokipan77-gif/fudan-lib-seat)
