# 以「任务计划程序」每天在固定时间运行选座脚本（需以管理员身份运行 PowerShell 一次）。
# 使用前请修改下面三行。

$PythonExe = "python"   # 或完整路径，如 "C:\Users\你\AppData\Local\Programs\Python\Python312\python.exe"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$OpenSeat   = Join-Path $ScriptDir "open_seat.py"

# 每天触发的时间（本机时区）；ExtraArgs 传给 open_seat.py
$DailyAtLocal = "00:00:05"
# 已用 Chrome 插件自动登录时可去掉 --copy-id，仅打开选座页。
# 测试当天页面可用：--today --area 3
$ExtraArgs = "--tomorrow --area 3"

# ---------------------------------------------------------------------------

$taskName = "FudanLibrarySeatOpen"
$argLine = "`"$OpenSeat`" $ExtraArgs"
$action = New-ScheduledTaskAction -Execute $PythonExe -Argument $argLine -WorkingDirectory $ScriptDir
$trigger = New-ScheduledTaskTrigger -Daily -At $DailyAtLocal
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force
Write-Host "已注册计划任务: $taskName  每天 $DailyAtLocal 执行。"
Write-Host "在「任务计划程序」里可禁用/删除/改触发器。"
