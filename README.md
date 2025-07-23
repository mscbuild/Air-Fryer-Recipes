# 🍳 Air Fryer Recipes Telegram Bot

A Telegram bot that provides delicious air fryer recipes with search functionality and intuitive navigation. Built with Python and integrated with the Spoonacular API.

## 🌟 Features

- **Recipe Search**: Find recipes by ingredients or dish names
- **Category Browsing**: Browse recipes by type (vegetarian, meat, quick meals)
- **Detailed Recipes**: Get ingredients, instructions, and descriptions
- **Persistent Menu**: Easy-to-use reply keyboard that stays visible
- **Pagination**: Navigate through recipe lists with Previous/Next buttons
- **API Integration**: Real recipes from Spoonacular API
- **Responsive Design**: Works great on both mobile and desktop

## 📱 Bot Menu

The bot features a persistent reply keyboard with these options:

- 🔍 **Search Recipes** - Search by keyword
- 📚 **Random Recipes** - Discover new recipes
- ⭐ **Popular** - Most searched recipes
- 🥗 **Vegetarian** - Plant-based options
- 🥩 **Meat** - For meat lovers
- ⏱ **Quick (<30min)** - Fast meal ideas
- ❓ **Help** - Usage instructions

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- Telegram account
- Spoonacular API key (free tier available)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/Air-Fryer-Recipes.git
cd Air-Fryer-Recipes
```
2. **Create a virtual environment** :
~~~bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
~~~
3. **Install dependencies** :
~~~bash
pip install python-telegram-bot aiohttp
~~~
4. **Get API keys** :
   
- Telegram Bot Token : Talk to @BotFather on Telegram
- Spoonacular API Key : Sign up at Spoonacular API
 
5. **Configure the bot** :
 
- Open `bot.py`

- Replace `"YOUR_TELEGRAM_BOT_TOKEN"` with your Telegram bot token
 
- Replace `"YOUR_SPOONACULAR_API_KEY"` with your Spoonacular API key

 # Running the Bot
~~~bash
python bot.py
~~~

# 🛠️ Configuration

**Environment Variables (Recommended)**

Create a `.env` file in the project root:
~~~bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
SPOONACULAR_API_KEY=your_spoonacular_api_key_here
~~~

# 📊 API Usage

The bot uses the `Spoonacular API` which offers:

- Free tier: 150 requests per day
- Recipe search and filtering
- Detailed recipe information
- Equipment-based filtering (air fryer)

# 🏗️ Project Structure
~~~bash
air-fryer-recipes-bot/
├── bot.py                 # Main bot application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore file
└── LICENSE               # MIT License
~~~

# 📦 Dependencies

- `python-telegram-bot` - Telegram Bot API wrapper
- `aiohttp` - Async HTTP client for API requests
- `python-dotenv` (optional) - Environment variable management

  # 🎯 Usage Examples

- Click "🔍 Search Recipes"
- Enter a search term (e.g., "chicken", "vegetables")
- Browse results with pagination
- Click any recipe to see details

**Browsing Categories**

- Use menu buttons to select a category
- Browse recipes in that category
- View detailed recipe information

# 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
