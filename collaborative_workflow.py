#!/usr/bin/env python3
"""
Complete Collaborative Workflow
Orchestrates the entire process from staging to PR-ready state.
"""

import json
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        # Split the command into a list of arguments to avoid shell=True
        cmd_args = shlex.split(command)
        result = subprocess.run(cmd_args, shell=False, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def check_prerequisites():
    """Check if all required files and tools are available."""
    print("🔍 Checking prerequisites...")
    
    required_files = [
        'nyaya_corpus_staging.jsonl',
        'sanskrit_staging_pipeline.py',
        'classify_cultural_traditions.py',
        'organize_batches.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All prerequisites satisfied")
    return True

def analyze_staging_data():
    """Analyze current staging data and report status."""
    print("📊 Analyzing staging data...")
    
    try:
        with open('nyaya_corpus_staging.jsonl', 'r', encoding='utf-8') as f:
            entries = [json.loads(line) for line in f]
        
        total_entries = len(entries)
        unclassified = sum(1 for e in entries if e.get('cultural_tradition') == 'Unknown')
        unbatched = sum(1 for e in entries if e.get('batch_id') == 'None')
        
        print(f"📈 Staging Analysis:")
        print(f"   Total entries: {total_entries}")
        print(f"   Unclassified: {unclassified}")
        print(f"   Unbatched: {unbatched}")
        
        return {
            'total': total_entries,
            'unclassified': unclassified,
            'unbatched': unbatched
        }
    except Exception as e:
        print(f"❌ Failed to analyze staging data: {e}")
        return None

def build_workflow_steps(analysis: dict) -> list:
    """Build the list of workflow steps based on current analysis."""
    workflow_steps = []
    
    # Step 1: Cultural Classification (if needed)
    if analysis['unclassified'] > 0:
        workflow_steps.append({
            'command': 'python classify_cultural_traditions.py',
            'description': f'Classify {analysis["unclassified"]} cultural traditions'
        })
    
    # Step 2: Batch Organization (if needed)
    if analysis['unbatched'] > 0:
        workflow_steps.append({
            'command': 'python organize_batches.py', 
            'description': f'Organize {analysis["unbatched"]} entries into batches'
        })
    
    # Step 3: Staging Pipeline Validation
    workflow_steps.append({
        'command': 'python sanskrit_staging_pipeline.py',
        'description': 'Run complete validation pipeline'
    })
    
    return workflow_steps

def execute_workflow_steps(workflow_steps: list) -> bool:
    """Execute the given workflow steps sequentially."""
    print(f"\n🔧 Executing {len(workflow_steps)} workflow steps...")
    
    for i, step in enumerate(workflow_steps, 1):
        print(f"\n--- Step {i}/{len(workflow_steps)} ---")
        success = run_command(step['command'], step['description'])
        if not success:
            print(f"💥 Workflow failed at step {i}")
            return False
    return True

def generate_workflow_summary(analysis: dict, steps_executed: int):
    """Generate and save the workflow summary."""
    print("\n📋 Generating workflow summary...")
    summary = {
        'workflow_date': datetime.now().isoformat(),
        'initial_analysis': analysis,
        'steps_executed': steps_executed,
        'status': 'completed',
        'next_actions': [
            'Review validation results',
            'Update analysis notebook', 
            'Create pull request using PR_TEMPLATE.md',
            'Coordinate with repository maintainers'
        ]
    }
    
    with open('workflow_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

def print_final_status(final_analysis: dict):
    """Print the final status of the collaborative workflow."""
    print("\n🎉 Collaborative Workflow Complete!")
    print("=" * 50)
    print(f"📊 Final Status:")
    print(f"   Total entries processed: {final_analysis['total']}")
    print(f"   Remaining unclassified: {final_analysis['unclassified']}")
    print(f"   Remaining unbatched: {final_analysis['unbatched']}")
    
    print(f"\n📝 Next Steps:")
    print(f"   1. Review workflow_summary.json for details")
    print(f"   2. Check pipeline validation results")
    print(f"   3. Use PR_TEMPLATE.md to create pull request")
    print(f"   4. Update analysis notebook with new entries")
    
    print(f"\n🤝 Ready for Pull Request Creation!")

def main():
    """Main collaborative workflow orchestration."""
    print("🚀 Starting Collaborative Nyāya Corpus Workflow")
    print("=" * 50)

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Analyze current state
    analysis = analyze_staging_data()
    if not analysis:
        sys.exit(1)

    # Build workflow steps
    workflow_steps = build_workflow_steps(analysis)

    # Execute workflow steps
    if not execute_workflow_steps(workflow_steps):
        sys.exit(1)

    # Generate workflow summary
    generate_workflow_summary(analysis, len(workflow_steps))

    # Final analysis
    final_analysis = analyze_staging_data()
    if final_analysis:
        print_final_status(final_analysis)

if __name__ == "__main__":
    main()
