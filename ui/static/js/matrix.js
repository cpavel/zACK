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
        this.fontSize = 15;
        this.columns = Math.floor(this.canvas.width / this.fontSize);
        this.drops = Array(this.columns).fill(1);
        
        // Create character sets including our messages
        this.chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$@#*%'.split('');
        this.messageChars = this.messages.join(' ').split('');
        
        // Start the animation
        this.animate();
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    getRandomChar() {
        // 20% chance to use a character from our messages
        if (Math.random() < 0.2) {
            return this.messageChars[Math.floor(Math.random() * this.messageChars.length)];
        }
        return this.chars[Math.floor(Math.random() * this.chars.length)];
    }

    draw() {
        // Create semi-transparent black rectangle with more opacity to slow down the fade
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Set text properties
        this.ctx.fillStyle = '#0F0';
        this.ctx.font = `${this.fontSize}px monospace`;

        // Draw characters
        for (let i = 0; i < this.drops.length; i++) {
            const text = this.getRandomChar();
            const x = i * this.fontSize;
            const y = this.drops[i] * this.fontSize;

            // Add white highlight for first character in column
            if (this.drops[i] === 1) {
                this.ctx.fillStyle = '#FFF';
                this.ctx.fillText(text, x, y);
                this.ctx.fillStyle = '#0F0';
            } else {
                this.ctx.fillText(text, x, y);
            }

            // Reset column or move it down (reduced probability to reset)
            if (y > this.canvas.height && Math.random() > 0.995) {
                this.drops[i] = 0;
            }
            // Slow down the falling speed by incrementing by 0.25 instead of 1
            this.drops[i] += 0.25;
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
