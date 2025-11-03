#!/usr/bin/env python3
# devbot_manager.py
# DevBot final: Termux-friendly manager for a list of repos
# - auto-add github known_host to avoid interactive prompt
# - create basic files if missing, auto-commit local changes, pull/rebase, run release script, tag, push
# - daily report written to ~/nawah-devbot/devbot_repo_report.txt
# - optional Slack/Telegram notifications via ~/nawah-devbot/.env

import os
import subprocess
import traceback
from pathlib import Path
from datetime import datetime, timezone

# -----------------------
# Configuration: update if needed
# -----------------------
REPOS = [
    "~/nawah-contracts",
    "~/nawah-nft-test",
    "~/nawah-devbot",
    "~/nawah-wallet-pro",
    "~/nawah-webhook",
    "~/nawah-ui",
    "~/nawah-dex",
    "~/nawah-staking",
    "~/nawah-nft-market",
    "~/nawah-faucet",
    "~/nawah-bridge",
    "~/nawah-analytics",
    "~/nawah-launchpad",
    "~/nawah-farming",
    "~/nawah-docs",
    "~/nawah-game",
    "~/nawah-erc20",
    "~/nawah-erc721",
    "~/nawah-erc1155",
    "~/nawah-api",
    "~/nawah-bot",
    "~/nawah-dashboard",
    "~/nawah-frontend",
    "~/nawah-backend",
    "~/nawah-smartcontracts",
    "~/nawah-nft-generator",
    "~/nawah-tokenomics",
    "~/nawah-defi",
    "~/nawah-liquidity",
    "~/nawah-ico",
    "~/nawah-payments",
    "~/nawah-tools",
    "~/nawah-marketplace",
    "~/nawah-support",
    "~/nawah-automation",
    "~/nawah-explorer",
    "~/nawah-scripts",
    "~/nawah-test",
    "~/nawah-tutorials",
    "~/nawah-docs-legacy",
    "~/nawah-integration",
    "~/nawah-infra",
]

HOME = Path.home()
DEVBOT_DIR = HOME / "nawah-devbot"
REPORT_FILE = DEVBOT_DIR / "devbot_repo_report.txt"
ENV_FILE = DEVBOT_DIR / ".env"

# -----------------------
# Helpers
# -----------------------
def run(cmd, cwd=None, timeout=None):
    """Run shell command, return (code, stdout, stderr)."""
    try:
        proc = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()
    except Exception as e:
        return 1, "", str(e)

def append_report(lines):
    DEVBOT_DIR.mkdir(parents=True, exist_ok=True)
    with REPORT_FILE.open("a", encoding="utf-8") as f:
        for ln in lines:
            f.write(ln + "\n")

def ensure_github_known_host():
    ssh_dir = HOME / ".ssh"
    known_hosts = ssh_dir / "known_hosts"
    try:
        ssh_dir.mkdir(mode=0o700, exist_ok=True)
    except Exception:
        pass
    if known_hosts.exists():
        try:
            content = known_hosts.read_text(encoding="utf-8")
            if "github.com" in content:
                return True, "github.com already in known_hosts"
        except Exception:
            pass
    # attempt ssh-keyscan
    code, out, err = run("ssh-keyscan -t rsa,ecdsa,ed25519 github.com 2>/dev/null")
    if code == 0 and out:
        try:
            with known_hosts.open("a", encoding="utf-8") as f:
                f.write(out + "\n")
            try:
                known_hosts.chmod(0o600)
            except Exception:
                pass
            return True, "added github.com via ssh-keyscan"
        except Exception as e:
            return False, f"failed write known_hosts: {e}"
    return False, f"ssh-keyscan failed: {err or out}"

def compute_next_tag(repo):
    code, out, err = run("git tag --list", cwd=repo)
    if code != 0:
        return None, f"git tag failed: {err}"
    tags = [t.strip() for t in out.splitlines() if t.strip().startswith("v")]
    sems = []
    for t in tags:
        body = t[1:]
        parts = body.split(".")
        try:
            nums = list(map(int, parts))
            sems.append((nums, t))
        except Exception:
            continue
    if sems:
        sems.sort(key=lambda x: x[0])
        nums, last = sems[-1]
        while len(nums) < 3:
            nums.append(0)
        nums[2] += 1
        return f"v{nums[0]}.{nums[1]}.{nums[2]}", None
    # fallback to timestamp
    tag = "v" + datetime.now(timezone.utc).strftime("%Y.%m.%d.%H%M%S")
    return tag, None

def send_slack(webhook, text):
    try:
        import json, urllib.request
        data = json.dumps({"text": text}).encode("utf-8")
        req = urllib.request.Request(webhook, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.getcode() == 200, ""
    except Exception as e:
        return False, str(e)

def send_telegram(token, chat_id, text):
    try:
        import urllib.parse, urllib.request
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": text}
        data = urllib.parse.urlencode(params).encode()
        with urllib.request.urlopen(url, data=data, timeout=10) as resp:
            return resp.getcode() == 200, ""
    except Exception as e:
        return False, str(e)

# -----------------------
# Per-repo processing
# -----------------------
def process_repo(repo_raw):
    repo = os.path.expanduser(repo_raw)
    lines = []
    lines.append(f"--- {datetime.now(timezone.utc).isoformat()} Processing {repo} ---")
    p = Path(repo)
    if not p.exists():
        lines.append(f"ERROR: path not found: {repo}")
        return lines

    # ensure git
    code, out, err = run("git rev-parse --is-inside-work-tree", cwd=repo)
    if code != 0:
        lines.append(f"ERROR: not a git repo or git error: {err or out}")
        return lines

    # create basic files if missing
    essentials = {
        "package.json": '{\n  "name": "auto-created",\n  "version": "0.0.1"\n}\n',
        "release_only.sh": "#!/bin/bash\n# auto-created by DevBot - placeholder\nexit 0\n",
    }
    for fname, content in essentials.items():
        fp = p / fname
        if not fp.exists():
            try:
                fp.write_text(content, encoding="utf-8")
                if fname.endswith(".sh"):
                    run(f"chmod +x {fname}", cwd=repo)
                lines.append(f"Created missing file: {fname}")
            except Exception as e:
                lines.append(f"Failed to create {fname}: {e}")

    # ensure workflows dir and default workflow
    wfdir = p / ".github" / "workflows"
    if not wfdir.exists():
        try:
            wfdir.mkdir(parents=True, exist_ok=True)
            lines.append("Created .github/workflows")
        except Exception as e:
            lines.append(f"Failed create workflows dir: {e}")
    wf_file = wfdir / "release_only.yml"
    if not wf_file.exists():
        try:
            wf_file.write_text("name: DevBot placeholder\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - run: echo 'placeholder'\n", encoding="utf-8")
            lines.append("Created default workflow: release_only.yml")
        except Exception as e:
            lines.append(f"Failed to create workflow: {e}")

    # check uncommitted changes
    code, status_out, status_err = run("git status --porcelain", cwd=repo)
    if status_out:
        lines.append("Uncommitted changes found -> attempting auto-commit")
        run("git add -A", cwd=repo)
        run('git commit -m "DevBot: auto-commit local changes" || true', cwd=repo)
    else:
        lines.append("No uncommitted changes")

    # stash include-untracked then pull --rebase
    run("git stash push --include-untracked -m devbot-autostash || true", cwd=repo)
    code, pull_out, pull_err = run("git pull origin main --rebase", cwd=repo)
    if code == 0:
        lines.append("Pulled origin/main successfully")
    else:
        lines.append(f"git pull error (may need manual resolution): {pull_err or pull_out}")

    # pop stash
    run("git stash pop || true", cwd=repo)

    # run release_only.sh if exists
    rel = p / "release_only.sh"
    if rel.exists():
        lines.append("Running release_only.sh")
        code, out, err = run(f"./release_only.sh", cwd=repo, timeout=300)
        if code == 0:
            lines.append("release_only.sh executed")
            if out:
                lines.append(">>> " + out)
        else:
            lines.append(f"release_only.sh failed: {err or out}")

    # compute next tag & push
    new_tag, tag_err = compute_next_tag(repo)
    if new_tag:
        code, out, err = run(f"git tag {new_tag}", cwd=repo)
        if code == 0:
            code2, out2, err2 = run(f"git push origin {new_tag}", cwd=repo)
            if code2 == 0:
                lines.append(f"Created & pushed tag: {new_tag}")
            else:
                lines.append(f"Failed to push tag {new_tag}: {err2 or out2}")
        else:
            lines.append(f"Failed to create tag {new_tag}: {err or out}")
    else:
        lines.append(f"Failed to compute tag: {tag_err}")

    # final push (commits & tags)
    run("git push --follow-tags origin main || true", cwd=repo)

    lines.append(f"Finished {repo}")
    return lines

# -----------------------
# Main
# -----------------------
def main():
    DEVBOT_DIR.mkdir(parents=True, exist_ok=True)
    # rotate previous report
    try:
        if REPORT_FILE.exists():
            rotated = DEVBOT_DIR / f"devbot_report_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}.txt"
            REPORT_FILE.rename(rotated)
    except Exception:
        pass

    ok, msg = ensure_github_known_host()
    append_report([f"DevBot run: {datetime.now(timezone.utc).isoformat()} UTC", f"known_host: {ok} - {msg}", ""])

    all_lines = []
    for r in REPOS:
        try:
            lines = process_repo(r)
            append_report(lines + [""])
            all_lines.extend(lines)
        except Exception as e:
            tb = traceback.format_exc()
            err_lines = [f"Exception processing {r}: {e}", tb]
            append_report(err_lines + [""])
            all_lines.extend(err_lines)

    # try to send light summary if .env exists
    env = {}
    if ENV_FILE.exists():
        for ln in ENV_FILE.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#") or "=" not in ln:
                continue
            k, v = ln.split("=", 1)
            env[k.strip()] = v.strip()

    summary = "\n".join(all_lines[:200])
    if env.get("SLACK_WEBHOOK"):
        ok, err = send_slack(env["SLACK_WEBHOOK"], f"DevBot summary:\n{summary}")
        append_report([f"Slack notify ok={ok}, err={err}"])
    if env.get("TELEGRAM_TOKEN") and env.get("TELEGRAM_CHAT_ID"):
        ok, err = send_telegram(env["TELEGRAM_TOKEN"], env["TELEGRAM_CHAT_ID"], f"DevBot summary:\n{summary}")
        append_report([f"Telegram notify ok={ok}, err={err}"])

    print(f"DevBot finished. Report: {REPORT_FILE}")

if __name__ == "__main__":
    main()
