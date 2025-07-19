"""
Moment Analyzer

Identifies the most engaging gameplay moments from analyzed games
that would work well as short interactive ads
"""
import json
import re
from typing import Dict, List, Tuple
from pathlib import Path
from dataclasses import dataclass


@dataclass
class EngagingMoment:
    """Represents a potentially engaging gameplay moment"""
    name: str
    description: str
    engagement_score: float
    mini_game_potential: float
    required_assets: List[str]
    gameplay_mechanics: List[str]
    estimated_play_time: int  # in minutes
    tutorial_complexity: str  # simple, medium, complex


class MomentAnalyzer:
    """Analyzes game code and assets to find engaging moments"""
    
    def __init__(self):
        self.engagement_patterns = {
            # Combat patterns
            'combat': {
                'patterns': ['attack', 'damage', 'health', 'weapon', 'fight', 'battle'],
                'weight': 0.9,
                'description': 'Combat interactions'
            },
            # Decision making
            'strategy': {
                'patterns': ['move', 'turn', 'strategy', 'tactical', 'decision'],
                'weight': 0.8,
                'description': 'Strategic decision points'
            },
            # Resource management
            'resource': {
                'patterns': ['spawn', 'build', 'resource', 'money', 'cost', 'upgrade'],
                'weight': 0.7,
                'description': 'Resource management'
            },
            # Competition
            'competitive': {
                'patterns': ['score', 'win', 'lose', 'victory', 'defeat', 'rank'],
                'weight': 0.85,
                'description': 'Competitive elements'
            },
            # Progression
            'progression': {
                'patterns': ['level', 'unlock', 'achievement', 'progress', 'advance'],
                'weight': 0.6,
                'description': 'Progression systems'
            }
        }
        
    def analyze_game_moments(self, repo_path: Path, analysis_data: Dict) -> List[EngagingMoment]:
        """Analyze game to identify engaging moments"""
        moments = []
        
        # Analyze code for gameplay patterns
        code_moments = self._analyze_code_patterns(repo_path)
        
        # Analyze assets for visual engagement
        asset_moments = self._analyze_asset_potential(analysis_data)
        
        # Generate specific moments for this game type
        if analysis_data.get('repository', {}).get('genre') == 'Strategy':
            moments.extend(self._generate_strategy_moments(repo_path, analysis_data))
        
        # Combine and score all moments
        all_moments = code_moments + asset_moments + moments
        return self._score_and_filter_moments(all_moments, analysis_data)
        
    def _analyze_code_patterns(self, repo_path: Path) -> List[EngagingMoment]:
        """Analyze code files for engagement patterns"""
        moments = []
        script_files = list(repo_path.rglob('*.gd')) + list(repo_path.rglob('*.cs'))
        
        pattern_scores = {pattern: 0 for pattern in self.engagement_patterns}
        
        for script_file in script_files:
            try:
                with open(script_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    
                    for pattern_name, pattern_data in self.engagement_patterns.items():
                        for keyword in pattern_data['patterns']:
                            matches = len(re.findall(r'\b' + keyword + r'\b', content))
                            pattern_scores[pattern_name] += matches * pattern_data['weight']
                            
            except (UnicodeDecodeError, Exception):
                continue
                
        # Create moments from high-scoring patterns
        for pattern_name, score in pattern_scores.items():
            if score > 10:  # Threshold for significant presence
                pattern_data = self.engagement_patterns[pattern_name]
                moments.append(EngagingMoment(
                    name=f"{pattern_name.title()} System",
                    description=pattern_data['description'],
                    engagement_score=min(score / 100, 1.0),
                    mini_game_potential=pattern_data['weight'],
                    required_assets=[],
                    gameplay_mechanics=[pattern_name],
                    estimated_play_time=5,
                    tutorial_complexity="medium"
                ))
                
        return moments
        
    def _analyze_asset_potential(self, analysis_data: Dict) -> List[EngagingMoment]:
        """Analyze visual assets for mini-game potential"""
        moments = []
        asset_analysis = analysis_data.get('asset_analysis', {})
        character_assets = analysis_data.get('character_assets', [])
        
        # Character-based moments
        if len(character_assets) >= 2:
            moments.append(EngagingMoment(
                name="Character Showcase",
                description="Interactive character selection and preview",
                engagement_score=0.7,
                mini_game_potential=0.8,
                required_assets=[asset['path'] for asset in character_assets],
                gameplay_mechanics=['selection', 'preview'],
                estimated_play_time=3,
                tutorial_complexity="simple"
            ))
            
        # UI-heavy moments suggest menu interactions
        ui_assets = asset_analysis.get('by_category', {}).get('ui', 0)
        if ui_assets > 20:
            moments.append(EngagingMoment(
                name="Base Building",
                description="Quick base construction and management",
                engagement_score=0.6,
                mini_game_potential=0.7,
                required_assets=[],
                gameplay_mechanics=['building', 'management'],
                estimated_play_time=7,
                tutorial_complexity="medium"
            ))
            
        return moments
        
    def _generate_strategy_moments(self, repo_path: Path, analysis_data: Dict) -> List[EngagingMoment]:
        """Generate strategy game specific moments"""
        moments = []
        
        # Analyze specific strategy patterns
        has_units = any('unit' in asset['path'] for asset in analysis_data.get('character_assets', []))
        has_buildings = 'buildings' in str(repo_path)
        has_ai = (repo_path / 'scripts' / 'ai').exists()
        
        if has_units and has_ai:
            moments.append(EngagingMoment(
                name="Quick Skirmish",
                description="Fast-paced tactical battle with limited units",
                engagement_score=0.9,
                mini_game_potential=0.95,
                required_assets=['units_spritesheet.png', 'terrain assets'],
                gameplay_mechanics=['combat', 'movement', 'tactics'],
                estimated_play_time=8,
                tutorial_complexity="medium"
            ))
            
        if has_buildings:
            moments.append(EngagingMoment(
                name="Territory Rush",
                description="Capture and hold strategic points",
                engagement_score=0.85,
                mini_game_potential=0.9,
                required_assets=['building sprites', 'unit sprites'],
                gameplay_mechanics=['capture', 'defense', 'resource'],
                estimated_play_time=6,
                tutorial_complexity="simple"
            ))
            
        # Campaign moments
        campaign_dir = repo_path / 'maps' / 'campaign'
        if campaign_dir.exists():
            campaign_files = list(campaign_dir.glob('*.gd'))
            moments.append(EngagingMoment(
                name="Story Mission Sampler",
                description="Play key moments from campaign missions",
                engagement_score=0.8,
                mini_game_potential=0.85,
                required_assets=['all game assets'],
                gameplay_mechanics=['story', 'objectives', 'combat'],
                estimated_play_time=10,
                tutorial_complexity="complex"
            ))
            
        return moments
        
    def _score_and_filter_moments(self, moments: List[EngagingMoment], analysis_data: Dict) -> List[EngagingMoment]:
        """Score and filter moments based on feasibility"""
        # Filter by play time (5-10 minutes)
        valid_moments = [m for m in moments if 3 <= m.estimated_play_time <= 10]
        
        # Sort by engagement potential
        valid_moments.sort(key=lambda x: x.engagement_score * x.mini_game_potential, reverse=True)
        
        # Return top candidates
        return valid_moments[:5]
        
    def generate_moment_report(self, moments: List[EngagingMoment], game_name: str) -> Dict:
        """Generate detailed report of engaging moments"""
        return {
            "game": game_name,
            "total_moments_found": len(moments),
            "top_moments": [
                {
                    "name": moment.name,
                    "description": moment.description,
                    "engagement_score": moment.engagement_score,
                    "mini_game_potential": moment.mini_game_potential,
                    "estimated_play_time": moment.estimated_play_time,
                    "tutorial_complexity": moment.tutorial_complexity,
                    "required_assets": moment.required_assets,
                    "gameplay_mechanics": moment.gameplay_mechanics,
                    "feasibility_score": moment.engagement_score * moment.mini_game_potential
                }
                for moment in moments
            ],
            "recommendations": self._generate_recommendations(moments)
        }
        
    def _generate_recommendations(self, moments: List[EngagingMoment]) -> List[str]:
        """Generate implementation recommendations"""
        recommendations = []
        
        if not moments:
            return ["No suitable moments found for mini-game extraction"]
            
        top_moment = moments[0]
        
        if top_moment.tutorial_complexity == "simple":
            recommendations.append("Start with the highest-rated simple moment for quick implementation")
        else:
            recommendations.append("Consider simplifying the top moment for faster development")
            
        if any(m.estimated_play_time <= 5 for m in moments):
            recommendations.append("Focus on shorter moments for better ad performance")
            
        if len(set(m.gameplay_mechanics[0] for m in moments if m.gameplay_mechanics)) > 3:
            recommendations.append("Multiple gameplay types available - create variety pack")
        else:
            recommendations.append("Consistent gameplay theme - focus on perfecting one mechanic")
            
        return recommendations