import os
import subprocess
from datetime import datetime

# قائمة مسارات المستودعات المهمة
repos = [
    "~/nawah-contracts",
    "~/nawah-nft-test",
    "~/nawah-devbot",
    "~/nawah-wallet-pro",
    # أضف باقي المسارات هنا
]

REPORT_FILE = os.path.expanduser("~/nawah-devbot/devbot_repo_report.txt")

def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

def run_cmd(cmd, cwd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)

def get_next_tag(repo_path):
    result = run_cmd(["git", "tag"], repo_path)
    tags = result.stdout.strip().split("\n")
    tags = [t for t in tags if t.startswith("v")]
    if not tags or tags == [""]:
        return "v0.0.1"
    last_tag = sorted(tags, key=lambda s: list(map(int, s[1:].split("."))))[-1]
    major, minor, patch = map(int, last_tag[1:].split("."))
    patch += 1
    return f"v{major}.{minor}.{patch}"

def ensure_file(repo_path, filename, default_content=""):
    file_path = os.path.join(repo_path, filename)
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write(default_content)
        return f"⚡ Created missing file: {filename}"
    return f"✅ File exists: {filename}"

def ensure_workflows(repo_path):
    workflows_path = os.path.join(repo_path, ".github", "workflows")
    messages = []
    if not os.path.exists(workflows_path):
        os.makedirs(workflows_path)
        messages.append("⚡ Created missing folder: .github/workflows")
    # إنشاء workflow أولي إذا لم يكن موجود
    sample_workflow = os.path.join(workflows_path, "release_only.yml")
    if not os.path.exists(sample_workflow):
        default_workflow_content = (
            "name: Release Only\non:\n  push:\n    branches: [ main ]\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - run: echo 'Release workflow placeholder'\n"
        )
        with open(sample_workflow, "w") as f:
            f.write(default_workflow_content)
        messages.append(f"⚡ Created default workflow: release_only.yml")
    else:
        messages.append("✅ Workflow exists: release_only.yml")
    return "\n".join(messages)

def process_repo(repo_path):
    repo_path = os.path.expanduser(repo_path)
    if not os.path.exists(repo_path):
        return f"❌ Repo not found: {repo_path}"

    messages = [f"\n=== Processing {repo_path} ==="]

    # تجهيز الملفات الأساسية
    messages.append(ensure_file(repo_path, "package.json", '{\n  "name": "my-repo",\n  "version": "0.0.1"\n}'))
    messages.append(ensure_file(repo_path, "release_only.sh", "#!/bin/bash\n# Placeholder release script\n"))
    messages.append(ensure_workflows(repo_path))

    # التحقق من تغييرات غير ملتزمة
    result = run_cmd(["git", "status", "--porcelain"], repo_path)
    changes = result.stdout.strip()

    if changes:
        messages.append(color_text("⚠️ Uncommitted changes detected. Committing...", "33"))
        run_cmd(["git", "add", "."], repo_path)
        run_cmd(["git", "commit", "-m", "DevBot: auto-commit local changes"], repo_path)
    else:
        messages.append(color_text("✅ No uncommitted changes.", "32"))

    # عمل pull مع rebase
    messages.append("🔄 Pulling latest changes from remote...")
    pull_result = run_cmd(["git", "pull", "--rebase"], repo_path)
    messages.append(pull_result.stdout.strip())

    # التحقق من commits لم تُدفع
    result_upstream = run_cmd(["git", "rev-list", "--count", "--left-only", "@{u}...HEAD"], repo_path)
    try:
        commits_ahead = int(result_upstream.stdout.strip())
    except:
        commits_ahead = 0

    if commits_ahead > 0:
        messages.append(color_text(f"🔺 {commits_ahead} commits ahead. Pushing to remote...", "35"))
        push_result = run_cmd(["git", "push"], repo_path)
        messages.append(push_result.stdout.strip())
    else:
        messages.append(color_text("✅ Repository up-to-date with remote.", "32"))

    # إنشاء tag إصدار جديد تلقائيًا
    new_tag = get_next_tag(repo_path)
    messages.append(color_text(f"🏷 Creating new release tag: {new_tag}", "36"))
    run_cmd(["git", "tag", new_tag], repo_path)
    run_cmd(["git", "push", "origin", new_tag], repo_path)
    messages.append(color_text(f"✅ Tag {new_tag} pushed to remote.", "32"))

    return "\n".join(messages)

def main():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"=== DevBot Full Update & Release Report ({timestamp}) ===\n"
    print(header)
    
    report_lines = [header]

    for repo in repos:
        repo_report = process_repo(repo)
        print(repo_report)
        report_lines.append(repo_report + "\n")

    # حفظ التقرير النهائي
    with open(REPORT_FILE, "w") as f:
        f.writelines(report_lines)

    print(f"\n📄 Full report saved to {REPORT_FILE}")

if __name__ == "__main__":
    main()

