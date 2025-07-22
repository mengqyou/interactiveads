#!/usr/bin/env python3
"""
GitHub Update Helper Script

Makes it easy to commit and push changes to GitHub
without storing any credentials.
"""
import subprocess
import sys
from datetime import datetime


def run_command(command, description):
    """Run a git command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} successful")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False


def check_git_status():
    """Check if there are changes to commit"""
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("📝 Changes detected:")
        print(result.stdout)
        return True
    else:
        print("✨ No changes to commit")
        return False


def main():
    """Main update workflow"""
    print("GitHub Update Helper")
    print("===================")
    
    # Check if we're in a git repository
    if not run_command("git status", "Checking git repository"):
        print("❌ Not in a git repository or git not configured")
        return False
    
    # Check for changes
    if not check_git_status():
        print("Nothing to update!")
        return True
    
    # Get commit message from user
    if len(sys.argv) > 1:
        commit_message = " ".join(sys.argv[1:])
    else:
        commit_message = input("Enter commit message (or press Enter for default): ").strip()
        
    if not commit_message:
        commit_message = f"Update project files - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Add all changes
    if not run_command("git add .", "Adding changes"):
        return False
    
    # Commit changes
    escaped_message = commit_message.replace('"', '\\"')
    if not run_command(f'git commit -m "{escaped_message}"', "Committing changes"):
        return False
    
    # Push to GitHub
    print("\n🚀 Ready to push to GitHub")
    print("Note: You may be prompted for authentication")
    
    if not run_command("git push origin main", "Pushing to GitHub"):
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure you're authenticated with GitHub")
        print("2. Try: gh auth login")
        print("3. Or set up SSH keys in GitHub settings")
        return False
    
    print("\n🎉 Successfully updated GitHub repository!")
    print("🔗 View at: https://github.com/mengqyou/interactiveads")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)