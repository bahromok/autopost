"""Content library with educational tech content."""

import random
from typing import Dict, List
from loguru import logger


class ContentLibrary:
    """Library of curated educational tech content."""
    
    # Tech Facts - Focus on AI, Programming, CS
    TECH_FACTS = [
        {
            "title": "🤖 AI Model Training",
            "content": "GPT-4 was trained on ~13 trillion tokens and cost over $100 million to train. The model has 1.76 trillion parameters - that's more than the number of stars in the Milky Way galaxy!",
            "hashtags": "#AI #MachineLearning #GPT4"
        },
        {
            "title": "💻 Programming Languages",
            "content": "Python is now the #1 most popular programming language, surpassing JavaScript. It's used in 48% of all data science projects and powers AI frameworks like TensorFlow and PyTorch.",
            "hashtags": "#Python #Programming #DataScience"
        },
        {
            "title": "🧠 Neural Networks",
            "content": "The human brain has ~86 billion neurons. GPT-3 has 175 billion parameters. But here's the twist: your brain uses only 20 watts of power, while training GPT-3 consumed enough electricity to power 120 homes for a year!",
            "hashtags": "#AI #NeuralNetworks #DeepLearning"
        },
        {
            "title": "⚡ Code Execution Speed",
            "content": "C++ is ~100x faster than Python for the same task. But Python's development speed is 5-10x faster. That's why we use Python for AI research and C++ for production systems!",
            "hashtags": "#Programming #Performance #CPlusPlus"
        },
        {
            "title": "🔐 Encryption Power",
            "content": "Breaking a 256-bit encryption would take a supercomputer longer than the age of the universe (13.8 billion years). Even with quantum computers, it would still take millions of years!",
            "hashtags": "#Cybersecurity #Encryption #Quantum"
        },
        {
            "title": "🎮 Game Development",
            "content": "Unreal Engine 5 can render 10 billion triangles per frame in real-time. That's more detail than the human eye can perceive! Modern games are basically interactive movies.",
            "hashtags": "#GameDev #UnrealEngine #Graphics"
        },
        {
            "title": "🌐 Internet Scale",
            "content": "Google processes over 8.5 billion searches per day. That's ~99,000 searches per second! Their index contains over 100 petabytes of data - enough to fill 100 million laptops.",
            "hashtags": "#Google #Internet #BigData"
        },
        {
            "title": "🚀 Open Source Impact",
            "content": "96% of all applications use open source code. Linux powers 96.3% of the world's top 1 million servers. Open source isn't just free - it's the foundation of modern technology!",
            "hashtags": "#OpenSource #Linux #GitHub"
        },
    ]
    
    # Quick Tutorials - Programming, AI, CS, Tools
    TUTORIALS = [
        {
            "title": "📚 Python for AI/ML",
            "content": """Essential Python libraries for AI:

1️⃣ NumPy - Fast numerical computing
2️⃣ Pandas - Data manipulation
3️⃣ TensorFlow/PyTorch - Deep learning
4️⃣ Scikit-learn - Machine learning
5️⃣ Matplotlib - Data visualization

Install: pip install numpy pandas tensorflow

Start your AI journey! 🤖""",
            "hashtags": "#Tutorial #Python #AI #MachineLearning"
        },
        {
            "title": "📚 Git Basics",
            "content": """Essential Git commands:

1️⃣ git init - Start repository
2️⃣ git add . - Stage changes
3️⃣ git commit -m "msg" - Save changes
4️⃣ git push - Upload to remote
5️⃣ git pull - Download updates
6️⃣ git branch - Create branches
7️⃣ git merge - Merge branches

Master version control! 🚀""",
            "hashtags": "#Tutorial #Git #Programming"
        },
        {
            "title": "📚 JavaScript Async/Await",
            "content": """Modern async JavaScript:

// Old way (callbacks)
fetch(url).then(res => res.json())

// New way (async/await)
const data = await fetch(url).then(r => r.json())

✅ Cleaner code
✅ Better error handling
✅ Easier to read

Async made simple! ⚡""",
            "hashtags": "#Tutorial #JavaScript #WebDev"
        },
        {
            "title": "📚 Big O Notation",
            "content": """Algorithm complexity explained:

O(1) - Constant: Array access
O(log n) - Logarithmic: Binary search
O(n) - Linear: Simple loop
O(n log n) - Efficient sort
O(n²) - Quadratic: Nested loops
O(2ⁿ) - Exponential: Avoid!

Optimize your code! 🎯""",
            "hashtags": "#Tutorial #Algorithms #CS"
        },
        {
            "title": "📚 Docker Basics",
            "content": """Essential Docker commands:

1️⃣ docker build -t name . - Build image
2️⃣ docker run -p 8080:80 name - Run container
3️⃣ docker ps - List containers
4️⃣ docker stop id - Stop container
5️⃣ docker rm id - Remove container

Containerize everything! 🐳""",
            "hashtags": "#Tutorial #Docker #DevOps"
        },
        {
            "title": "📚 VS Code Extensions",
            "content": """Must-have VS Code extensions:

1️⃣ Prettier - Code formatter
2️⃣ GitLens - Git superpowers
3️⃣ Live Server - Local web server
4️⃣ Python - Python support
5️⃣ ESLint - JavaScript linter

Supercharge your editor! ⚡""",
            "hashtags": "#Tutorial #VSCode #Tools"
        },
        {
            "title": "📚 SQL Basics",
            "content": """Essential SQL queries:

SELECT * FROM users WHERE age > 18
INSERT INTO users VALUES ('John', 25)
UPDATE users SET age = 26 WHERE name = 'John'
DELETE FROM users WHERE id = 1
JOIN tables ON users.id = orders.user_id

Data at your fingertips! 📊""",
            "hashtags": "#Tutorial #SQL #Database"
        },
        {
            "title": "📚 Regex Patterns",
            "content": """Useful regex patterns:

📧 Email: ^[\\w.-]+@[\\w.-]+\\.\\w+$
🔗 URL: https?://[\\w.-]+\\.\\w+
📱 Phone: ^\\+?\\d{10,15}$
💳 Credit Card: ^\\d{4}[- ]?\\d{4}[- ]?\\d{4}[- ]?\\d{4}$

Pattern matching mastered! 🎯""",
            "hashtags": "#Tutorial #Regex #Programming"
        },
        {
            "title": "📚 Free AI Tools",
            "content": """100% Free AI tools you should use:

🤖 ChatGPT (free tier) - AI assistant
🎨 Stable Diffusion - Image generation
💻 GitHub Copilot (students) - Code completion
📝 Grammarly - Writing assistant
🎵 Suno AI - Music generation

No limits, no costs! 🆓""",
            "hashtags": "#Tutorial #AI #FreeTools"
        },
        {
            "title": "📚 Linux Commands",
            "content": """Essential Linux commands:

1️⃣ ls -la - List files (detailed)
2️⃣ cd ~/path - Change directory
3️⃣ grep "text" file - Search in files
4️⃣ chmod +x file - Make executable
5️⃣ top - Monitor processes

Command line power! 💪""",
            "hashtags": "#Tutorial #Linux #Terminal"
        },
    ]
    
    # Pro Tips - Useful Tools & Lifehacks
    PRO_TIPS = [
        {
            "title": "🎯 Free Developer Tools",
            "content": """Amazing free tools for developers:

🔧 VS Code - Best code editor
🎨 Figma - UI/UX design
📊 Postman - API testing
🗄️ MongoDB Atlas - Free database
🚀 Vercel/Netlify - Free hosting

Build without spending! 💰""",
            "hashtags": "#ProTip #Tools #Free"
        },
        {
            "title": "🎯 AI Productivity Hacks",
            "content": """Use AI to 10x your productivity:

💡 ChatGPT - Code debugging
📝 Claude - Document writing
🎨 Midjourney - Design mockups
🔍 Perplexity - Research
📧 Gmail AI - Email drafts

Work smarter with AI! 🤖""",
            "hashtags": "#ProTip #AI #Productivity"
        },
        {
            "title": "🎯 GitHub Secrets",
            "content": """Hidden GitHub features:

1️⃣ Press '.' on any repo - VS Code in browser
2️⃣ Press 't' - File finder
3️⃣ Press 'l' - Jump to line
4️⃣ Add '.dev' to URL - GitHub Codespaces
5️⃣ Use GitHub CLI - gh repo clone

GitHub power user! 🚀""",
            "hashtags": "#ProTip #GitHub #Tools"
        },
        {
            "title": "🎯 Chrome Extensions",
            "content": """Must-have Chrome extensions:

🔐 Bitwarden - Password manager
📚 Pocket - Save articles
🎨 ColorZilla - Color picker
📊 Wappalyzer - Tech stack detector
⚡ uBlock Origin - Ad blocker

Browse like a pro! 🌐""",
            "hashtags": "#ProTip #Chrome #Extensions"
        },
        {
            "title": "🎯 Keyboard Shortcuts",
            "content": """Universal productivity shortcuts:

⌨️ Ctrl+Z - Undo
⌨️ Ctrl+Shift+Z - Redo
⌨️ Ctrl+F - Find
⌨️ Ctrl+Shift+T - Reopen tab
⌨️ Win+V - Clipboard history
⌨️ Win+Shift+S - Screenshot

Save hours daily! ⏱️""",
            "hashtags": "#ProTip #Productivity #Shortcuts"
        },
        {
            "title": "🎯 Free Learning Resources",
            "content": """Best free learning platforms:

📚 freeCodeCamp - Web development
🎓 CS50 - Computer science
🤖 Fast.ai - Deep learning
💻 The Odin Project - Full stack
📖 MDN - Web documentation

Learn anything, free! 🆓""",
            "hashtags": "#ProTip #Learning #Free"
        },
        {
            "title": "🎯 Code Optimization",
            "content": """Quick optimization tips:

1️⃣ Use const/let instead of var
2️⃣ Avoid nested loops
3️⃣ Cache DOM queries
4️⃣ Use async/await
5️⃣ Minimize HTTP requests

Faster code = happier users! ⚡""",
            "hashtags": "#ProTip #Programming #Performance"
        },
        {
            "title": "🎯 Terminal Aliases",
            "content": """Save time with aliases:

alias gs='git status'
alias gc='git commit -m'
alias gp='git push'
alias ll='ls -la'
alias ..='cd ..'

Add to ~/.bashrc or ~/.zshrc

Type less, do more! 🚀""",
            "hashtags": "#ProTip #Terminal #Productivity"
        },
    ]
    
    
    def __init__(self):
        """Initialize content library."""
        from src.core.dynamic_content_fetcher import DynamicContentFetcher
        self.dynamic_fetcher = DynamicContentFetcher()
        self.used_facts = set()
        self.used_tutorials = set()
        self.used_tips = set()
    
    def get_random_fact(self) -> Dict[str, str]:
        """Get a random tech fact (avoid recently used)."""
        available = [f for i, f in enumerate(self.TECH_FACTS) if i not in self.used_facts]
        
        if not available:
            # Reset if all used
            self.used_facts.clear()
            available = self.TECH_FACTS
        
        fact = random.choice(available)
        self.used_facts.add(self.TECH_FACTS.index(fact))
        
        logger.info(f"Selected tech fact: {fact['title']}")
        return fact
    
    def get_random_tutorial(self) -> Dict[str, str]:
        """Get a random tutorial (avoid recently used)."""
        available = [t for i, t in enumerate(self.TUTORIALS) if i not in self.used_tutorials]
        
        if not available:
            self.used_tutorials.clear()
            available = self.TUTORIALS
        
        tutorial = random.choice(available)
        self.used_tutorials.add(self.TUTORIALS.index(tutorial))
        
        logger.info(f"Selected tutorial: {tutorial['title']}")
        return tutorial
    
    def get_random_tip(self) -> Dict[str, str]:
        """Get a random pro tip (avoid recently used)."""
        available = [t for i, t in enumerate(self.PRO_TIPS) if i not in self.used_tips]
        
        if not available:
            self.used_tips.clear()
            available = self.PRO_TIPS
        
        tip = random.choice(available)
        self.used_tips.add(self.PRO_TIPS.index(tip))
        
        logger.info(f"Selected pro tip: {tip['title']}")
        return tip
    
    async def get_random_educational_content(self) -> Dict[str, str]:
        """
        Get random educational content.
        Tries to get dynamic content first (80% chance), falls back to static.
        """
        # Try dynamic content 80% of the time if enabled
        if random.random() < 0.8:
            try:
                logger.info("Fetching dynamic educational content...")
                content = await self.dynamic_fetcher.get_random_content()
                if content:
                    logger.success(f"Fetched dynamic content: {content['title']}")
                    return content
            except Exception as e:
                logger.error(f"Failed to fetch dynamic content: {e}")
        
        # Fallback to static content
        logger.info("Using static educational content (fallback)")
        content_type = random.choice(['fact', 'tutorial', 'tip'])
        
        if content_type == 'fact':
            return self.get_random_fact()
        elif content_type == 'tutorial':
            return self.get_random_tutorial()
        else:
            return self.get_random_tip()
    
    def format_educational_post(self, content: Dict[str, str]) -> str:
        """Format educational content for Telegram post."""
        from src.core.content_formatter import ContentFormatter
        
        main_content_raw = content.get('summary') or content.get('content', '')
        # Use helper to handle dict/str
        main_content = ContentFormatter._format_summary(main_content_raw)
        
        parts = [
            f"<b>{content['title']}</b>",
            "",
            main_content,
            "",
            content.get('hashtags', ''),
        ]
        
        footer = ContentFormatter.create_social_footer()
        if footer:
            parts.append("")
            parts.append("━━━━━━━━━━━━━━━━━━━━")
            parts.append(footer)
            
        return "\n".join(parts)
