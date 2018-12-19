
from telegram import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button
from ..util import parse_date, parse_amount, build_menu

from ..main import logger

def info(bot, update, user_data):

    callback = update.callback_query
    message = update.message

    portfolio = user_data["portfolio"][user_data["current_portfolio"]]
    counts = portfolio.get_asset_counts().iloc[0, 0:-1]
    rates = portfolio.get_distribution().iloc[0, 0:-1]

    assets_str = '\n'.join([f'{i}\n 💠 {j} ({l*100:.1f}%)' for (i, j), (k,l) in zip(counts.items(), rates.items()) if j>0.0])

    ans = f"Your portfolio contents:\n\n{assets_str}"
    
    footer = [Button('Return', callback_data='done')]
    reply_markup = Markup([footer])

    if callback:
        callback.edit_message_text(ans, reply_markup=reply_markup)
    else:
        update.message.reply_text(ans, reply_markup=reply_markup)

    return 'INFO'