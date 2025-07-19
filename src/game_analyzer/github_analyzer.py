"""
GitHub Repository Analyzer

Downloads and analyzes open source game repositories
"""
import os
import json
from typing import Dict, List, Optional
from pathlib import Path
import git
import requests
from dataclasses import dataclass


@dataclass
class GameRepository:
    """Represents a game repository with metadata"""
    name: str
    url: str
    stars: int
    engine: str  # Unity, Godot, Custom, etc.
    genre: str
    language: str
    description: str


class GitHubAnalyzer:
    """Analyzes GitHub game repositories"""
    
    def __init__(self, data_dir: str = "data/repositories"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def clone_repository(self, repo_url: str, local_name: str) -> Path:
        """Clone a repository locally for analysis"""
        repo_path = self.data_dir / local_name
        
        if repo_path.exists():
            print(f"Repository {local_name} already exists")
            return repo_path
            
        print(f"Cloning {repo_url} to {repo_path}")
        git.Repo.clone_from(repo_url, repo_path)
        return repo_path
        
    def analyze_repository_structure(self, repo_path: Path) -> Dict:
        """Analyze repository file structure and identify game components"""
        analysis = {
            "total_files": 0,
            "code_files": {},
            "asset_files": {},
            "config_files": [],
            "readme_info": None,
            "engine_detected": None
        }
        
        # File type mappings
        code_extensions = {'.cs', '.js', '.py', '.cpp', '.h', '.gd', '.cs'}
        asset_extensions = {'.png', '.jpg', '.jpeg', '.fbx', '.obj', '.wav', '.ogg', '.mp3'}
        config_extensions = {'.json', '.yaml', '.yml', '.xml', '.ini', '.cfg'}
        
        for file_path in repo_path.rglob('*'):
            if file_path.is_file():
                analysis["total_files"] += 1
                ext = file_path.suffix.lower()
                
                if ext in code_extensions:
                    analysis["code_files"][ext] = analysis["code_files"].get(ext, 0) + 1
                elif ext in asset_extensions:
                    analysis["asset_files"][ext] = analysis["asset_files"].get(ext, 0) + 1
                elif ext in config_extensions:
                    analysis["config_files"].append(str(file_path.relative_to(repo_path)))
                    
        # Detect game engine
        if (repo_path / "Assets").exists() or any(repo_path.glob("*.unity")):
            analysis["engine_detected"] = "Unity"
        elif (repo_path / "project.godot").exists():
            analysis["engine_detected"] = "Godot"
        elif (repo_path / "CMakeLists.txt").exists():
            analysis["engine_detected"] = "Custom/C++"
            
        # Read README
        for readme_file in ["README.md", "README.txt", "README.rst"]:
            readme_path = repo_path / readme_file
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        analysis["readme_info"] = f.read()[:1000]  # First 1000 chars
                    break
                except UnicodeDecodeError:
                    pass
                    
        return analysis
        
    def get_recommended_repositories(self) -> List[GameRepository]:
        """Return list of recommended open source games for analysis"""
        return [
            GameRepository(
                name="hypersomnia",
                url="https://github.com/TeamHypersomnia/Hypersomnia",
                stars=1100,
                engine="Custom/C++",
                genre="Action",
                language="C++",
                description="Fast-paced top-down arena shooter"
            ),
            GameRepository(
                name="anyrpg",
                url="https://github.com/AnyRPG/AnyRPGCore",
                stars=1500,
                engine="Unity",
                genre="RPG",
                language="C#",
                description="Open source RPG engine"
            ),
            GameRepository(
                name="godot-open-rpg",
                url="https://github.com/gdquest-demos/godot-open-rpg",
                stars=800,
                engine="Godot",
                genre="RPG", 
                language="GDScript",
                description="Turn-based RPG demo"
            ),
            GameRepository(
                name="tanks-of-freedom",
                url="https://github.com/w84death/Tanks-of-Freedom",
                stars=1000,
                engine="Godot",
                genre="Strategy",
                language="GDScript",
                description="Turn-based strategy game"
            )
        ]