// Flappy Bird Game for Summit
(function() {
    const canvas = document.getElementById('flappy-canvas');
    const ctx = canvas.getContext('2d');
    const overlay = document.getElementById('game-overlay');
    const overlayTitle = document.getElementById('overlay-title');
    const overlayScore = document.getElementById('overlay-score');
    const startBtn = document.getElementById('start-btn');
    const currentScoreEl = document.getElementById('current-score');
    const highScoreEl = document.getElementById('high-score');

    // Game constants
    const GRAVITY = 0.5;
    const JUMP_FORCE = -9;
    const PIPE_WIDTH = 60;
    const PIPE_GAP = 150;
    const PIPE_SPEED = 3;
    const PIPE_SPAWN_RATE = 90;

    // Colors matching the theme
    const ACCENT_COLOR = '#00d4ff';
    const BG_DARK = '#0a0a0f';
    const BG_CARD = '#12121a';

    // Game state
    let bird, pipes, score, highScore, gameLoop, frameCount, isPlaying;

    // Load high score from localStorage
    highScore = parseInt(localStorage.getItem('flappyHighScore')) || 0;
    highScoreEl.textContent = highScore;

    function initGame() {
        bird = {
            x: 80,
            y: canvas.height / 2,
            width: 30,
            height: 24,
            velocity: 0
        };
        pipes = [];
        score = 0;
        frameCount = 0;
        currentScoreEl.textContent = '0';
    }

    function startGame() {
        initGame();
        isPlaying = true;
        overlay.classList.add('hidden');
        gameLoop = requestAnimationFrame(update);
    }

    function endGame() {
        isPlaying = false;
        cancelAnimationFrame(gameLoop);

        if (score > highScore) {
            highScore = score;
            localStorage.setItem('flappyHighScore', highScore);
            highScoreEl.textContent = highScore;
            overlayTitle.textContent = 'New High Score!';
        } else {
            overlayTitle.textContent = 'Game Over';
        }

        overlayScore.textContent = `Score: ${score}`;
        startBtn.textContent = 'Play Again';
        overlay.classList.remove('hidden');
    }

    function jump() {
        if (isPlaying) {
            bird.velocity = JUMP_FORCE;
        }
    }

    function spawnPipe() {
        const minHeight = 50;
        const maxHeight = canvas.height - PIPE_GAP - minHeight;
        const topHeight = Math.random() * (maxHeight - minHeight) + minHeight;

        pipes.push({
            x: canvas.width,
            topHeight: topHeight,
            bottomY: topHeight + PIPE_GAP,
            passed: false
        });
    }

    function update() {
        frameCount++;

        // Clear canvas
        ctx.fillStyle = BG_DARK;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw background gradient lines
        ctx.strokeStyle = '#1a1a2e';
        ctx.lineWidth = 1;
        for (let i = 0; i < canvas.height; i += 30) {
            ctx.beginPath();
            ctx.moveTo(0, i);
            ctx.lineTo(canvas.width, i);
            ctx.stroke();
        }

        // Update bird
        bird.velocity += GRAVITY;
        bird.y += bird.velocity;

        // Draw bird (triangle/arrow shape pointing right)
        ctx.save();
        ctx.translate(bird.x + bird.width / 2, bird.y + bird.height / 2);
        ctx.rotate(Math.min(Math.max(bird.velocity * 0.05, -0.5), 0.5));

        // Bird body
        ctx.fillStyle = ACCENT_COLOR;
        ctx.shadowColor = ACCENT_COLOR;
        ctx.shadowBlur = 15;
        ctx.beginPath();
        ctx.moveTo(bird.width / 2, 0);
        ctx.lineTo(-bird.width / 2, -bird.height / 2);
        ctx.lineTo(-bird.width / 3, 0);
        ctx.lineTo(-bird.width / 2, bird.height / 2);
        ctx.closePath();
        ctx.fill();
        ctx.restore();

        // Spawn pipes
        if (frameCount % PIPE_SPAWN_RATE === 0) {
            spawnPipe();
        }

        // Update and draw pipes
        for (let i = pipes.length - 1; i >= 0; i--) {
            const pipe = pipes[i];
            pipe.x -= PIPE_SPEED;

            // Draw pipes
            ctx.fillStyle = BG_CARD;
            ctx.strokeStyle = ACCENT_COLOR;
            ctx.lineWidth = 2;

            // Top pipe
            ctx.fillRect(pipe.x, 0, PIPE_WIDTH, pipe.topHeight);
            ctx.strokeRect(pipe.x, 0, PIPE_WIDTH, pipe.topHeight);

            // Bottom pipe
            const bottomHeight = canvas.height - pipe.bottomY;
            ctx.fillRect(pipe.x, pipe.bottomY, PIPE_WIDTH, bottomHeight);
            ctx.strokeRect(pipe.x, pipe.bottomY, PIPE_WIDTH, bottomHeight);

            // Pipe caps with glow
            ctx.shadowColor = ACCENT_COLOR;
            ctx.shadowBlur = 10;
            ctx.fillStyle = ACCENT_COLOR;
            ctx.fillRect(pipe.x - 5, pipe.topHeight - 20, PIPE_WIDTH + 10, 20);
            ctx.fillRect(pipe.x - 5, pipe.bottomY, PIPE_WIDTH + 10, 20);
            ctx.shadowBlur = 0;

            // Check for score
            if (!pipe.passed && pipe.x + PIPE_WIDTH < bird.x) {
                pipe.passed = true;
                score++;
                currentScoreEl.textContent = score;
            }

            // Remove off-screen pipes
            if (pipe.x + PIPE_WIDTH < 0) {
                pipes.splice(i, 1);
            }

            // Collision detection
            if (bird.x + bird.width > pipe.x && bird.x < pipe.x + PIPE_WIDTH) {
                if (bird.y < pipe.topHeight || bird.y + bird.height > pipe.bottomY) {
                    endGame();
                    return;
                }
            }
        }

        // Check boundaries
        if (bird.y + bird.height > canvas.height || bird.y < 0) {
            endGame();
            return;
        }

        // Draw score on canvas
        ctx.fillStyle = ACCENT_COLOR;
        ctx.font = 'bold 24px "Segoe UI", sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(score, canvas.width / 2, 50);

        gameLoop = requestAnimationFrame(update);
    }

    // Event listeners
    startBtn.addEventListener('click', startGame);

    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space') {
            e.preventDefault();
            if (!isPlaying) {
                startGame();
            } else {
                jump();
            }
        }
    });

    canvas.addEventListener('click', () => {
        if (isPlaying) {
            jump();
        }
    });

    // Touch support for mobile
    canvas.addEventListener('touchstart', (e) => {
        e.preventDefault();
        if (isPlaying) {
            jump();
        }
    });

    // Initialize
    initGame();
})();
