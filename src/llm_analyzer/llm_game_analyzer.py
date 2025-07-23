"""
LLM-Powered Game Analyzer

Uses SOTA Large Language Models to intelligently analyze game repositories,
understand gameplay mechanics, and identify the most engaging moments.
"""
import os
import json
import base64
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import requests
from PIL import Image
import anthropic
import openai


@dataclass
class LLMAnalysisResult:
    """Results from LLM analysis"""
    game_summary: str
    core_mechanics: List[str]
    engagement_moments: List[Dict]
    visual_style: str
    target_audience: str
    mini_game_concepts: List[Dict]
    confidence_score: float


class LLMGameAnalyzer:
    """SOTA LLM-powered game analysis system"""
    
    def __init__(self, anthropic_api_key: str = None, openai_api_key: str = None):
        """Initialize with API keys for LLM services"""
        self.anthropic_client = None
        self.openai_client = None
        
        if anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        
        if openai_api_key:
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
    
    def analyze_game_with_llm(self, repo_path: Path, game_name: str) -> LLMAnalysisResult:
        """
        Use SOTA LLM to analyze game repository and identify engaging moments
        """
        # Step 1: Analyze code structure with LLM
        code_analysis = self._analyze_code_with_llm(repo_path)
        
        # Step 2: Analyze visual assets with LLM
        visual_analysis = self._analyze_assets_with_llm(repo_path)
        
        # Step 3: Generate engagement insights
        engagement_analysis = self._find_engaging_moments_with_llm(
            code_analysis, visual_analysis, game_name
        )
        
        # Step 4: Generate mini-game concepts
        mini_game_concepts = self._generate_mini_game_concepts_with_llm(
            engagement_analysis, visual_analysis
        )
        
        return LLMAnalysisResult(
            game_summary=engagement_analysis.get('summary', ''),
            core_mechanics=engagement_analysis.get('mechanics', []),
            engagement_moments=engagement_analysis.get('moments', []),
            visual_style=visual_analysis.get('style', ''),
            target_audience=engagement_analysis.get('audience', ''),
            mini_game_concepts=mini_game_concepts,
            confidence_score=engagement_analysis.get('confidence', 0.0)
        )
    
    def _analyze_code_with_llm(self, repo_path: Path) -> Dict:
        """Use LLM to understand game code and mechanics"""
        
        # Collect representative code files
        code_samples = self._collect_code_samples(repo_path)
        
        prompt = f"""
        You are an expert game developer analyzing a game repository. 
        
        Analyze these code files and identify:
        1. Core gameplay mechanics
        2. Player interaction systems
        3. Game progression elements
        4. Combat/challenge systems
        5. Most engaging gameplay loops
        
        Code samples:
        {code_samples}
        
        Provide analysis in JSON format:
        {{
            "mechanics": ["list of core mechanics"],
            "interactions": ["player interaction types"],
            "progression": ["progression systems"],
            "engagement_factors": ["what makes this game engaging"],
            "complexity_level": "simple/medium/complex",
            "genre": "detected genre",
            "key_files": ["most important code files"]
        }}
        """
        
        if self.anthropic_client:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return self._parse_json_response(response.content[0].text)
        
        elif self.openai_client:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            return self._parse_json_response(response.choices[0].message.content)
        
        else:
            raise ValueError("No LLM API key provided")
    
    def _analyze_assets_with_llm(self, repo_path: Path) -> Dict:
        """Use LLM to understand visual style and asset composition"""
        
        # Find key visual assets
        asset_info = self._collect_visual_assets(repo_path)
        
        prompt = f"""
        You are an expert game artist analyzing visual assets from a game.
        
        Asset information:
        {asset_info}
        
        Analyze the visual style and provide insights:
        1. Art style (pixel art, 3D, hand-drawn, etc.)
        2. Color palette and mood
        3. Character design approach
        4. UI/UX style
        5. Most visually striking elements
        6. Target audience based on visuals
        
        Provide analysis in JSON format:
        {{
            "art_style": "description of art style",
            "color_palette": ["main colors"],
            "mood": "visual mood/atmosphere",
            "character_style": "character design approach",
            "ui_style": "interface design style",
            "visual_highlights": ["most striking visual elements"],
            "target_demographic": "inferred target audience",
            "appeal_factors": ["what makes visuals appealing"]
        }}
        """
        
        if self.anthropic_client:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            return self._parse_json_response(response.content[0].text)
        
        elif self.openai_client:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            return self._parse_json_response(response.choices[0].message.content)
    
    def _find_engaging_moments_with_llm(self, code_analysis: Dict, visual_analysis: Dict, game_name: str) -> Dict:
        """Use LLM to identify the most engaging moments for mini-games"""
        
        prompt = f"""
        You are an expert in game design and player engagement, analyzing "{game_name}".
        
        Code Analysis:
        {json.dumps(code_analysis, indent=2)}
        
        Visual Analysis:
        {json.dumps(visual_analysis, indent=2)}
        
        Based on this analysis, identify the most engaging moments that would work 
        well as 5-10 minute interactive ads/mini-games. Consider:
        
        1. What are the most immediately satisfying gameplay loops?
        2. Which mechanics can be learned quickly but have depth?
        3. What moments would make players want to try the full game?
        4. Which elements showcase the game's unique appeal?
        5. What can be simplified without losing the core fun?
        
        Provide your analysis in JSON format:
        {{
            "summary": "2-3 sentence game summary",
            "mechanics": ["core mechanics list"],
            "audience": "target audience description",
            "moments": [
                {{
                    "name": "moment name",
                    "description": "detailed description",
                    "engagement_score": 0.0-1.0,
                    "complexity": "simple/medium/complex",
                    "duration_minutes": 5-10,
                    "core_mechanics": ["required mechanics"],
                    "appeal_factor": "why this is engaging",
                    "assets_needed": ["required visual/audio assets"]
                }}
            ],
            "confidence": 0.0-1.0
        }}
        
        Rank moments by engagement potential for interactive ads.
        """
        
        if self.anthropic_client:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            return self._parse_json_response(response.content[0].text)
        
        elif self.openai_client:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000
            )
            return self._parse_json_response(response.choices[0].message.content)
    
    def _generate_mini_game_concepts_with_llm(self, engagement_analysis: Dict, visual_analysis: Dict) -> List[Dict]:
        """Use LLM to generate specific mini-game implementation concepts"""
        
        top_moments = engagement_analysis.get('moments', [])[:3]  # Top 3 moments
        
        prompt = f"""
        You are an expert game developer tasked with creating mini-game concepts
        for interactive advertising.
        
        Top Engaging Moments:
        {json.dumps(top_moments, indent=2)}
        
        Visual Style:
        {json.dumps(visual_analysis, indent=2)}
        
        For each engaging moment, design a specific mini-game concept that:
        1. Can be played in 5-8 minutes
        2. Uses the original game's visual assets
        3. Captures the core appeal of the moment
        4. Is simple enough to learn without tutorial
        5. Creates desire to play the full game
        
        For each concept, provide:
        {{
            "concept_name": "mini-game name",
            "base_moment": "which moment this is based on",
            "game_description": "2-3 sentences describing gameplay",
            "core_loop": "what the player does repeatedly",
            "win_condition": "how the player wins",
            "difficulty_progression": "how challenge increases",
            "asset_requirements": ["specific assets needed"],
            "technical_complexity": "implementation difficulty",
            "estimated_engagement": 0.0-1.0,
            "conversion_potential": 0.0-1.0
        }}
        
        Return as JSON array of concepts.
        """
        
        if self.anthropic_client:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            result = self._parse_json_response(response.content[0].text)
            return result if isinstance(result, list) else [result]
        
        elif self.openai_client:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000
            )
            result = self._parse_json_response(response.choices[0].message.content)
            return result if isinstance(result, list) else [result]
    
    def _collect_code_samples(self, repo_path: Path) -> str:
        """Collect representative code samples for LLM analysis"""
        code_samples = []
        
        # Priority file patterns for game analysis
        priority_patterns = [
            '**/player*.gd', '**/player*.cs', '**/player*.py',
            '**/game*.gd', '**/game*.cs', '**/game*.py',
            '**/main*.gd', '**/main*.cs', '**/main*.py',
            '**/combat*.gd', '**/combat*.cs', '**/combat*.py',
            '**/level*.gd', '**/level*.cs', '**/level*.py'
        ]
        
        for pattern in priority_patterns:
            for file_path in repo_path.glob(pattern):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if len(content) > 100:  # Skip tiny files
                                code_samples.append(f"\n--- {file_path.name} ---\n{content[:2000]}")
                                if len(code_samples) >= 10:  # Limit for token efficiency
                                    break
                    except (UnicodeDecodeError, Exception):
                        continue
            if len(code_samples) >= 10:
                break
        
        # Fallback: get any code files
        if not code_samples:
            for ext in ['.gd', '.cs', '.py', '.js']:
                for file_path in repo_path.rglob(f'*{ext}'):
                    if file_path.is_file():
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if len(content) > 100:
                                    code_samples.append(f"\n--- {file_path.name} ---\n{content[:1500]}")
                                    if len(code_samples) >= 8:
                                        break
                        except (UnicodeDecodeError, Exception):
                            continue
                if code_samples:
                    break
        
        return '\n'.join(code_samples)
    
    def _collect_visual_assets(self, repo_path: Path) -> str:
        """Collect information about visual assets for LLM analysis"""
        asset_info = []
        
        # Find key visual files
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        
        for ext in image_extensions:
            for file_path in repo_path.rglob(f'*{ext}'):
                if file_path.is_file():
                    try:
                        # Get image dimensions and file size
                        with Image.open(file_path) as img:
                            width, height = img.size
                        
                        size_mb = file_path.stat().st_size / (1024 * 1024)
                        
                        asset_info.append({
                            'file': str(file_path.relative_to(repo_path)),
                            'dimensions': f'{width}x{height}',
                            'size_mb': round(size_mb, 2),
                            'category': self._categorize_asset_by_path(str(file_path))
                        })
                        
                        if len(asset_info) >= 20:  # Limit for analysis
                            break
                    except Exception:
                        continue
        
        return json.dumps(asset_info, indent=2)
    
    def _categorize_asset_by_path(self, file_path: str) -> str:
        """Categorize asset based on file path"""
        path_lower = file_path.lower()
        
        if any(keyword in path_lower for keyword in ['character', 'player', 'unit', 'avatar']):
            return 'character'
        elif any(keyword in path_lower for keyword in ['ui', 'gui', 'interface', 'button', 'menu']):
            return 'interface'
        elif any(keyword in path_lower for keyword in ['background', 'environment', 'terrain', 'map']):
            return 'environment'
        elif any(keyword in path_lower for keyword in ['icon', 'logo', 'symbol']):
            return 'icon'
        else:
            return 'unknown'
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON response from LLM, handling potential formatting issues"""
        try:
            # Try to find JSON block
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                json_text = response_text[start:end].strip()
            elif '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_text = response_text[start:end]
            else:
                json_text = response_text
            
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text[:500]}...")
            return {"error": "Failed to parse LLM response", "raw_response": response_text}


class LLMCodeGenerator:
    """Uses LLM to generate mini-game code based on analysis"""
    
    def __init__(self, anthropic_api_key: str = None, openai_api_key: str = None):
        self.anthropic_client = None
        self.openai_client = None
        
        if anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        
        if openai_api_key:
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
    
    def generate_mini_game_code(self, concept: Dict, assets_info: Dict) -> Dict[str, str]:
        """Generate complete mini-game code using LLM"""
        
        prompt = f"""
        You are an expert game developer. Generate a complete, functional mini-game 
        based on this concept:
        
        {json.dumps(concept, indent=2)}
        
        Available assets:
        {json.dumps(assets_info, indent=2)}
        
        Generate a complete Python game using Pygame that:
        1. Implements the core gameplay loop described in the concept
        2. Uses the available assets appropriately
        3. Has simple but engaging mechanics
        4. Can be played for 5-8 minutes
        5. Is mobile-friendly (touch controls)
        6. Includes win/lose conditions
        
        Provide the code in these files:
        1. main.py - Entry point and game loop
        2. game_engine.py - Core game mechanics
        3. ui_renderer.py - Visual rendering and UI
        4. asset_manager.py - Asset loading and management
        
        Return as JSON with file names as keys and code as values.
        Make sure the code is complete and functional.
        """
        
        if self.anthropic_client:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            return self._parse_code_response(response.content[0].text)
        
        elif self.openai_client:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000
            )
            return self._parse_code_response(response.choices[0].message.content)
    
    def _parse_code_response(self, response_text: str) -> Dict[str, str]:
        """Parse code files from LLM response"""
        try:
            # Try to find JSON block first
            if '```json' in response_text:
                start = response_text.find('```json') + 7
                end = response_text.find('```', start)
                json_text = response_text[start:end].strip()
                return json.loads(json_text)
            
            # Fallback: extract code blocks manually
            files = {}
            lines = response_text.split('\n')
            current_file = None
            current_code = []
            
            for line in lines:
                if line.startswith('```python') and any(fname in line for fname in ['main.py', 'game_engine.py', 'ui_renderer.py', 'asset_manager.py']):
                    if current_file:
                        files[current_file] = '\n'.join(current_code)
                    current_file = line.split('# ')[-1] if '# ' in line else 'main.py'
                    current_code = []
                elif line.startswith('```') and current_file:
                    files[current_file] = '\n'.join(current_code)
                    current_file = None
                    current_code = []
                elif current_file:
                    current_code.append(line)
            
            if current_file and current_code:
                files[current_file] = '\n'.join(current_code)
            
            return files
            
        except Exception as e:
            return {"error": f"Failed to parse code response: {e}", "raw_response": response_text}