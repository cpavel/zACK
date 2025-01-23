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
        this.speeds = Array.from({ length: this.columns }, () => Math.random() * 0.1 + 0.05); // Random speeds
        
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

    getRandomSentence() {
        // Select a random sentence from the messages array
        return this.messages[Math.floor(Math.random() * this.messages.length)];
    }

    draw() {
        // Create semi-transparent black rectangle to create trailing effect
        this.ctx.fillStyle = '#0001';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Set text properties
        this.ctx.fillStyle = '#0F0';
        this.ctx.font = '15pt monospace';

        // Draw characters vertically
        for (let i = 0; i < this.drops.length; i++) {
            const x = i * this.fontSize;
            const y = this.drops[i] * this.fontSize;

            // Generate a random character
            const char = String.fromCharCode(Math.random() * 128);
            this.ctx.fillText(char, x, y);

            // Randomly reset the end of the column if it's at least 100px high
            if (y > 100 + Math.random() * 10000) {
                this.drops[i] = 0;
            } else {
                // Move the y coordinate for the column down
                this.drops[i] += this.speeds[i] * 0.5;
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
