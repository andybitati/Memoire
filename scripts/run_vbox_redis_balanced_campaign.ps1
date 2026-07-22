param(
    [string]$VBoxManagePath = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
    [string]$HostRedisUrl = "redis://localhost:6379/0",
    [string]$GuestRedisUrl = "redis://10.0.2.2:6379/0",
    [string]$TaskStream = ("logminer:agent_tasks:vbox_balanced:" + (Get-Date -Format "yyyyMMddHHmmss")),
    [string]$Group = "logminer-intelligent-agents",
    [string]$RunId = ("redis-vbox-balanced-" + (Get-Date -Format "yyyyMMddHHmmss")),
    [int]$Batches = 4,
    [int]$CyclesPerWorker = 6,
    [string]$DebianUser = "vboxuser",
    [string]$DebianPassword = "",
    [string]$UbuntuUser = "andy",
    [string]$UbuntuPassword = "",
    [string]$OutputJson = "data/processed/vbox_redis_balanced_campaign.json",
    [string]$OutputMarkdown = "docs/memoire/tables/table_vbox_redis_balanced_campaign.md"
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

function Invoke-VBoxGuest {
    param(
        [string]$VmName,
        [string]$User,
        [string]$Password,
        [string]$Command
    )
    & $VBoxManagePath guestcontrol $VmName run `
        --username $User `
        --password="$Password" `
        --exe /bin/bash `
        -- -lc $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Commande invitee echouee sur $VmName"
    }
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

for ($i = 1; $i -le [Math]::Max(1, $Batches); $i++) {
    Invoke-Checked "Enfilement batch $i" {
        python scripts\logminer_intelligent_agent_worker.py `
            --redis-url $HostRedisUrl `
            --event-stream logminer:events `
            --task-stream $TaskStream `
            --group $Group `
            --run-id $RunId `
            --consumer windows-seeder `
            --agent-id windows-seeder `
            --enqueue-demo `
            --enqueue-only `
            --demo-input examples/windows_event_sample.xml
    }
}

$debianCommand = "cd `$HOME && LOGMINER_REDIS_URL='$GuestRedisUrl' `$HOME/.venv-logminer/bin/python scripts/logminer_intelligent_agent_worker.py --redis-url '$GuestRedisUrl' --event-stream logminer:events --task-stream '$TaskStream' --group '$Group' --run-id '$RunId' --consumer debian-worker-1 --agent-id debian-worker-1 --cycles $CyclesPerWorker --max-parallel-tasks 1 --claim-idle-ms 30000 --memory data/processed/debian-worker-1-memory.json"
$ubuntuCommand = "cd `$HOME && LOGMINER_REDIS_URL='$GuestRedisUrl' python3 scripts/logminer_intelligent_agent_worker.py --redis-url '$GuestRedisUrl' --event-stream logminer:events --task-stream '$TaskStream' --group '$Group' --run-id '$RunId' --consumer ubuntu-worker-1 --agent-id ubuntu-worker-1 --cycles $CyclesPerWorker --max-parallel-tasks 1 --claim-idle-ms 30000 --memory data/processed/ubuntu-worker-1-memory.json"

Invoke-VBoxGuest -VmName Debian -User $DebianUser -Password $DebianPassword -Command $debianCommand
Invoke-VBoxGuest -VmName Ubuntu -User $UbuntuUser -Password $UbuntuPassword -Command $ubuntuCommand
Invoke-VBoxGuest -VmName Debian -User $DebianUser -Password $DebianPassword -Command $debianCommand
Invoke-VBoxGuest -VmName Ubuntu -User $UbuntuUser -Password $UbuntuPassword -Command $ubuntuCommand

$summaryScript = @"
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, r"src\logminer")
from agents.bus import RedisMessageBus

run_id = "$RunId"
task_stream = "$TaskStream"
group = "$Group"
bus = RedisMessageBus(url="$HostRedisUrl", stream="logminer:events", run_id=run_id)
messages = bus.read(run_id=run_id, count=10000)
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
    "tasks_enqueued": stream_len,
    "tasks_completed": len(completed),
    "unique_tasks_completed": len([task_id for task_id in unique_tasks if task_id]),
    "tasks_failed": len(failed),
    "pending_after": pending,
    "by_agent": dict(by_agent),
    "by_type": dict(by_type),
}
Path("$OutputJson").parent.mkdir(parents=True, exist_ok=True)
Path("$OutputJson").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
md = [
    "| Indicateur | Valeur |",
    "| --- | ---: |",
    f"| Taches enfilees | {summary['tasks_enqueued']} |",
    f"| Taches terminees | {summary['tasks_completed']} |",
    f"| Taches uniques terminees | {summary['unique_tasks_completed']} |",
    f"| Taches echouees | {summary['tasks_failed']} |",
    f"| Pending final Redis | {summary['pending_after']} |",
    f"| Taches Debian | {summary['by_agent'].get('debian-worker-1', 0)} |",
    f"| Taches Ubuntu | {summary['by_agent'].get('ubuntu-worker-1', 0)} |",
]
Path("$OutputMarkdown").parent.mkdir(parents=True, exist_ok=True)
Path("$OutputMarkdown").write_text("\n".join(md) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
"@

python -c $summaryScript
if ($LASTEXITCODE -ne 0) {
    throw "Synthese de campagne echouee."
}
