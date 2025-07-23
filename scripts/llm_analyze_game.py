#!/usr/bin/env python3
"""
LLM-Powered Game Analysis Script

Uses SOTA Large Language Models to intelligently analyze games
and generate engaging mini-game concepts.

Usage: python scripts/llm_analyze_game.py <game_name> --anthropic-key <key>
"""
import sys
import json
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from llm_analyzer.llm_game_analyzer import LLMGameAnalyzer, LLMCodeGenerator


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/llm_analyze_game.py <game_name> [--anthropic-key KEY] [--openai-key KEY]")
        print("Example: python scripts/llm_analyze_game.py tanks-of-freedom --anthropic-key sk-...")
        return
    
    game_name = sys.argv[1]
    
    # Parse API keys from command line
    anthropic_key = None
    openai_key = None
    
    for i, arg in enumerate(sys.argv):
        if arg == "--anthropic-key" and i + 1 < len(sys.argv):
            anthropic_key = sys.argv[i + 1]
        elif arg == "--openai-key" and i + 1 < len(sys.argv):
            openai_key = sys.argv[i + 1]
    
    # Also check environment variables
    if not anthropic_key:
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if not openai_key:
        openai_key = os.getenv('OPENAI_API_KEY')
    
    if not anthropic_key and not openai_key:
        print("❌ Error: No API key provided")
        print("Options:")
        print("1. Use command line: --anthropic-key sk-... or --openai-key sk-...")
        print("2. Set environment variable: ANTHROPIC_API_KEY or OPENAI_API_KEY")
        print("3. Get API keys from:")
        print("   - Anthropic Claude: https://console.anthropic.com/")
        print("   - OpenAI GPT-4: https://platform.openai.com/api-keys")
        return
    
    # Check if game repository exists
    repo_path = Path("data/repositories") / game_name
    if not repo_path.exists():
        print(f"❌ Game repository not found: {repo_path}")
        print(f"Please run: python scripts/analyze_game.py {game_name}")
        return
    
    print(f"🤖 LLM Analysis Starting for: {game_name}")
    print(f"Repository: {repo_path}")
    print(f"Using: {'Claude' if anthropic_key else 'GPT-4'}")
    print()
    
    try:
        # Initialize LLM analyzer
        analyzer = LLMGameAnalyzer(
            anthropic_api_key=anthropic_key,
            openai_api_key=openai_key
        )
        
        print("🔍 Step 1: LLM analyzing game code and mechanics...")
        # Perform intelligent analysis
        analysis_result = analyzer.analyze_game_with_llm(repo_path, game_name)
        
        print("✅ LLM Analysis Complete!")
        print(f"Confidence Score: {analysis_result.confidence_score:.2f}")
        print()
        
        # Display results
        print("🎮 Game Summary:")
        print(f"  {analysis_result.game_summary}")
        print()
        
        print("⚙️ Core Mechanics:")
        for mechanic in analysis_result.core_mechanics:
            print(f"  • {mechanic}")
        print()
        
        print("🎯 Top Engaging Moments:")
        for i, moment in enumerate(analysis_result.engagement_moments[:3], 1):
            print(f"  {i}. {moment.get('name', 'Unknown')}")
            print(f"     {moment.get('description', 'No description')}")
            print(f"     Engagement: {moment.get('engagement_score', 0):.2f}")
            print(f"     Duration: {moment.get('duration_minutes', 0)} minutes")
            print()
        
        print("🎨 Visual Style:")
        print(f"  {analysis_result.visual_style}")
        print()
        
        print("👥 Target Audience:")
        print(f"  {analysis_result.target_audience}")
        print()
        
        print("💡 Mini-Game Concepts:")
        for i, concept in enumerate(analysis_result.mini_game_concepts, 1):
            print(f"  {i}. {concept.get('concept_name', 'Unnamed Concept')}")
            print(f"     {concept.get('game_description', 'No description')}")
            print(f"     Engagement: {concept.get('estimated_engagement', 0):.2f}")
            print(f"     Conversion Potential: {concept.get('conversion_potential', 0):.2f}")
            print()
        
        # Save detailed results
        output_path = Path("data") / f"{game_name}_llm_analysis.json"
        with open(output_path, 'w') as f:
            json.dump({
                "game_name": game_name,
                "analysis_result": {
                    "game_summary": analysis_result.game_summary,
                    "core_mechanics": analysis_result.core_mechanics,
                    "engagement_moments": analysis_result.engagement_moments,
                    "visual_style": analysis_result.visual_style,
                    "target_audience": analysis_result.target_audience,
                    "mini_game_concepts": analysis_result.mini_game_concepts,
                    "confidence_score": analysis_result.confidence_score
                },
                "llm_model": "Claude" if anthropic_key else "GPT-4",
                "timestamp": str(Path().cwd())
            }, f, indent=2)
        
        print(f"📄 Detailed analysis saved to: {output_path}")
        print()
        
        # Ask if user wants to generate code for top concept
        if analysis_result.mini_game_concepts:
            top_concept = analysis_result.mini_game_concepts[0]
            print(f"🚀 Generate code for top concept: '{top_concept.get('concept_name', 'Unknown')}'?")
            response = input("Generate mini-game code? (y/N): ").strip().lower()
            
            if response == 'y':
                print("🔧 Step 2: LLM generating mini-game code...")
                
                code_generator = LLMCodeGenerator(
                    anthropic_api_key=anthropic_key,
                    openai_api_key=openai_key
                )
                
                # Collect asset information
                assets_info = {"available_assets": "Character sprites, UI elements, sounds from original game"}
                
                generated_code = code_generator.generate_mini_game_code(top_concept, assets_info)
                
                if "error" not in generated_code:
                    # Save generated code files
                    generated_dir = Path("generated_games") / f"{game_name}_{top_concept.get('concept_name', 'concept').lower().replace(' ', '_')}"
                    generated_dir.mkdir(parents=True, exist_ok=True)
                    
                    for filename, code in generated_code.items():
                        if filename.endswith('.py'):
                            with open(generated_dir / filename, 'w') as f:
                                f.write(code)
                    
                    print(f"✅ Mini-game code generated in: {generated_dir}")
                    print(f"🎮 To play: cd {generated_dir} && python main.py")
                else:
                    print(f"❌ Code generation failed: {generated_code.get('error', 'Unknown error')}")
        
        print("\n🎉 LLM Analysis Complete!")
        print("Compare this intelligent analysis with the rule-based version to see")
        print("the difference between SOTA LLM capabilities and traditional programming!")
        
    except Exception as e:
        print(f"❌ Error during LLM analysis: {e}")
        print("Check your API key and internet connection")


if __name__ == "__main__":
    main()