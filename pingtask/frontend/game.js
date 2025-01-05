const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const pauseButton = document.getElementById("pauseButton");
const restartButton = document.getElementById("restartButton");

const socket = new WebSocket("ws://localhost:8000/ws");
let gameState = null;

// Handle incoming game state updates
socket.onmessage = (event) => {
    gameState = JSON.parse(event.data);
};

// Send player input to the server
document.addEventListener("keydown", (event) => {
    if (event.key === "w") {
        socket.send(JSON.stringify({ player: 1, action: "up" }));
    } else if (event.key === "s") {
        socket.send(JSON.stringify({ player: 1, action: "down" }));
    } else if (event.key === "ArrowUp") {
        socket.send(JSON.stringify({ player: 2, action: "up" }));
    } else if (event.key === "ArrowDown") {
        socket.send(JSON.stringify({ player: 2, action: "down" }));
    }
});

// Handle pause button
pauseButton.addEventListener("click", () => {
    socket.send(JSON.stringify({ action: "pause" }));
});

// Handle restart button
restartButton.addEventListener("click", () => {
    socket.send(JSON.stringify({ action: "restart" }));
});

// Draw game elements
function drawGame() {
    if (!gameState) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw ball
    const ball = gameState.ball;
    ctx.fillStyle = "white";
    ctx.beginPath();
    ctx.arc((ball.x / 100) * canvas.width, (ball.y / 100) * canvas.height, 5, 0, Math.PI * 2);
    ctx.fill();

    // Draw paddles
    Object.values(gameState.players).forEach((player, index) => {
        ctx.fillStyle = "white";
        ctx.fillRect(
            index === 0 ? 10 : canvas.width - 20,
            (player.y / 100) * canvas.height,
            10,
            50
        );
    });

    // Draw obstacles
    gameState.obstacles.forEach((obstacle) => {
        ctx.fillStyle = "red";
        ctx.fillRect(
            (obstacle.x / 100) * canvas.width,
            (obstacle.y / 100) * canvas.height,
            (obstacle.size / 100) * canvas.width,
            (obstacle.size / 100) * canvas.height
        );
    });

    // Draw scores
    ctx.fillStyle = "white";
    ctx.font = "16px Arial";
    ctx.fillText(`Player 1: ${gameState.score[1]}`, 10, 20);
    ctx.fillText(`Player 2: ${gameState.score[2]}`, canvas.width - 120, 20);
}

// Game loop
function gameLoop() {
    drawGame();
    requestAnimationFrame(gameLoop);
}

// Start game loop
gameLoop();
