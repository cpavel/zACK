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
        // Set canvas size
        this.resize();
        window.addEventListener('resize', () => this.resize());

        // Initialize columns
        this.fontSize = 14;
        this.columns = Math.floor(this.canvas.width / this.fontSize);
        this.drops = Array(this.columns).fill(0);
        this.activeColumns = new Set(); // Track which columns are showing messages
        
        // Initialize speeds and message states
        this.speeds = Array.from({ length: this.columns }, () => Math.random() * 0.3 + 0.1);
        this.messageStates = Array(this.columns).fill(null);
        
        // Create character sets
        this.chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$@#*%'.split('');
        
        // Start the animation
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
        // Create semi-transparent black rectangle for fade effect
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Set text properties
        this.ctx.font = this.fontSize + 'px monospace';

        // Randomly start new message streams
        if (Math.random() < 0.02) { // Adjust probability for message frequency
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
                
                // Draw each character of the message with different intensities
                for (let j = 0; j < chars.length; j++) {
                    const charY = y + (j * this.fontSize);
                    if (charY > 0 && charY < this.canvas.height) {
                        // Create glowing effect for leading characters
                        const alpha = Math.max(0, 1 - (j * 0.1));
                        this.ctx.fillStyle = `rgba(0, 255, 0, ${alpha})`;
                        if (j === 0) {
                            // Make first character brighter
                            this.ctx.fillStyle = '#fff';
                        }
                        this.ctx.fillText(chars[j], x, charY);
                    }
                }
            } else {
                // Draw random characters for non-message columns
                if (Math.random() < 0.05) { // Reduced probability for sparser effect
                    const randomChar = this.chars[Math.floor(Math.random() * this.chars.length)];
                    this.ctx.fillStyle = 'rgba(0, 255, 0, 0.3)';
                    this.ctx.fillText(randomChar, x, y);
                }
            }

            // Update positions
            this.drops[i] += this.speeds[i];

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
