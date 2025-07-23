import logging
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    ContextTypes,
    MessageHandler,
    filters
)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Store search results temporarily
user_searches = {}

# API configuration
API_BASE_URL = "https://api.spoonacular.com/recipes"
API_KEY = "YOUR_SPOONACULAR_API_KEY"  # Get free key at https://spoonacular.com/food-api

# Main menu keyboard
MAIN_MENU_KEYBOARD = [
    [KeyboardButton("🔍 Search Recipes"), KeyboardButton("📚 Random Recipes")],
    [KeyboardButton("⭐ Popular"), KeyboardButton("🥗 Vegetarian")],
    [KeyboardButton("🥩 Meat"), KeyboardButton("⏱ Quick (<30min)")],
    [KeyboardButton("❓ Help")]
]

def get_main_menu_markup():
    return ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True, one_time_keyboard=False)

async def fetch_recipes(query: str = "", number: int = 10, cuisine: str = "", diet: str = "", max_ready_time: int = 0) -> list:
    """Fetch recipes from Spoonacular API"""
    if not API_KEY or API_KEY == "YOUR_SPOONACULAR_API_KEY":
        # Return sample data if no API key is provided
        sample_recipes = [
            {"id": 1, "title": "Crispy Air Fryer Chicken", "image": "https://spoonacular.com/recipeImages/716429-312x231.jpg"},
            {"id": 2, "title": "Air Fryer Salmon", "image": "https://spoonacular.com/recipeImages/644387-312x231.jpg"},
            {"id": 3, "title": "Vegetable Skewers", "image": "https://spoonacular.com/recipeImages/639939-312x231.jpg"},
            {"id": 4, "title": "Air Fryer Steak", "image": "https://spoonacular.com/recipeImages/636759-312x231.jpg"},
            {"id": 5, "title": "Sweet Potato Fries", "image": "https://spoonacular.com/recipeImages/633547-312x231.jpg"}
        ]
        return sample_recipes[:number]
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{API_BASE_URL}/complexSearch"
            params = {
                "apiKey": API_KEY,
                "number": number,
                "instructionsRequired": True,
                "equipment": "air fryer"
            }
            
            if query:
                params["query"] = query
            if cuisine:
                params["cuisine"] = cuisine
            if diet:
                params["diet"] = diet
            if max_ready_time > 0:
                params["maxReadyTime"] = max_ready_time
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("results", [])
                else:
                    logger.error(f"API request failed with status {response.status}")
                    return []
    except Exception as e:
        logger.error(f"Error fetching recipes: {e}")
        return []

async def fetch_recipe_details(recipe_id: int) -> dict:
    """Fetch detailed recipe information"""
    if not API_KEY or API_KEY == "YOUR_SPOONACULAR_API_KEY":
        # Return sample detailed data
        return {
            "title": "Air Fryer Chicken Breast",
            "image": "https://spoonacular.com/recipeImages/716429-556x370.jpg",
            "summary": "Perfectly crispy air fryer chicken breast with minimal oil. Ready in just 20 minutes!",
            "extendedIngredients": [
                {"original": "2 boneless, skinless chicken breasts"},
                {"original": "1 tablespoon olive oil"},
                {"original": "1 teaspoon garlic powder"},
                {"original": "1 teaspoon paprika"},
                {"original": "Salt and pepper to taste"}
            ],
            "instructions": "1. Preheat air fryer to 375°F (190°C).\n2. Pat chicken dry and brush with olive oil.\n3. Season with garlic powder, paprika, salt, and pepper.\n4. Cook for 10 minutes, flip, and cook another 6-8 minutes until internal temp reaches 165°F."
        }
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get recipe details
            url = f"{API_BASE_URL}/{recipe_id}/information"
            params = {
                "apiKey": API_KEY,
                "includeNutrition": False
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Recipe details request failed with status {response.status}")
                    return {}
    except Exception as e:
        logger.error(f"Error fetching recipe details: {e}")
        return {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message with main menu"""
    welcome_message = (
        "🔥 *Welcome to Air Fryer Recipes Bot!* 🔥\n\n"
        "I'll help you discover delicious air fryer recipes!\n\n"
        "🍽 *Features:*\n"
        "• Search recipes by ingredients\n"
        "• Browse popular dishes\n"
        "• Find quick meals (<30 min)\n"
        "• Vegetarian options\n"
        "• Meat lover's selections\n\n"
        "Use the menu below to get started:"
    )
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=get_main_menu_markup(),
        parse_mode='Markdown'
    )

async def show_recipes(update: Update, context: ContextTypes.DEFAULT_TYPE, recipes=None, page=0, title="Recipes") -> None:
    """Display recipes with pagination"""
    query = update.callback_query
    message = update.message
    
    # Determine if this is a callback query or regular message
    if query:
        await query.answer()
        msg_obj = query.message
    else:
        msg_obj = message
    
    if recipes is None:
        recipes = await fetch_recipes()
    
    if not recipes:
        no_results_text = "No recipes found. Try a different search term or category."
        if query:
            await query.edit_message_text(no_results_text, reply_markup=get_main_menu_markup())
        else:
            await message.reply_text(no_results_text, reply_markup=get_main_menu_markup())
        return
    
    # Pagination logic
    page_size = 3
    start_idx = page * page_size
    end_idx = start_idx + page_size
    page_recipes = recipes[start_idx:end_idx]
    
    if not page_recipes:
        no_more_text = "No more recipes to show."
        if query:
            await query.edit_message_text(no_more_text, reply_markup=get_main_menu_markup())
        else:
            await message.reply_text(no_more_text, reply_markup=get_main_menu_markup())
        return
    
    # Create recipe buttons
    keyboard = []
    for recipe in page_recipes:
        keyboard.append([InlineKeyboardButton(recipe['title'], callback_data=f"recipe_{recipe['id']}")])
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"page_{page-1}"))
    if end_idx < len(recipes):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Main menu button
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = f"📋 *{title}*\nShowing recipes {start_idx+1}-{min(end_idx, len(recipes))} of {len(recipes)}:"
    
    if query:
        await query.edit_message_text(message_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await message.reply_text(message_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_recipe_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, recipe_id: int) -> None:
    """Show detailed recipe information"""
    query = update.callback_query
    await query.answer()
    
    # Show loading message
    await query.edit_message_text("🔍 Fetching recipe details...")
    
    recipe = await fetch_recipe_details(recipe_id)
    if not recipe:
        await query.edit_message_text("Recipe not found!", reply_markup=get_main_menu_markup())
        return
    
    # Format ingredients
    ingredients = "\n".join([f"• {ingredient['original']}" for ingredient in recipe.get('extendedIngredients', [])])
    
    # Format instructions
    instructions = recipe.get('instructions', 'No instructions available')
    
    # Clean up HTML tags from summary
    summary = recipe.get('summary', 'No description available').replace('<b>', '').replace('</b>', '').replace('<a href.*?>', '').replace('</a>', '')
    
    message = (
        f"🔥 *{recipe['title']}*\n\n"
        f"📋 *Ingredients:*\n{ingredients}\n\n"
        f"📝 *Instructions:*\n{instructions}\n\n"
        f"📖 *Description:*\n{summary[:200]}{'...' if len(summary) > 200 else ''}"
    )
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Back to Recipes", callback_data='recipes')],
        [InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help message"""
    help_text = (
        "❓ *Air Fryer Recipes Bot Help*\n\n"
        "This bot helps you find delicious air fryer recipes!\n\n"
        "📱 *How to use:*\n"
        "• Use the menu buttons to navigate\n"
        "• Tap 'Search Recipes' to find recipes by name\n"
        "• Browse categories like 'Vegetarian' or 'Quick'\n"
        "• Click on any recipe to see details\n\n"
        "📋 *Categories:*\n"
        "• 📚 Random - Surprise recipes\n"
        "• ⭐ Popular - Most searched recipes\n"
        "• 🥗 Vegetarian - Plant-based options\n"
        "• 🥩 Meat - For meat lovers\n"
        "• ⏱ Quick - Under 30 minutes\n\n"
        "👨‍🍳 Happy cooking!"
    )
    
    await update.message.reply_text(help_text, reply_markup=get_main_menu_markup(), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all inline button presses"""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == 'main_menu':
        await start(update, context)
    elif data == 'recipes':
        recipes = await fetch_recipes()
        await show_recipes(update, context, recipes, 0, "Random Recipes")
    elif data.startswith('page_'):
        page = int(data.split('_')[1])
        user_id = update.effective_user.id
        recipes = user_searches.get(user_id, await fetch_recipes())
        await show_recipes(update, context, recipes, page)
    elif data.startswith('recipe_'):
        recipe_id = int(data.split('_')[1])
        await show_recipe_detail(update, context, recipe_id)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages (menu selections and search queries)"""
    text = update.message.text
    
    # Handle menu selections
    if text == "🔍 Search Recipes":
        await update.message.reply_text(
            "Enter a search term (e.g., chicken, vegetables, beef):"
        )
        context.user_data['awaiting_search'] = True
        
    elif text == "📚 Random Recipes":
        await update.message.reply_text("🔍 Fetching random recipes...")
        recipes = await fetch_recipes()
        await show_recipes(update, context, recipes, 0, "Random Recipes")
        
    elif text == "⭐ Popular":
        await update.message.reply_text("🔍 Fetching popular recipes...")
        recipes = await fetch_recipes(query="popular")
        await show_recipes(update, context, recipes, 0, "Popular Recipes")
        
    elif text == "🥗 Vegetarian":
        await update.message.reply_text("🔍 Fetching vegetarian recipes...")
        recipes = await fetch_recipes(diet="vegetarian")
        await show_recipes(update, context, recipes, 0, "Vegetarian Recipes")
        
    elif text == "🥩 Meat":
        await update.message.reply_text("🔍 Fetching meat recipes...")
        recipes = await fetch_recipes(query="meat")
        await show_recipes(update, context, recipes, 0, "Meat Recipes")
        
    elif text == "⏱ Quick (<30min)":
        await update.message.reply_text("🔍 Fetching quick recipes...")
        recipes = await fetch_recipes(max_ready_time=30)
        await show_recipes(update, context, recipes, 0, "Quick Recipes (<30min)")
        
    elif text == "❓ Help":
        await show_help(update, context)
        
    # Handle search queries
    elif context.user_data.get('awaiting_search'):
        search_term = text.lower()
        user_id = update.effective_user.id
        
        # Show searching message
        await update.message.reply_text("🔍 Searching for recipes...")
        
        # Fetch recipes from API
        results = await fetch_recipes(search_term, 15)
        user_searches[user_id] = results
        
        # Reset search state
        context.user_data['awaiting_search'] = False
        
        if results:
            await show_recipes(update, context, results, 0, f"Search Results: {search_term}")
        else:
            await update.message.reply_text(
                f"Sorry, no recipes found for '{search_term}'. Try another search term.",
                reply_markup=get_main_menu_markup()
            )
    else:
        # Handle unrecognized commands
        await update.message.reply_text(
            "I didn't understand that. Please use the menu buttons below:",
            reply_markup=get_main_menu_markup()
        )

def main() -> None:
    """Run the bot"""
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
    application = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    
    # Callback query handler (for inline buttons)
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Message handler (for menu selections and search terms)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
