#!/usr/bin/env python3
"""
Robust LLM Test with Retry Logic

Tests SOTA LLM analysis with better error handling and retry logic.
"""
import sys
import json
import os
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from llm_analyzer.robust_llm_client import RobustLLMClient


def test_llm_analysis():
    """Test LLM analysis with robust error handling"""
    
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
    
    if not anthropic_key and not openai_key and not gemini_key:
        print("❌ No API keys provided")
        print("Usage: python scripts/robust_llm_test.py --anthropic-key sk-ant-...")
        print("   or: python scripts/robust_llm_test.py --openai-key sk-...")
        print("   or: python scripts/robust_llm_test.py --gemini-key AIza...")
        print("   or: Set environment variables: ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY")
        return
    
    print("🤖 SOTA LLM Game Analysis Test")
    print("=" * 40)
    
    if anthropic_key:
        print("✅ Claude API key found")
    if openai_key:
        print("✅ GPT-4 API key found")
    if gemini_key:
        print("✅ Gemini API key found")
    print()
    
    # Initialize robust LLM client with all providers
    client = RobustLLMClient(anthropic_key, openai_key, gemini_key)
    
    # Check if Tanks of Freedom repository exists
    repo_path = Path("data/repositories/tanks-of-freedom")
    if not repo_path.exists():
        print(f"❌ Repository not found: {repo_path}")
        print("Please run: python scripts/analyze_game.py tanks-of-freedom")
        return
    
    # Step 1: Quick code analysis
    print("🔍 Step 1: LLM Code Analysis")
    
    # Collect sample code
    code_samples = []
    for pattern in ['**/game*.gd', '**/player*.gd', '**/unit*.gd']:
        for file_path in repo_path.glob(pattern):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:1000]  # First 1000 chars
                        code_samples.append(f"File: {file_path.name}\n{content}")
                        if len(code_samples) >= 3:  # Limit samples
                            break
                except:
                    continue
    
    if not code_samples:
        print("❌ No code samples found")
        return
    
    code_prompt = f"""
    Analyze this game code from "Tanks of Freedom" and identify:
    1. Core gameplay mechanics
    2. Most engaging elements
    3. Best mini-game concept (5-8 minutes)
    
    Code samples:
    {chr(10).join(code_samples[:2])}  
    
    Respond with JSON:
    {{
        "game_type": "genre description",
        "core_mechanics": ["mechanic1", "mechanic2"],
        "engagement_factors": ["factor1", "factor2"], 
        "best_mini_game": {{
            "name": "concept name",
            "description": "2 sentence description",
            "duration": "5-8 minutes",
            "appeal": "why this is engaging"
        }}
    }}
    """
    
    response = client.query_simple(code_prompt, "Code Analysis")
    
    if "error" in response:
        print(f"❌ Analysis failed: {response['error']}")
        return
    
    print("✅ LLM Analysis Complete!")
    print(f"📡 Model used: {response.get('_model_used', 'Unknown')}")
    print()
    
    # Display results
    print("🎮 Game Analysis Results:")
    print(f"Type: {response.get('game_type', 'Unknown')}")
    print()
    
    print("⚙️ Core Mechanics:")
    for mechanic in response.get('core_mechanics', []):
        print(f"  • {mechanic}")
    print()
    
    print("🎯 Engagement Factors:")
    for factor in response.get('engagement_factors', []):
        print(f"  • {factor}")
    print()
    
    print("💡 Best Mini-Game Concept:")
    mini_game = response.get('best_mini_game', {})
    print(f"  Name: {mini_game.get('name', 'Unknown')}")
    print(f"  Description: {mini_game.get('description', 'No description')}")
    print(f"  Duration: {mini_game.get('duration', 'Unknown')}")
    print(f"  Appeal: {mini_game.get('appeal', 'Unknown')}")
    print()
    
    # Step 2: Compare with traditional analysis
    print("🔬 Comparison with Traditional Analysis:")
    print()
    
    try:
        # Load traditional analysis if available
        traditional_file = Path("data/tanks-of-freedom_moments.json")
        if traditional_file.exists():
            with open(traditional_file, 'r') as f:
                traditional = json.load(f)
            
            print("📊 Traditional System:")
            print(f"  Method: Rule-based keyword counting")
            print(f"  Top concept: {traditional['top_moments'][0]['name']}")
            print(f"  Score: {traditional['top_moments'][0]['feasibility_score']:.3f}")
            print()
            
            print("🤖 LLM System:")
            print(f"  Method: Semantic code analysis")
            print(f"  Top concept: {mini_game.get('name', 'Unknown')}")
            print(f"  Quality: Creative, contextual concept generation")
            print()
            
    except Exception as e:
        print(f"Note: Traditional analysis not found ({e})")
    
    # Save LLM results
    output_path = Path("data/llm_analysis_results.json")
    with open(output_path, 'w') as f:
        json.dump({
            "timestamp": str(time.time()),
            "model_used": response.get('_model_used', 'Unknown'),
            "analysis": response,
            "status": "success"
        }, f, indent=2)
    
    print(f"💾 Results saved to: {output_path}")
    print()
    print("🎉 LLM Analysis Complete!")
    print()
    print("🔍 Key Differences Observed:")
    print("  Traditional: Simple pattern matching → numeric scores")
    print("  LLM System: Semantic understanding → creative concepts")
    print("  Quality: LLM provides game designer-level insights!")


if __name__ == "__main__":
    test_llm_analysis()