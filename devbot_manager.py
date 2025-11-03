#!/usr/bin/env python3
"""
DevBot Manager - final automated script
- works on a list of local repo paths (repos list)
- ensures basic files, commits local changes, pulls, runs release script, creates tags, pushes
- logs detailed report to ~/nawah-devbot/devbot_repo_report.txt
- optional Slack/Telegram notifications via env vars in ~/nawah-devbot/.env
"""

import os
import subprocess
import traceback
from datetime import datetime
from pathlib import Path

# -----------------------
# CONFIGURATION (edit if needed)
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

REPORT_FILE = Path.home() / "nawah-devbot" / "devbot_repo_report.txt"
ENV_FILE = Path.home() / "nawah-devbot" / ".env"  # optional: SLACK_WEBHOOK, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# -----------------------
# UTILITIES
# -----------------------
def run(cmd, cwd=None, check=False):
    """Run command (shell), return (code, stdout, stderr)."""
    try:
        proc = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def log_append(lines):
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

def load_env():
    env = {}
    if ENV_FILE.exists():
        for ln in ENV_FILE.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#") or "=" not in ln:
                continue
            k, v = ln.split("=", 1)
            env[k.strip()] = v.strip()
    return env

# -----------------------
# TAG helper
# -----------------------
def compute_next_tag(repo_path):
    # gather tags starting with v and parse semantic vX.Y.Z (fallback to datetime)
    code, out, err = run("git tag --list", cwd=repo_path)
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
        except:
            continue
    if sems:
        # pick the max then increment patch
        sems_sorted = sorted(sems, key=lambda x: x[0])
        nums, last_tag = sems_sorted[-1]
        while len(nums) < 3:
            nums.append(0)
        nums[2] += 1  # increment patch
        return f"v{nums[0]}.{nums[1]}.{nums[2]}", None
    # if no sem tags, fallback to date-based tag
    tag = "v" + datetime.utcnow().strftime("%Y.%m.%d.%H%M%S")
    return tag, None

# -----------------------
# OPTIONAL notifications
# -----------------------
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
        import urllib.parse, urllib.request, json
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": text}
        data = urllib.parse.urlencode(params).encode()
        with urllib.request.urlopen(url, data=data, timeout=10) as resp:
            return resp.getcode() == 200, ""
    except Exception as e:
        return False, str(e)

# -----------------------
# MAIN processing
# -----------------------
def process_repo(repo_raw, env):
    repo = os.path.expanduser(repo_raw)
    lines = []
    lines.append(f"--- Processing {repo} ---")
    if not os.path.isdir(repo):
        lines.append(f"ERROR: path not found: {repo}")
        return lines

    # ensure in git repo
    code, out, err = run("git rev-parse --is-inside-work-tree", cwd=repo)
    if code != 0:
        lines.append(f"ERROR: not a git repo or git not available: {err}")
        return lines

    # create basic files if missing
    essentials = {
        "package.json": '{\n  "name": "auto-created",\n  "version": "0.0.1"\n}\n',
        "release_only.sh": "#!/bin/bash\n# placeholder release script\n"
    }
    for fname, content in essentials.items():
        p = Path(repo) / fname
        if not p.exists():
            try:
                p.write_text(content, encoding="utf-8")
                if fname.endswith(".sh"):
                    run(f"chmod +x {fname}", cwd=repo)
                lines.append(f"Created missing file: {fname}")
            except Exception as e:
                lines.append(f"Failed to create {fname}: {e}")

    # ensure workflows dir and default workflow
    wfdir = Path(repo) / ".github" / "workflows"
    if not wfdir.exists():
        try:
            wfdir.mkdir(parents=True, exist_ok=True)
            lines.append("Created missing folder: .github/workflows")
        except Exception as e:
            lines.append(f"Failed to create workflows dir: {e}")
    wf_file = wfdir / "release_only.yml"
    if not wf_file.exists():
        try:
            wf_file.write_text("name: Release (placeholder)\non: [push]\njobs: { build: { runs-on: ubuntu-latest, steps: [{ uses: actions/checkout@v4 }] } }\n", encoding="utf-8")
            lines.append("Created default workflow: release_only.yml")
        except Exception as e:
            lines.append(f"Failed to create workflow: {e}")

    # check uncommitted changes
    code, stdout, stderr = run("git status --porcelain", cwd=repo)
    if stdout:
        lines.append("Uncommitted changes detected -> auto-commit")
        run("git add -A", cwd=repo)
        # commit but ignore failure (e.g., if no user configured)
        run('git commit -m "DevBot: auto-commit local changes"', cwd=repo)
    else:
        lines.append("No uncommitted changes")

    # stash local changes before pull to avoid rebase issues
    run("git stash --include-untracked || true", cwd=repo)
    code, out, err = run("git pull origin main --rebase", cwd=repo)
    if code == 0:
        lines.append("Pulled latest changes from origin/main")
    else:
        lines.append(f"git pull error: {err or out}")

    # try pop stash (if any)
    run("git stash pop || true", cwd=repo)

    # run release script if exists and executable
    rel_script = Path(repo) / "release_only.sh"
    if rel_script.exists():
        lines.append("Running release_only.sh (if present)")
        code, out, err = run(f"./release_only.sh", cwd=repo)
        if code == 0:
            lines.append("release_only.sh executed")
            if out:
                lines.append(out)
        else:
            lines.append(f"release_only.sh error: {err or out}")

    # compute next tag, create and push
    new_tag, err_tag = compute_next_tag(repo)
    if new_tag:
        code, out, err = run(f"git tag {new_tag}", cwd=repo)
        if code == 0:
            code2, out2, err2 = run(f"git push origin {new_tag}", cwd=repo)
            if code2 == 0:
                lines.append(f"Created and pushed tag: {new_tag}")
            else:
                lines.append(f"Failed to push tag {new_tag}: {err2 or out2}")
        else:
            lines.append(f"Failed to create tag {new_tag}: {err or out}")
    else:
        lines.append(f"Failed to compute tag: {err_tag}")

    # final push of commits (if any)
    run("git push --follow-tags origin main || true", cwd=repo)

    return lines

def main():
    # prepare report file
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== DevBot Report {datetime.utcnow().isoformat()} UTC ===\n\n")

    env = load_env()
    all_lines = []
    for repo in REPOS:
        try:
            lines = process_repo(repo, env)
            all_lines.extend(lines)
            # append to report file as we go
            log_append(lines)
            log_append([""])
        except Exception as e:
            tb = traceback.format_exc()
            err_line = f"Exception processing {repo}: {e}\n{tb}"
            all_lines.append(err_line)
            log_append([err_line])

    # Optional: send summary to Slack/Telegram if configured
    summary = "\n".join(all_lines[:50])  # include first 50 lines in summary
    if env.get("SLACK_WEBHOOK"):
        ok, err = send_slack(env["SLACK_WEBHOOK"], f"DevBot run summary:\n{summary}")
        log_append([f"Slack notify: ok={ok}, err={err}"])
    if env.get("TELEGRAM_TOKEN") and env.get("TELEGRAM_CHAT_ID"):
        ok, err = send_telegram(env["TELEGRAM_TOKEN"], env["TELEGRAM_CHAT_ID"], f"DevBot run summary:\n{summary}")
        log_append([f"Telegram notify: ok={ok}, err={err}"])

    print(f"Report saved to: {REPORT_FILE}")

if __name__ == "__main__":
    main()

