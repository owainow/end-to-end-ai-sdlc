#!/usr/bin/env python3
"""
Convert speckit tasks.md to GitHub Issues.

Usage:
    python scripts/create_github_issues.py specs/002-weather-frontend/tasks.md

Requirements:
    - GitHub CLI (gh) installed and authenticated
    - Run from the repository root
"""

import re
import subprocess
import sys
from pathlib import Path


def parse_tasks(tasks_file: Path) -> list[dict]:
    """Parse tasks.md and extract task information."""
    content = tasks_file.read_text(encoding="utf-8")
    tasks = []
    
    # Pattern to match task blocks
    task_pattern = re.compile(
        r"### (T\d+): (.+?)(?:\s*✅)?\n"
        r"- \*\*Priority:\*\* (\w+)\n"
        r"- \*\*Estimate:\*\* (.+?)\n"
        r"(?:- \*\*Dependencies:\*\* (.+?)\n)?"
        r"(?:- \*\*File:\*\* (.+?)\n)?"
        r"(?:- \*\*FR:\*\* (.+?)\n)?"
        r"(?:- \*\*NFR:\*\* (.+?)\n)?"
        r"- \*\*Acceptance Criteria:\*\*\n((?:\s+- \[[ x]\] .+\n)+)",
        re.MULTILINE
    )
    
    # Find current phase
    phase_pattern = re.compile(r"## (Phase \d+: .+)")
    phases = phase_pattern.findall(content)
    
    for match in task_pattern.finditer(content):
        task_id = match.group(1)
        title = match.group(2).strip()
        priority = match.group(3)
        estimate = match.group(4)
        dependencies = match.group(5) or "None"
        file_path = match.group(6) or ""
        fr = match.group(7) or ""
        nfr = match.group(8) or ""
        acceptance_criteria = match.group(9)
        
        # Find which phase this task belongs to
        task_pos = match.start()
        current_phase = "Unknown"
        for phase_match in phase_pattern.finditer(content):
            if phase_match.start() < task_pos:
                current_phase = phase_match.group(1)
        
        # Parse acceptance criteria
        criteria_lines = []
        for line in acceptance_criteria.strip().split("\n"):
            line = line.strip()
            if line.startswith("- ["):
                criteria_lines.append(line)
        
        # Determine if task is complete
        is_complete = "✅" in content[match.start():match.end()+5]
        
        tasks.append({
            "id": task_id,
            "title": title,
            "priority": priority,
            "estimate": estimate,
            "dependencies": dependencies,
            "file": file_path,
            "fr": fr,
            "nfr": nfr,
            "phase": current_phase,
            "acceptance_criteria": criteria_lines,
            "complete": is_complete
        })
    
    return tasks


def create_issue_body(task: dict, spec_name: str) -> str:
    """Create GitHub issue body from task."""
    body = f"""## Task: {task['id']}

**Spec:** {spec_name}  
**Phase:** {task['phase']}  
**Priority:** {task['priority']}  
**Estimate:** {task['estimate']}  
**Dependencies:** {task['dependencies']}  
"""
    
    if task['file']:
        body += f"**File:** `{task['file']}`  \n"
    
    if task['fr']:
        body += f"**Functional Requirements:** {task['fr']}  \n"
    
    if task['nfr']:
        body += f"**Non-Functional Requirements:** {task['nfr']}  \n"
    
    body += "\n## Acceptance Criteria\n\n"
    for criterion in task['acceptance_criteria']:
        body += f"{criterion}\n"
    
    return body


def get_labels(task: dict) -> list[str]:
    """Determine labels for the issue."""
    labels = []
    
    # Priority label
    if task['priority'].lower() == 'must':
        labels.append('priority: high')
    elif task['priority'].lower() == 'should':
        labels.append('priority: medium')
    else:
        labels.append('priority: low')
    
    # Type label
    labels.append('task')
    
    # Phase label (sanitized)
    phase_num = re.search(r"Phase (\d+)", task['phase'])
    if phase_num:
        labels.append(f"phase-{phase_num.group(1)}")
    
    return labels


def create_github_issue(task: dict, spec_name: str, dry_run: bool = False) -> bool:
    """Create a GitHub issue using gh CLI."""
    title = f"[{task['id']}] {task['title']}"
    body = create_issue_body(task, spec_name)
    labels = get_labels(task)
    
    if dry_run:
        print(f"\n{'='*60}")
        print(f"ISSUE: {title}")
        print(f"LABELS: {', '.join(labels)}")
        print(f"{'='*60}")
        print(body)
        return True
    
    # Build gh command
    cmd = [
        "gh", "issue", "create",
        "--title", title,
        "--body", body,
    ]
    
    for label in labels:
        cmd.extend(["--label", label])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Created: {title}")
        print(f"   URL: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create: {title}")
        print(f"   Error: {e.stderr}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_github_issues.py <tasks.md> [--dry-run]")
        print("\nOptions:")
        print("  --dry-run    Preview issues without creating them")
        print("  --skip-complete  Skip tasks marked as complete")
        sys.exit(1)
    
    tasks_file = Path(sys.argv[1])
    dry_run = "--dry-run" in sys.argv
    skip_complete = "--skip-complete" in sys.argv
    
    if not tasks_file.exists():
        print(f"Error: File not found: {tasks_file}")
        sys.exit(1)
    
    # Extract spec name from path
    spec_name = tasks_file.parent.name
    
    print(f"📋 Parsing tasks from: {tasks_file}")
    tasks = parse_tasks(tasks_file)
    
    if not tasks:
        print("No tasks found in file.")
        sys.exit(1)
    
    print(f"Found {len(tasks)} tasks")
    
    if skip_complete:
        tasks = [t for t in tasks if not t['complete']]
        print(f"  ({len(tasks)} incomplete)")
    
    if dry_run:
        print("\n🔍 DRY RUN MODE - No issues will be created\n")
    
    created = 0
    failed = 0
    
    for task in tasks:
        if create_github_issue(task, spec_name, dry_run):
            created += 1
        else:
            failed += 1
    
    print(f"\n{'='*40}")
    print(f"Summary: {created} created, {failed} failed")
    
    if dry_run:
        print("\nTo create issues for real, run without --dry-run")


if __name__ == "__main__":
    main()
