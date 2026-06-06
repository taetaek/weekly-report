# Windows 작업 스케줄러 등록 - 매주 월요일 오전 8시 자동 실행
# 관리자 권한으로 실행하세요: Right-click → "관리자 권한으로 실행"

$TaskName = "WeeklyCalendarReport"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonPath = (Get-Command python).Source
$ScriptPath = Join-Path $ScriptDir "main.py"
$LogPath = Join-Path $ScriptDir "logs\run.log"

# 로그 디렉터리 생성
New-Item -ItemType Directory -Path (Join-Path $ScriptDir "logs") -Force | Out-Null

# 기존 태스크 제거
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# 트리거: 매주 월요일 08:00
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "08:00AM"

# 실행 명령: python main.py >> logs\run.log 2>&1
$Action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "`"$ScriptPath`"" `
    -WorkingDirectory $ScriptDir

# 설정: 네트워크 연결 시 실행, 최대 30분 실행
$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
    -RunOnlyIfNetworkAvailable `
    -StartWhenAvailable

# 현재 사용자 계정으로 실행 (로그인 여부 무관)
$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType InteractiveToken `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName $TaskName `
    -Trigger $Trigger `
    -Action $Action `
    -Settings $Settings `
    -Principal $Principal `
    -Description "매주 월요일 오전 8시 Google Calendar 분석 후 카카오톡 알림 전송"

Write-Host ""
Write-Host "✅ 작업 스케줄러 등록 완료!" -ForegroundColor Green
Write-Host "   이름: $TaskName"
Write-Host "   실행: 매주 월요일 08:00"
Write-Host "   스크립트: $ScriptPath"
Write-Host ""
Write-Host "즉시 테스트 실행:"
Write-Host "  cd `"$ScriptDir`""
Write-Host "  python main.py --dry-run"
