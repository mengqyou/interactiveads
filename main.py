#!/usr/bin/env python3
"""
SuperTuxKart Mobile Web - Simple HTTP Server for Android WebView
Simplified web-based version using only Python standard library
"""

import http.server
import socketserver
import json
import random
import urllib.parse
import os

# Simple game state
game_state = {
    "turn": 1,
    "max_turns": 10,
    "player_units": [
        {"id": 1, "type": "tank", "x": 0, "y": 0, "hp": 3, "selected": False},
        {"id": 2, "type": "soldier", "x": 1, "y": 0, "hp": 2, "selected": False},
        {"id": 3, "type": "soldier", "x": 2, "y": 0, "hp": 2, "selected": False}
    ],
    "enemy_units": [
        {"id": 4, "type": "tank", "x": 3, "y": 5, "hp": 3, "selected": False},
        {"id": 5, "type": "soldier", "x": 4, "y": 5, "hp": 2, "selected": False},
        {"id": 6, "type": "soldier", "x": 5, "y": 5, "hp": 2, "selected": False}
    ],
    "selected_unit": None,
    "game_over": False,
    "winner": None
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>SuperTuxKart Mobile</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            margin: 0; 
            padding: 10px; 
            font-family: Arial, sans-serif; 
            background: #2c3e50;
            color: white;
        }
        .game-container { 
            max-width: 400px; 
            margin: 0 auto; 
        }
        .game-board { 
            display: grid; 
            grid-template-columns: repeat(6, 1fr); 
            gap: 2px; 
            background: #34495e;
            padding: 10px;
            border-radius: 8px;
        }
        .cell { 
            aspect-ratio: 1;
            background: #95a5a6;
            border: 1px solid #7f8c8d;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            cursor: pointer;
            border-radius: 4px;
        }
        .cell.player { background: #3498db; }
        .cell.enemy { background: #e74c3c; }
        .cell.selected { box-shadow: 0 0 10px #f1c40f; }
        .cell.movable { background: #2ecc71; }
        .cell.attackable { background: #e67e22; }
        .info { 
            text-align: center; 
            margin: 10px 0; 
            padding: 10px;
            background: #34495e;
            border-radius: 8px;
        }
        .controls { 
            text-align: center; 
            margin: 10px 0; 
        }
        button { 
            background: #e74c3c; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            font-size: 16px; 
            cursor: pointer; 
            border-radius: 5px;
            margin: 5px;
        }
        button:hover { background: #c0392b; }
        .unit-info {
            font-size: 12px;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="info">
            <h2>🏎️ SuperTuxKart Mobile</h2>
            <div>Turn: {turn}/{max_turns}</div>
            <div class="unit-info">
                Player Units: {player_count} | Enemy Units: {enemy_count}
            </div>
        </div>
        
        <div class="game-board" id="gameBoard">
            {board_html}
        </div>
        
        <div class="controls">
            {controls_html}
        </div>
        
        <div class="info">
            <div style="font-size: 14px;">
                💡 Tap your blue units to select, then tap green areas to move or red areas to attack!
            </div>
        </div>
    </div>

    <script>
        function cellClick(x, y) {{
            fetch('/action?action=cell_click&x=' + x + '&y=' + y)
                .then(() => location.reload());
        }}
        
        function endTurn() {{
            fetch('/action?action=end_turn')
                .then(() => location.reload());
        }}
        
        function resetGame() {{
            fetch('/action?action=reset')
                .then(() => location.reload());
        }}
    </script>
</body>
</html>"""

def get_unit_at(x, y):
    """Get unit at specific coordinates"""
    for unit in game_state["player_units"] + game_state["enemy_units"]:
        if unit["x"] == x and unit["y"] == y and unit["hp"] > 0:
            return unit
    return None

def get_cell_class(x, y, unit):
    """Get CSS class for cell"""
    classes = []
    if unit:
        if unit in game_state["player_units"]:
            classes.append("player")
        else:
            classes.append("enemy")
        if unit.get("selected"):
            classes.append("selected")
    
    # Show possible moves/attacks for selected unit
    selected = game_state.get("selected_unit")
    if selected and not unit:
        distance = abs(x - selected["x"]) + abs(y - selected["y"])
        if distance == 1:  # Adjacent cell
            classes.append("movable")
    elif selected and unit and unit not in game_state["player_units"]:
        distance = abs(x - selected["x"]) + abs(y - selected["y"])
        if distance == 1:  # Adjacent enemy
            classes.append("attackable")
    
    return " ".join(classes)

def get_unit_symbol(unit):
    """Get emoji symbol for unit"""
    if unit["type"] == "tank":
        return "🚗" if unit in game_state["player_units"] else "🔴"
    else:
        return "👤" if unit in game_state["player_units"] else "💀"

def generate_board_html():
    """Generate the game board HTML"""
    html = ""
    for row in range(6):
        for col in range(6):
            unit = get_unit_at(col, row)
            cell_class = get_cell_class(col, row, unit)
            symbol = get_unit_symbol(unit) if unit else ""
            html += f'<div class="cell {cell_class}" onclick="cellClick({col}, {row})">{symbol}</div>'
    return html

def generate_controls_html():
    """Generate the controls HTML"""
    if game_state["game_over"]:
        return f'''
            <div style="font-size: 20px; margin: 10px;">
                🎉 {game_state["winner"]} Wins! 🎉
            </div>
            <button onclick="resetGame()">New Game</button>
        '''
    else:
        return '''
            <button onclick="endTurn()">End Turn</button>
            <button onclick="resetGame()">Reset Game</button>
        '''

def handle_action(action, x=None, y=None):
    """Handle game actions"""
    if action == 'cell_click' and x is not None and y is not None:
        unit = get_unit_at(x, y)
        
        # Select player unit
        if unit and unit in game_state["player_units"] and unit["hp"] > 0:
            # Deselect all units
            for u in game_state["player_units"] + game_state["enemy_units"]:
                u["selected"] = False
            # Select this unit
            unit["selected"] = True
            game_state["selected_unit"] = unit
        
        # Move or attack with selected unit
        elif game_state.get("selected_unit"):
            selected = game_state["selected_unit"]
            distance = abs(x - selected["x"]) + abs(y - selected["y"])
            
            if distance == 1:  # Adjacent cell
                if unit and unit not in game_state["player_units"]:
                    # Attack enemy
                    unit["hp"] -= 1
                    if unit["hp"] <= 0:
                        unit["x"] = -1  # Remove from board
                        unit["y"] = -1
                elif not unit:
                    # Move to empty cell
                    selected["x"] = x
                    selected["y"] = y
                
                # Deselect after action
                selected["selected"] = False
                game_state["selected_unit"] = None
    
    elif action == 'end_turn':
        # Simple AI: move random enemy toward player
        enemies = [u for u in game_state["enemy_units"] if u["hp"] > 0]
        if enemies:
            enemy = random.choice(enemies)
            # Move toward center
            if enemy["x"] > 2:
                enemy["x"] -= 1
            elif enemy["x"] < 2:
                enemy["x"] += 1
            if enemy["y"] > 2:
                enemy["y"] -= 1
        
        game_state["turn"] += 1
        
        # Check win conditions
        player_alive = any(u["hp"] > 0 for u in game_state["player_units"])
        enemy_alive = any(u["hp"] > 0 for u in game_state["enemy_units"])
        
        if not player_alive:
            game_state["game_over"] = True
            game_state["winner"] = "Enemy"
        elif not enemy_alive:
            game_state["game_over"] = True
            game_state["winner"] = "Player"
        elif game_state["turn"] > game_state["max_turns"]:
            game_state["game_over"] = True
            player_count = len([u for u in game_state["player_units"] if u["hp"] > 0])
            enemy_count = len([u for u in game_state["enemy_units"] if u["hp"] > 0])
            game_state["winner"] = "Player" if player_count > enemy_count else "Enemy"
    
    elif action == 'reset':
        # Reset game state
        game_state.update({
            "turn": 1,
            "selected_unit": None,
            "game_over": False,
            "winner": None
        })
        # Reset units
        game_state["player_units"] = [
            {"id": 1, "type": "tank", "x": 0, "y": 0, "hp": 3, "selected": False},
            {"id": 2, "type": "soldier", "x": 1, "y": 0, "hp": 2, "selected": False},
            {"id": 3, "type": "soldier", "x": 2, "y": 0, "hp": 2, "selected": False}
        ]
        game_state["enemy_units"] = [
            {"id": 4, "type": "tank", "x": 3, "y": 5, "hp": 3, "selected": False},
            {"id": 5, "type": "soldier", "x": 4, "y": 5, "hp": 2, "selected": False},
            {"id": 6, "type": "soldier", "x": 5, "y": 5, "hp": 2, "selected": False}
        ]

class GameHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Serve main game page
            player_count = len([u for u in game_state["player_units"] if u["hp"] > 0])
            enemy_count = len([u for u in game_state["enemy_units"] if u["hp"] > 0])
            
            html = HTML_TEMPLATE.format(
                turn=game_state["turn"],
                max_turns=game_state["max_turns"],
                player_count=player_count,
                enemy_count=enemy_count,
                board_html=generate_board_html(),
                controls_html=generate_controls_html()
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        elif self.path.startswith('/action'):
            # Handle game actions
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            
            action = params.get('action', [None])[0]
            x = int(params.get('x', [0])[0]) if params.get('x') else None
            y = int(params.get('y', [0])[0]) if params.get('y') else None
            
            handle_action(action, x, y)
            
            # Return simple response
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            # Default 404
            self.send_response(404)
            self.end_headers()

def main():
    PORT = 5000
    with socketserver.TCPServer(("0.0.0.0", PORT), GameHandler) as httpd:
        print(f"SuperTuxKart Mobile server running on port {PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    main()