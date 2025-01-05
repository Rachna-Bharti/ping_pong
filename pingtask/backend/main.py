import asyncio
import json
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

clients = []

# Initial Game State
game_state = {
    "players": {
        1: {"y": 50},  # Paddle position for Player 1 (percentage)
        2: {"y": 50},  # Paddle position for Player 2 (percentage)
    },
    "ball": {"x": 50, "y": 50, "vx": 0.5, "vy": 0.5},  # Ball position and velocity
    "obstacles": [
        {"x": 30, "y": 40, "size": 10},  # Random obstacle positions and sizes
        {"x": 60, "y": 30, "size": 10},
    ],
    "score": {1: 0, 2: 0},
    "running": False,  # Indicates if the game is running
    "paused": False,   # Indicates if the game is paused
}

async def update_game_state():
    global game_state
    while True:
        if game_state["running"] and not game_state["paused"]:
            # Update ball position
            ball = game_state["ball"]
            ball["x"] += ball["vx"]
            ball["y"] += ball["vy"]

            # Check for collisions with top and bottom walls
            if ball["y"] <= 0 or ball["y"] >= 100:
                ball["vy"] *= -1

            # Check for scoring
            if ball["x"] <= 0:
                game_state["score"][2] += 1
                reset_ball()
            elif ball["x"] >= 100:
                game_state["score"][1] += 1
                reset_ball()

            # Check for collisions with paddles
            for player_id, player in game_state["players"].items():
                if (
                    (player_id == 1 and ball["x"] <= 5 and abs(ball["y"] - player["y"]) <= 10) or
                    (player_id == 2 and ball["x"] >= 95 and abs(ball["y"] - player["y"]) <= 10)
                ):
                    ball["vx"] *= -1

            # Check for collisions with obstacles
            for obstacle in game_state["obstacles"]:
                if (
                    obstacle["x"] <= ball["x"] <= obstacle["x"] + obstacle["size"] and
                    obstacle["y"] <= ball["y"] <= obstacle["y"] + obstacle["size"]
                ):
                    ball["vx"] *= -1
                    ball["vy"] *= -1

        await asyncio.sleep(0.016)  # ~60 FPS

def reset_ball():
    game_state["ball"] = {"x": 50, "y": 50, "vx": 0.5, "vy": 0.5}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle player controls
            if "player" in message:
                player = game_state["players"][message["player"]]
                if message["action"] == "up" and player["y"] > 5:
                    player["y"] -= 5
                elif message["action"] == "down" and player["y"] < 95:
                    player["y"] += 5

            # Handle pause and restart
            if "action" in message:
                if message["action"] == "pause":
                    game_state["paused"] = not game_state["paused"]
                elif message["action"] == "restart":
                    game_state["running"] = True
                    game_state["paused"] = False
                    reset_ball()
                    game_state["score"] = {1: 0, 2: 0}

            # Broadcast updated state
            for client in clients:
                await client.send_text(json.dumps(game_state))
    except:
        clients.remove(websocket)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_game_state())
