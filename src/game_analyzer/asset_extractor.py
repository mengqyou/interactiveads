"""
Asset Extractor

Extracts and analyzes game assets (images, audio, models)
to identify characters, UI elements, and gameplay assets
"""
import os
import json
from typing import Dict, List, Tuple
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from dataclasses import dataclass


@dataclass
class GameAsset:
    """Represents a game asset with metadata"""
    path: str
    type: str  # image, audio, model, animation
    category: str  # character, ui, environment, effect
    dimensions: Tuple[int, int] = None
    size_bytes: int = 0
    description: str = ""


class AssetExtractor:
    """Extracts and categorizes game assets"""
    
    def __init__(self):
        self.supported_image_formats = {'.png', '.jpg', '.jpeg', '.bmp', '.tga', '.gif'}
        self.supported_audio_formats = {'.wav', '.ogg', '.mp3', '.m4a'}
        self.supported_model_formats = {'.fbx', '.obj', '.dae', '.blend', '.3ds'}
        
    def extract_assets(self, repo_path: Path) -> List[GameAsset]:
        """Extract all assets from repository"""
        assets = []
        
        for file_path in repo_path.rglob('*'):
            if file_path.is_file():
                asset = self._analyze_file(file_path, repo_path)
                if asset:
                    assets.append(asset)
                    
        return assets
        
    def _analyze_file(self, file_path: Path, repo_root: Path) -> GameAsset:
        """Analyze individual file and create asset object"""
        ext = file_path.suffix.lower()
        relative_path = str(file_path.relative_to(repo_root))
        
        if ext in self.supported_image_formats:
            return self._analyze_image(file_path, relative_path)
        elif ext in self.supported_audio_formats:
            return self._analyze_audio(file_path, relative_path)
        elif ext in self.supported_model_formats:
            return self._analyze_model(file_path, relative_path)
        
        return None
        
    def _analyze_image(self, file_path: Path, relative_path: str) -> GameAsset:
        """Analyze image file"""
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                
            # Categorize based on path and filename
            category = self._categorize_image(relative_path, (width, height))
            
            return GameAsset(
                path=relative_path,
                type="image",
                category=category,
                dimensions=(width, height),
                size_bytes=file_path.stat().st_size
            )
        except Exception as e:
            print(f"Error analyzing image {file_path}: {e}")
            return None
            
    def _analyze_audio(self, file_path: Path, relative_path: str) -> GameAsset:
        """Analyze audio file"""
        category = self._categorize_audio(relative_path)
        
        return GameAsset(
            path=relative_path,
            type="audio",
            category=category,
            size_bytes=file_path.stat().st_size
        )
        
    def _analyze_model(self, file_path: Path, relative_path: str) -> GameAsset:
        """Analyze 3D model file"""
        category = self._categorize_model(relative_path)
        
        return GameAsset(
            path=relative_path,
            type="model",
            category=category,
            size_bytes=file_path.stat().st_size
        )
        
    def _categorize_image(self, path: str, dimensions: Tuple[int, int]) -> str:
        """Categorize image based on path and properties"""
        path_lower = path.lower()
        width, height = dimensions
        
        # UI elements are typically small or have specific naming
        if any(keyword in path_lower for keyword in ['ui', 'gui', 'button', 'icon', 'menu']):
            return "ui"
            
        # Characters often have specific naming or are in character folders
        if any(keyword in path_lower for keyword in ['character', 'player', 'enemy', 'sprite']):
            return "character"
            
        # Large images are likely backgrounds/environments
        if width > 1024 or height > 1024:
            return "environment"
            
        # Small square images might be icons or tiles
        if width == height and width <= 64:
            return "ui"
            
        # Animation frames are often numbered
        if any(char.isdigit() for char in path_lower.split('/')[-1]):
            return "animation"
            
        return "unknown"
        
    def _categorize_audio(self, path: str) -> str:
        """Categorize audio based on path"""
        path_lower = path.lower()
        
        if any(keyword in path_lower for keyword in ['music', 'bgm', 'background']):
            return "music"
        elif any(keyword in path_lower for keyword in ['sfx', 'sound', 'effect']):
            return "effect"
        elif any(keyword in path_lower for keyword in ['voice', 'dialog', 'speech']):
            return "voice"
            
        return "unknown"
        
    def _categorize_model(self, path: str) -> str:
        """Categorize 3D model based on path"""
        path_lower = path.lower()
        
        if any(keyword in path_lower for keyword in ['character', 'player', 'enemy']):
            return "character"
        elif any(keyword in path_lower for keyword in ['environment', 'terrain', 'building']):
            return "environment"
        elif any(keyword in path_lower for keyword in ['weapon', 'item', 'prop']):
            return "prop"
            
        return "unknown"
        
    def find_character_assets(self, assets: List[GameAsset]) -> List[GameAsset]:
        """Filter assets to find character-related content"""
        return [asset for asset in assets if asset.category == "character"]
        
    def generate_asset_report(self, assets: List[GameAsset]) -> Dict:
        """Generate summary report of assets"""
        report = {
            "total_assets": len(assets),
            "by_type": {},
            "by_category": {},
            "character_assets": 0,
            "largest_assets": []
        }
        
        for asset in assets:
            # Count by type
            report["by_type"][asset.type] = report["by_type"].get(asset.type, 0) + 1
            
            # Count by category
            report["by_category"][asset.category] = report["by_category"].get(asset.category, 0) + 1
            
            # Count character assets
            if asset.category == "character":
                report["character_assets"] += 1
                
        # Find largest assets
        sorted_assets = sorted(assets, key=lambda x: x.size_bytes, reverse=True)
        report["largest_assets"] = [
            {"path": asset.path, "size_mb": asset.size_bytes / 1024 / 1024}
            for asset in sorted_assets[:10]
        ]
        
        return report