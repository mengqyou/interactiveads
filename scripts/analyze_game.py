#!/usr/bin/env python3
"""
Game Analysis Script

Clones and analyzes an open source game repository
Usage: python scripts/analyze_game.py <repo_name>
"""
import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from game_analyzer.github_analyzer import GitHubAnalyzer, GameRepository
from game_analyzer.asset_extractor import AssetExtractor


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/analyze_game.py <repo_name>")
        print("Available repos: hypersomnia, anyrpg, godot-open-rpg, tanks-of-freedom")
        return
        
    repo_name = sys.argv[1]
    
    # Initialize analyzers
    github_analyzer = GitHubAnalyzer()
    asset_extractor = AssetExtractor()
    
    # Get repository info
    repos = github_analyzer.get_recommended_repositories()
    target_repo = None
    
    for repo in repos:
        if repo.name == repo_name:
            target_repo = repo
            break
            
    if not target_repo:
        print(f"Repository {repo_name} not found in recommendations")
        return
        
    print(f"Analyzing {target_repo.name}...")
    print(f"Description: {target_repo.description}")
    print(f"Engine: {target_repo.engine}")
    print(f"Genre: {target_repo.genre}")
    print()
    
    # Clone repository
    repo_path = github_analyzer.clone_repository(target_repo.url, target_repo.name)
    
    # Analyze repository structure
    print("Analyzing repository structure...")
    structure_analysis = github_analyzer.analyze_repository_structure(repo_path)
    
    # Extract and analyze assets
    print("Extracting assets...")
    assets = asset_extractor.extract_assets(repo_path)
    asset_report = asset_extractor.generate_asset_report(assets)
    
    # Generate final report
    report = {
        "repository": {
            "name": target_repo.name,
            "url": target_repo.url,
            "engine": target_repo.engine,
            "genre": target_repo.genre,
            "description": target_repo.description
        },
        "structure_analysis": structure_analysis,
        "asset_analysis": asset_report,
        "character_assets": [
            {"path": asset.path, "dimensions": asset.dimensions}
            for asset in asset_extractor.find_character_assets(assets)
        ]
    }
    
    # Save report
    output_path = Path("data") / f"{repo_name}_analysis.json"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    print(f"\nAnalysis complete! Report saved to {output_path}")
    print(f"Total files: {structure_analysis['total_files']}")
    print(f"Total assets: {asset_report['total_assets']}")
    print(f"Character assets: {asset_report['character_assets']}")
    print(f"Detected engine: {structure_analysis['engine_detected']}")


if __name__ == "__main__":
    main()