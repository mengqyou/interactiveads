#!/usr/bin/env python3
"""
Engagement Moment Analysis Script

Analyzes a game repository to find the most engaging moments
for mini-game creation

Usage: python scripts/analyze_moments.py <game_analysis.json>
"""
import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from engagement_ai.moment_analyzer import MomentAnalyzer


def main():
    if len(sys.argv) != 2:
        print("Usage: python scripts/analyze_moments.py <game_analysis.json>")
        print("Example: python scripts/analyze_moments.py data/tanks-of-freedom_analysis.json")
        return
        
    analysis_file = Path(sys.argv[1])
    
    if not analysis_file.exists():
        print(f"Analysis file {analysis_file} not found")
        return
        
    # Load game analysis
    with open(analysis_file, 'r') as f:
        analysis_data = json.load(f)
        
    game_name = analysis_data['repository']['name']
    print(f"Analyzing engagement moments for {game_name}...")
    
    # Find repository path
    repo_path = Path("data/repositories") / game_name
    if not repo_path.exists():
        print(f"Repository path {repo_path} not found")
        return
        
    # Analyze moments
    analyzer = MomentAnalyzer()
    moments = analyzer.analyze_game_moments(repo_path, analysis_data)
    
    # Generate report
    report = analyzer.generate_moment_report(moments, game_name)
    
    # Save report
    output_path = Path("data") / f"{game_name}_moments.json"
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    # Display summary
    print(f"\nEngagement Analysis Complete!")
    print(f"Found {report['total_moments_found']} potential mini-game moments")
    print(f"Report saved to {output_path}")
    print()
    
    print("Top Moments:")
    for i, moment in enumerate(report['top_moments'][:3], 1):
        print(f"{i}. {moment['name']}")
        print(f"   {moment['description']}")
        print(f"   Engagement: {moment['engagement_score']:.2f} | Potential: {moment['mini_game_potential']:.2f}")
        print(f"   Play time: {moment['estimated_play_time']} min | Complexity: {moment['tutorial_complexity']}")
        print()
        
    print("Recommendations:")
    for rec in report['recommendations']:
        print(f"• {rec}")


if __name__ == "__main__":
    main()