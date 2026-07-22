param(
    [string]$VBoxManagePath = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
    [string]$HostRedisUrl = "redis://localhost:6379/0",
    [string]$GuestRedisUrl = "redis://10.0.2.2:6379/0",
    [string]$TaskStream = ("logminer:agent_tasks:vbox_1h:" + (Get-Date -Format "yyyyMMddHHmmss")),
    [string]$Group = "logminer-intelligent-agents",
    [string]$RunId = ("redis-vbox-1h-" + (Get-Date -Format "yyyyMMddHHmmss")),
    [int]$DurationSec = 3600,
    [int]$DrainSec = 120,
    [int]$EnqueueIntervalSec = 15,
    [string]$DebianUser = "vboxuser",
    [string]$DebianPassword = "",
    [string]$UbuntuUser = "andy",
    [string]$UbuntuPassword = "",
    [string]$OutputJson = "data/processed/vbox_redis_1h_campaign.json",
    [string]$OutputMarkdown = "docs/memoire/tables/table_vbox_redis_1h_campaign.md"
)

$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param([string]$Label, [scriptblock]$Block)
    Write-Host "== $Label"
    & $Block
    if ($LASTEXITCODE -ne 0) {
        throw "$Label a echoue avec le code $LASTEXITCODE"
    }
}

function Copy-ToGuest {
    param(
        [string]$VmName,
        [string]$User,
        [string]$Password,
        [string]$HostPath,
        [string]$GuestPath
    )
    & $VBoxManagePath guestcontrol $VmName copyto `
        --username $User `
        --password="$Password" `
        $HostPath `
        $GuestPath
    if ($LASTEXITCODE -ne 0) {
        throw "Copie echouee vers $VmName : $GuestPath"
    }
}

function Start-VBoxWorker {
    param(
        [string]$VmName,
        [string]$User,
        [string]$Password,
        [string]$Command,
        [string]$StdoutPath,
        [string]$StderrPath
    )
    return Start-Job -ScriptBlock {
        param($VBoxManagePath, $VmName, $User, $Password, $Command, $StdoutPath, $StderrPath)
        & $VBoxManagePath guestcontrol $VmName run `
            --username $User `
            --password="$Password" `
            --exe /bin/bash `
            -- -lc $Command `
            *> $StdoutPath `
            2> $StderrPath
        exit $LASTEXITCODE
    } -ArgumentList $VBoxManagePath, $VmName, $User, $Password, $Command, $StdoutPath, $StderrPath
}

if (-not (Test-Path -LiteralPath $VBoxManagePath)) {
    throw "VBoxManage introuvable: $VBoxManagePath"
}
if (-not $DebianPassword -or -not $UbuntuPassword) {
    throw "Renseigner -DebianPassword et -UbuntuPassword."
}

Invoke-Checked "Redis ping" {
    docker exec logminer-redis redis-cli ping
}

foreach ($vm in @("Debian", "Ubuntu")) {
    $info = & $VBoxManagePath showvminfo $vm --machinereadable
    if ($LASTEXITCODE -ne 0) {
        throw "VM introuvable: $vm"
    }
    $runLevel = ($info | Select-String '^GuestAdditionsRunLevel=').ToString()
    $state = ($info | Select-String '^VMState=').ToString()
    Write-Host "$vm $state $runLevel"
    if ($state -notmatch '"running"' -or $runLevel -notmatch '=2') {
        throw "$vm n'est pas prete pour guestcontrol."
    }
}

$root = (Resolve-Path .).Path
$workerHostPath = Join-Path $root "scripts\logminer_intelligent_agent_worker.py"
$runtimeHostPath = Join-Path $root "src\logminer\agents\intelligent_runtime.py"
Copy-ToGuest -VmName Debian -User $DebianUser -Password $DebianPassword -HostPath $workerHostPath -GuestPath "/home/vboxuser/scripts/logminer_intelligent_agent_worker.py"
Copy-ToGuest -VmName Ubuntu -User $UbuntuUser -Password $UbuntuPassword -HostPath $workerHostPath -GuestPath "/home/andy/scripts/logminer_intelligent_agent_worker.py"
Copy-ToGuest -VmName Debian -User $DebianUser -Password $DebianPassword -HostPath $runtimeHostPath -GuestPath "/home/vboxuser/src/logminer/agents/intelligent_runtime.py"
Copy-ToGuest -VmName Ubuntu -User $UbuntuUser -Password $UbuntuPassword -HostPath $runtimeHostPath -GuestPath "/home/andy/src/logminer/agents/intelligent_runtime.py"

$workerDuration = [Math]::Max(60, $DurationSec + $DrainSec)
$debianCommand = "cd `$HOME && LOGMINER_REDIS_URL='$GuestRedisUrl' `$HOME/.venv-logminer/bin/python scripts/logminer_intelligent_agent_worker.py --redis-url '$GuestRedisUrl' --event-stream logminer:events --task-stream '$TaskStream' --group '$Group' --run-id '$RunId' --consumer debian-worker-1h --agent-id debian-worker-1h --duration-sec $workerDuration --max-parallel-tasks 1 --block-ms 1000 --claim-idle-ms 1000 --memory data/processed/debian-worker-1h-memory.json"
$ubuntuCommand = "cd `$HOME && LOGMINER_REDIS_URL='$GuestRedisUrl' python3 scripts/logminer_intelligent_agent_worker.py --redis-url '$GuestRedisUrl' --event-stream logminer:events --task-stream '$TaskStream' --group '$Group' --run-id '$RunId' --consumer ubuntu-worker-1h --agent-id ubuntu-worker-1h --duration-sec $workerDuration --max-parallel-tasks 1 --block-ms 1000 --claim-idle-ms 1000 --memory data/processed/ubuntu-worker-1h-memory.json"

$logDir = Join-Path $root "data\processed\vbox_1h_worker_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$debianStdout = Join-Path $logDir "$RunId-debian.out.log"
$debianStderr = Join-Path $logDir "$RunId-debian.err.log"
$ubuntuStdout = Join-Path $logDir "$RunId-ubuntu.out.log"
$ubuntuStderr = Join-Path $logDir "$RunId-ubuntu.err.log"

$started = Get-Date
$deadline = $started.AddSeconds([Math]::Max(60, $DurationSec))
$iterations = 0

Write-Host "== Campagne multi-VM 1h"
Write-Host "RunId=$RunId"
Write-Host "TaskStream=$TaskStream"
Write-Host "Debut=$($started.ToString('s')) Fin cible=$($deadline.ToString('s'))"

$debianProcess = Start-VBoxWorker -VmName Debian -User $DebianUser -Password $DebianPassword -Command $debianCommand -StdoutPath $debianStdout -StderrPath $debianStderr
$ubuntuProcess = Start-VBoxWorker -VmName Ubuntu -User $UbuntuUser -Password $UbuntuPassword -Command $ubuntuCommand -StdoutPath $ubuntuStdout -StderrPath $ubuntuStderr
Start-Sleep -Seconds 5

while ((Get-Date) -lt $deadline) {
    $iterations++
    Invoke-Checked "Enfilement iteration $iterations" {
        python scripts\logminer_intelligent_agent_worker.py `
            --redis-url $HostRedisUrl `
            --event-stream logminer:events `
            --task-stream $TaskStream `
            --group $Group `
            --run-id $RunId `
            --consumer windows-seeder-1h `
            --agent-id windows-seeder-1h `
            --enqueue-demo `
            --enqueue-only `
            --demo-input examples/windows_event_sample.xml
    }
    Start-Sleep -Seconds ([Math]::Max(1, $EnqueueIntervalSec))
}

Write-Host "== Drain des workers pendant $DrainSec secondes"
Start-Sleep -Seconds ([Math]::Max(1, $DrainSec))

foreach ($proc in @($debianProcess, $ubuntuProcess)) {
    if ($proc.State -eq "Running") {
        Write-Host "Attente worker job $($proc.Id)"
        Wait-Job -Job $proc -Timeout 30 | Out-Null
    }
}

$summaryScript = @"
import json
import sys
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, r"src\logminer")
from agents.bus import RedisMessageBus

run_id = "$RunId"
task_stream = "$TaskStream"
group = "$Group"
started = "$($started.ToUniversalTime().ToString("o"))"
finished = datetime.now(timezone.utc).isoformat()
bus = RedisMessageBus(url="$HostRedisUrl", stream="logminer:events", run_id=run_id)
messages = bus.read(run_id=run_id, count=200000)
completed = [m for m in messages if m.message_type == "agent.task.completed"]
failed = [m for m in messages if m.message_type == "agent.task.failed"]
by_agent = Counter(m.source for m in completed)
by_type = Counter((m.payload.get("result") or {}).get("task_type", "") for m in completed)
unique_tasks = {(m.payload.get("result") or {}).get("task_id", "") for m in completed}
pending_raw = bus.client.xpending(task_stream, group)
pending = int(pending_raw.get("pending", 0)) if isinstance(pending_raw, dict) else 0
stream_len = int(bus.client.xlen(task_stream))
summary = {
    "run_id": run_id,
    "task_stream": task_stream,
    "group": group,
    "started_at": started,
    "finished_at": finished,
    "target_duration_sec": $DurationSec,
    "drain_sec": $DrainSec,
    "enqueue_interval_sec": $EnqueueIntervalSec,
    "iterations": $iterations,
    "tasks_enqueued": stream_len,
    "tasks_completed": len(completed),
    "unique_tasks_completed": len([task_id for task_id in unique_tasks if task_id]),
    "tasks_failed": len(failed),
    "pending_after": pending,
    "debian_job_state": "$($debianProcess.State)",
    "ubuntu_job_state": "$($ubuntuProcess.State)",
    "by_agent": dict(by_agent),
    "by_type": dict(by_type),
    "worker_logs": {
        "debian_stdout": r"$debianStdout",
        "debian_stderr": r"$debianStderr",
        "ubuntu_stdout": r"$ubuntuStdout",
        "ubuntu_stderr": r"$ubuntuStderr",
    },
}
Path("$OutputJson").parent.mkdir(parents=True, exist_ok=True)
Path("$OutputJson").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
md = [
    "| Indicateur | Valeur |",
    "| --- | ---: |",
    f"| Duree cible | {summary['target_duration_sec']} s |",
    f"| Drain final | {summary['drain_sec']} s |",
    f"| Iterations d'enfilement | {summary['iterations']} |",
    f"| Taches enfilees | {summary['tasks_enqueued']} |",
    f"| Taches terminees | {summary['tasks_completed']} |",
    f"| Taches uniques terminees | {summary['unique_tasks_completed']} |",
    f"| Taches echouees | {summary['tasks_failed']} |",
    f"| Pending final Redis | {summary['pending_after']} |",
    f"| Taches Debian | {summary['by_agent'].get('debian-worker-1h', 0)} |",
    f"| Taches Ubuntu | {summary['by_agent'].get('ubuntu-worker-1h', 0)} |",
]
Path("$OutputMarkdown").parent.mkdir(parents=True, exist_ok=True)
Path("$OutputMarkdown").write_text("\n".join(md) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
"@

python -c $summaryScript
if ($LASTEXITCODE -ne 0) {
    throw "Synthese de campagne 1h echouee."
}
