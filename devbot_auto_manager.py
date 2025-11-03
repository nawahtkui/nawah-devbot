#!/data/data/com.termux/files/usr/bin/env python3
# devbot_auto_manager.py
# Final DevBot for Termux: manage many repos, auto-commit, pull, run release, tag, push, daily report
# Usage: python3 ~/nawah-devbot/devbot_auto_manager.py

import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import traceback

# ----------------------
# CONFIG: قائمة المستودعات (تأكد أن المسارات صحيحة محلياً)
# ----------------------
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

# ----------------------
# Paths & env
# ----------------------
HOME = Path.home()
DEVBOT_DIR = HOME / "nawah-devbot"
REPORT_FILE = DEVBOT_DIR / "devbot_daily_report.txt"
ENV_FILE = DEVBOT_DIR / ".env"  # optional: for SLACK_WEBHOOK, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

# ----------------------
# Helpers
# ----------------------
def run(cmd, cwd=None, timeout=None):
    """Run command (shell mode) and return (code, stdout, stderr)."""
    try:
        proc = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def append_report(lines):
    DEVBOT_DIR.mkdir(parents=True, exist_ok=True)
    with REPORT_FILE.open("a", encoding="utf-8") as f:
        for ln in lines:
            f.write(ln + "\n")

def ensure_ssh_known_host():
    """
    Add GitHub host key to ~/.ssh/known_hosts using ssh-keyscan to avoid interactive prompt.
    Safe: overwrites only if missing.
    """
    ssh_dir = HOME / ".ssh"
    known_hosts = ssh_dir / "known_hosts"
    ssh_dir.mkdir(mode=0o700, exist_ok=True)
    # Check if github.com already present
    if known_hosts.exists():
        try:
            content = known_hosts.read_text(encoding="utf-8")
            if "github.com" in content:
                return True, "github.com already in known_hosts"
        except Exception:
            pass
    # use ssh-keyscan to fetch host keys
    code, out, err = run("ssh-keyscan -t rsa,ecdsa,ed25519 github.com 2>/dev/null")
    if code == 0 and out:
        try:
            with known_hosts.open("a", encoding="utf-8") as f:
                f.write(out + "\n")
            known_hosts.chmod(0o600)
            return True, "ssh-keyscan added github.com to known_hosts"
        except Exception as e:
            return False, f"failed writing known_hosts: {e}"
    else:
        return False, f"ssh-keyscan failed: {err or out}"

def compute_next_semver_tag(repo):
    """
    Attempt to compute next semantic version tag:
    - find tags starting with v and with numeric parts vX.Y.Z
    - increment patch
    - fallback: date-based tag
    """
    code, out, err = run("git tag --list", cwd=repo)
    if code != 0:
        return None, f"git tag failed: {err}"
    tags = [t.strip() for t in out.splitlines() if t.strip().startswith("v")]
    sem_tags = []
    for t in tags:
        body = t[1:]
        parts = body.split(".")
        try:
            nums = list(map(int, parts))
            sem_tags.append((nums, t))
        except:
            continue
    if sem_tags:
        sem_tags.sort(key=lambda x: x[0])
        nums, last = sem_tags[-1]
        while len(nums) < 3:
            nums.append(0)
        nums[2] += 1
        return f"v{nums[0]}.{nums[1]}.{nums[2]}", None
    # fallback: timestamp tag
    tag = "v" + datetime.now(timezone.utc).strftime("%Y.%m.%d.%H%M%S")
    return tag, None

# ----------------------
# Main repo processing
# ----------------------
def process_repo(repo_raw):
    repo = os.path.expanduser(repo_raw)
    lines = []
    lines.append(f"--- {datetime.now(timezone.utc).isoformat()} Processing {repo} ---")
    p = Path(repo)
    if not p.exists():
        lines.append(f"ERROR: path does not exist: {repo}")
        return lines

    # verify git repo
    code, out, err = run("git rev-parse --is-inside-work-tree", cwd=repo)
    if code != 0:
        lines.append("ERROR: not a git repository or git not available")
        lines.append(f"git rev-parse err: {err}")
        return lines

    # create basic files if missing
    essentials = {
        "package.json": '{\n  "name": "auto-created",\n  "version": "0.0.1"\n}\n',
        "release_only.sh": "#!/bin/bash\n# auto-created by DevBot - placeholder release script\nexit 0\n",
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

    # ensure workflows dir and default workflow file
    wfdir = p / ".github" / "workflows"
    if not wfdir.exists():
        try:
            wfdir.mkdir(parents=True, exist_ok=True)
            lines.append("Created .github/workflows folder")
        except Exception as e:
            lines.append(f"Failed create workflows dir: {e}")
    wf_file = wfdir / "release_only.yml"
    if not wf_file.exists():
        try:
            wf_file.write_text("name: DevBot placeholder\non: [push]\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - run: echo 'placeholder'\n", encoding="utf-8")
            lines.append("Created default workflow: release_only.yml")
        except Exception as e:
            lines.append(f"Failed to create default workflow: {e}")

    # check uncommitted changes
    code, status_out, status_err = run("git status --porcelain", cwd=repo)
    if status_out:
        lines.append("Uncommitted changes found -> attempting auto-commit")
        run("git add -A", cwd=repo)
        # commit may fail if user.name/user.email not configured; ignore error
        run('git commit -m "DevBot: auto-commit local changes" || true', cwd=repo)
    else:
        lines.append("No uncommitted changes")

    # stash (include untracked) to avoid rebase conflicts
    run("git stash push --include-untracked -m devbot-autostash || true", cwd=repo)
    # pull latest
    code, pull_out, pull_err = run("git pull origin main --rebase", cwd=repo)
    if code == 0:
        lines.append("Pulled origin/main successfully")
    else:
        lines.append(f"git pull error (may need manual resolution): {pull_err or pull_out}")

    # try to pop stash
    run("git stash pop || true", cwd=repo)

    # run release script if exists and executable
    rel = p / "release_only.sh"
    if rel.exists():
        lines.append("Running release_only.sh...")
        code, out, err = run(f"./release_only.sh", cwd=repo, timeout=300)
        if code == 0:
            lines.append("release_only.sh completed successfully")
            if out:
                lines.append(">>> " + out)
        else:
            lines.append(f"release_only.sh failed: {err or out}")

    # compute next tag and push
    new_tag, tag_err = compute_next_semver_tag(repo)
    if new_tag:
        code, out, err = run(f"git tag {new_tag}", cwd=repo)
        if code == 0:
            code2, out2, err2 = run(f"git push origin {new_tag}", cwd=repo)
            if code2 == 0:
                lines.append(f"Created & pushed tag: {new_tag}")
            else:
                lines.append(f"Tag pushed but push failed: {err2 or out2}")
        else:
            lines.append(f"Failed to create tag {new_tag}: {err or out}")
    else:
        lines.append(f"Failed to compute next tag: {tag_err}")

    # push commits & tags if any
    run("git push --follow-tags origin main || true", cwd=repo)

    lines.append(f"Finished processing {repo}")
    return lines

# ----------------------
# Main
# ----------------------
def main():
    # ensure devbot dir and log rotated
    DEVBOT_DIR.mkdir(parents=True, exist_ok=True)
    # rotate previous report
    if REPORT_FILE.exists():
        rotated = DEVBOT_DIR / f"devbot_report_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}.txt"
        REPORT_FILE.rename(rotated)

    # ensure known_hosts has github key to avoid interactive prompt
    ok, msg = ensure_ssh_known_host()
    initial_lines = [f"DevBot start: {datetime.now(timezone.utc).isoformat()} UTC", f"ssh known_hosts ensure: {ok} - {msg}", ""]
    append_report(initial_lines)

    all_summary = []
    for r in REPOS:
        try:
            lines = process_repo(r)
            append_report(lines + [""])
            all_summary.extend(lines)
        except Exception as e:
            tb = traceback.format_exc()
            err_lines = [f"Exception processing {r}: {e}", tb]
            append_report(err_lines + [""])
            all_summary.extend(err_lines)

    # send lightweight summary via optional channels (reads ENV_FILE if present)
    env = {}
    if ENV_FILE.exists():
        for ln in ENV_FILE.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#") or "=" not in ln:
                continue
            k, v = ln.split("=", 1)
            env[k.strip()] = v.strip()

    summary_text = "\n".join(all_summary[:200])  # short summary
    if env.get("SLACK_WEBHOOK"):
        ok, err = send_slack(env["SLACK_WEBHOOK"], f"DevBot daily summary:\n{summary_text}")
        append_report([f"Slack notify: ok={ok}, err={err}"])
    if env.get("TELEGRAM_TOKEN") and env.get("TELEGRAM_CHAT_ID"):
        ok, err = send_telegram(env["TELEGRAM_TOKEN"], env["TELEGRAM_CHAT_ID"], f"DevBot daily summary:\n{summary_text}")
        append_report([f"Telegram notify: ok={ok}, err={err}"])

    print(f"DevBot finished. Report at: {REPORT_FILE}")

if __name__ == "__main__":
    main()
