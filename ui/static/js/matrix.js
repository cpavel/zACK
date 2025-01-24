class MatrixEffect {
    constructor() {
        this.canvas = document.getElementById('matrix');
        this.ctx = this.canvas.getContext('2d');
        
        // Messages to be integrated into the effect
        this.messages = [
            "zACK - Your AI Agent for Lead Engagement",
            "Machine Learning expensive production scale",
            "AI infrastructure costs",
            "GPU acceleration",
            "AI optimization",
            "Social Media outreach",
            "AI agents writing for you",
            "Pavel says hi",
            "Panda and his friend racoon were here",
            "Trash Panda ftw"
        ];

        this.initialize();
    }

    initialize() {
        this.resize();
        window.addEventListener('resize', () => this.resize());

        // Adjusted font size for better readability
        this.fontSize = 18;
        this.columns = Math.floor(this.canvas.width / this.fontSize);
        this.drops = Array(this.columns).fill(0);
        this.activeColumns = new Set();
        
        // Even slower speeds for message readability
        this.speeds = Array.from({ length: this.columns }, () => Math.random() * 0.05 + 0.02);
        this.messageStates = Array(this.columns).fill(null);
        
        // Background characters
        this.chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$@#*%'.split('');
        
        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    getRandomMessage() {
        return this.messages[Math.floor(Math.random() * this.messages.length)];
    }

    draw() {
        // Subtle fade effect for trail
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Set base text properties
        this.ctx.font = `${this.fontSize}px monospace`;

        // Start new message streams occasionally
        if (Math.random() < 0.005) {
            const col = Math.floor(Math.random() * this.columns);
            if (!this.activeColumns.has(col)) {
                this.activeColumns.add(col);
                this.messageStates[col] = {
                    message: this.getRandomMessage(),
                    position: 0
                };
            }
        }

        // Draw and update each column
        for (let i = 0; i < this.columns; i++) {
            const x = i * this.fontSize;
            const y = this.drops[i] * this.fontSize;

            // Draw message characters if column is active
            if (this.activeColumns.has(i) && this.messageStates[i]) {
                const messageState = this.messageStates[i];
                const chars = messageState.message.split('');
                
                // Draw the message vertically with improved visibility
                for (let j = 0; j < chars.length; j++) {
                    const charY = y + (j * this.fontSize * 1.2); // Slightly reduced spacing
                    if (charY > 0 && charY < this.canvas.height) {
                        // Create a glowing effect for the message
                        const alpha = Math.max(0, 1 - (j * 0.03)); // Slower fade for longer readability
                        
                        // Draw glow effect
                        this.ctx.shadowColor = 'rgba(0, 255, 0, 0.5)';
                        this.ctx.shadowBlur = 5;
                        
                        if (j === 0) {
                            // Leading character: bright but not too harsh
                            this.ctx.fillStyle = 'rgba(180, 255, 180, 0.95)';
                        } else {
                            // Following characters: gentle green gradient
                            this.ctx.fillStyle = `rgba(0, 255, 0, ${alpha * 0.8})`;
                        }
                        
                        this.ctx.fillText(chars[j], x, charY);
                        
                        // Reset shadow for next character
                        this.ctx.shadowBlur = 0;
                    }
                }
            } else {
                // Background matrix rain
                if (Math.random() < 0.02) {
                    const randomChar = this.chars[Math.floor(Math.random() * this.chars.length)];
                    this.ctx.fillStyle = 'rgba(0, 255, 0, 0.15)';
                    this.ctx.fillText(randomChar, x, y);
                }
            }

            // Update positions
            this.drops[i] += this.speeds[i] * 0.3;

            // Reset column when it goes off screen
            if (this.drops[i] * this.fontSize > this.canvas.height + 100) {
                this.drops[i] = 0;
                this.activeColumns.delete(i);
                this.messageStates[i] = null;
            }
        }
    }

    animate() {
        this.draw();
        requestAnimationFrame(() => this.animate());
    }
}

// Initialize when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MatrixEffect();
});
