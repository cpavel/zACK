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

    getRandomSentence() {
        // Select a random sentence from the messages array
        return this.messages[Math.floor(Math.random() * this.messages.length)];
    }

    draw() {
        // Create semi-transparent black rectangle with more opacity to slow down the fade
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Set text properties
        this.ctx.fillStyle = '#0F0';
        this.ctx.font = `${this.fontSize}px monospace`;

        // Draw characters vertically
        for (let i = 0; i < this.drops.length; i++) {
            const sentence = this.getRandomSentence();
            const x = i * this.fontSize;
            let y = this.drops[i] * this.fontSize;

            // Draw each character of the sentence vertically
            for (let j = 0; j < sentence.length; j++) {
                const char = sentence[j];
                this.ctx.fillText(char, x, y + j * this.fontSize);
            }

            // Move the column down
            this.drops[i] += 0.05;

            // Reset column if it goes off screen
            if (this.drops[i] * this.fontSize > this.canvas.height) {
                this.drops[i] = 0;
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
