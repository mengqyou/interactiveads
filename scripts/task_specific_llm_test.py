#!/usr/bin/env python3
"""
Task-Specific LLM Test

Tests Claude Sonnet 4 for code analysis and Gemini 2.5 Pro for creative generation.
"""
import sys
import json
import os
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from llm_analyzer.robust_llm_client import RobustLLMClient


def test_task_specific_routing():
    """Test task-specific LLM routing: Claude for code, Gemini for creativity"""
    
    # Get API keys
    anthropic_key = None
    openai_key = None
    gemini_key = None
    
    for i, arg in enumerate(sys.argv):
        if arg == "--anthropic-key" and i + 1 < len(sys.argv):
            anthropic_key = sys.argv[i + 1]
        elif arg == "--openai-key" and i + 1 < len(sys.argv):
            openai_key = sys.argv[i + 1]
        elif arg == "--gemini-key" and i + 1 < len(sys.argv):
            gemini_key = sys.argv[i + 1]
    
    # Check environment variables
    if not anthropic_key:
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if not openai_key:
        openai_key = os.getenv('OPENAI_API_KEY')
    if not gemini_key:
        gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not anthropic_key and not gemini_key:
        print("❌ Need Claude and Gemini API keys for task-specific routing")
        print("Usage: python scripts/task_specific_llm_test.py \\")
        print("         --anthropic-key sk-ant-... \\")
        print("         --gemini-key AIza...")
        return
    
    print("🎯 Task-Specific LLM Routing Test")
    print("=" * 50)
    print("📋 Priority Configuration:")
    print("  🧠 Claude Sonnet 4 → Code Analysis")
    print("  🎨 Gemini 2.5 Pro → Creative Generation")
    print("  🔄 GPT-4.1 → Final backup")
    print()
    
    # Initialize client with all providers
    client = RobustLLMClient(anthropic_key, openai_key, gemini_key)
    
    # Check if Tanks of Freedom repository exists
    repo_path = Path("data/repositories/tanks-of-freedom")
    if not repo_path.exists():
        print(f"❌ Repository not found: {repo_path}")
        print("Please run: python scripts/analyze_game.py tanks-of-freedom")
        return
    
    # Collect sample code for analysis
    print("📁 Loading game code samples...")
    code_samples = []
    for pattern in ['**/game*.gd', '**/player*.gd', '**/unit*.gd']:
        for file_path in repo_path.glob(pattern):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:800]  # First 800 chars
                        code_samples.append(f"File: {file_path.name}\\n{content}")
                        if len(code_samples) >= 2:  # Limit samples
                            break
                except:
                    continue
    
    if not code_samples:
        print("❌ No code samples found")
        return
    
    # Task 1: Code Analysis with Claude Sonnet 4
    print("🧠 TASK 1: Code Analysis (Claude Sonnet 4)")
    print("-" * 40)
    
    code_analysis_prompt = f"""
    You are an expert game developer analyzing this tactical strategy game code.
    
    Code samples from "Tanks of Freedom":
    {chr(10).join(code_samples)}
    
    Analyze and provide JSON response:
    {{
        "game_engine": "engine type detected",
        "programming_patterns": ["pattern1", "pattern2"],
        "core_mechanics": ["mechanic1", "mechanic2"],
        "technical_complexity": "low/medium/high",
        "code_quality_score": 0.8,
        "optimization_potential": ["area1", "area2"]
    }}
    """
    
    code_response = client.query_code_analysis(code_analysis_prompt, max_tokens=1500)
    
    if code_response.success:
        print(f"✅ Code Analysis Complete!")
        print(f"🤖 Model: {code_response.model_used}")
        print()
        
        # Parse and display results
        try:
            if '{' in code_response.content:
                start = code_response.content.find('{')
                end = code_response.content.rfind('}') + 1
                json_text = code_response.content[start:end]
                analysis_results = json.loads(json_text)
                
                print("📊 Code Analysis Results:")
                print(f"  Engine: {analysis_results.get('game_engine', 'Unknown')}")
                print(f"  Quality Score: {analysis_results.get('code_quality_score', 'N/A')}")
                print(f"  Complexity: {analysis_results.get('technical_complexity', 'Unknown')}")
                
                print("⚙️ Core Mechanics:")
                for mechanic in analysis_results.get('core_mechanics', []):
                    print(f"    • {mechanic}")
            else:
                print("📝 Raw Analysis:")
                print(code_response.content[:300] + "...")
                
        except json.JSONDecodeError:
            print("📝 Analysis Summary:")
            print(code_response.content[:300] + "...")
    else:
        print(f"❌ Code analysis failed: {code_response.error}")
        return
    
    print()
    print("🎨 TASK 2: Creative Generation (Gemini 2.5 Pro)")
    print("-" * 40)
    
    # Task 2: Creative Generation with Gemini 2.5 Pro
    creative_prompt = f"""
    You are a creative game designer who creates engaging mini-games for advertising.
    
    Based on this tactical strategy game analysis, generate creative mini-game concepts:
    
    Game Type: Turn-based tactical combat with military units
    Core Appeal: Strategic positioning and resource management
    Target Duration: 5-8 minutes for advertising
    
    Create JSON response with 2 creative mini-game concepts:
    {{
        "mini_games": [
            {{
                "name": "Creative Concept Name",
                "tagline": "Catchy one-liner",
                "core_hook": "What makes this instantly engaging",
                "gameplay_flow": "Brief 3-step progression",
                "mobile_adaptation": "How it works on touch devices",
                "viral_factor": "What makes players share this"
            }}
        ],
        "creative_insights": [
            "Insight about player psychology",
            "Marketing appeal factor"
        ]
    }}
    """
    
    creative_response = client.query_creative_generation(creative_prompt, max_tokens=1500)
    
    if creative_response.success:
        print(f"✅ Creative Generation Complete!")
        print(f"🎨 Model: {creative_response.model_used}")
        print()
        
        # Parse and display results
        try:
            if '{' in creative_response.content:
                start = creative_response.content.find('{')
                end = creative_response.content.rfind('}') + 1
                json_text = creative_response.content[start:end]
                creative_results = json.loads(json_text)
                
                print("💡 Creative Mini-Game Concepts:")
                for i, game in enumerate(creative_results.get('mini_games', []), 1):
                    print(f"  🎮 Concept {i}: {game.get('name', 'Unnamed')}")
                    print(f"    Tagline: {game.get('tagline', 'N/A')}")
                    print(f"    Hook: {game.get('core_hook', 'N/A')}")
                    print()
                
                print("🧠 Creative Insights:")
                for insight in creative_results.get('creative_insights', []):
                    print(f"    • {insight}")
                    
            else:
                print("📝 Raw Creative Response:")
                print(creative_response.content[:400] + "...")
                
        except json.JSONDecodeError:
            print("📝 Creative Summary:")
            print(creative_response.content[:400] + "...")
    else:
        print(f"❌ Creative generation failed: {creative_response.error}")
    
    print()
    print("🎯 TASK-SPECIFIC ROUTING COMPLETE!")
    print("=" * 50)
    print("📈 Results:")
    print(f"  Code Analysis: {'✅ Claude Sonnet 4' if code_response.success else '❌ Failed'}")
    print(f"  Creative Generation: {'✅ Gemini 2.5 Pro' if creative_response.success else '❌ Failed'}")
    print()
    
    # Save combined results
    output_data = {
        "timestamp": str(time.time()),
        "task_routing": {
            "code_analysis": {
                "model": code_response.model_used,
                "success": code_response.success,
                "content": code_response.content[:500] + "..." if len(code_response.content) > 500 else code_response.content
            },
            "creative_generation": {
                "model": creative_response.model_used, 
                "success": creative_response.success,
                "content": creative_response.content[:500] + "..." if len(creative_response.content) > 500 else creative_response.content
            }
        },
        "configuration": {
            "priority_order": "Claude Sonnet 4 → Gemini 2.5 Pro → GPT-4.1",
            "task_specialization": "Enabled"
        }
    }
    
    output_path = Path("data/task_specific_results.json")
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"💾 Results saved to: {output_path}")
    print()
    print("🚀 Next: Test with your API keys to see both models in action!")


if __name__ == "__main__":
    test_task_specific_routing()