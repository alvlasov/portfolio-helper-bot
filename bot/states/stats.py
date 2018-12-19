
from telegram import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button
from ..util import parse_date, parse_amount, build_menu

from ..main import logger




def stats(bot, update, user_data):

    callback = update.callback_query
    message = update.message

    portfolio = user_data["portfolio"][user_data["current_portfolio"]]
    if 'tmp_list_pos' not in user_data: 
        user_data['tmp_list_pos'] = 0
        user_data['tmp_stats'] = portfolio.get_monthly_stats()

  
    if callback:
        data = callback.data

        if data == 'prev':
            user_data['tmp_list_pos'] -= 1
        elif data == 'next':
            user_data['tmp_list_pos'] += 1

    #     Start date                            2018-12-01 00:00:00
    # End date                              2018-12-18 00:00:00
    # FinEx Gold ETF USD (RUB)                    578.5 (+1.22)
    # FinEx MSCI China UCITS ETF (RUB)           2430.0 (-3.57)
    # FinEx MSCI Germany UCITS ETF (RUB)         1917.5 (-5.54)
    # Альфа-Капитал Баланс                       2078.7 (-1.00)
    # Альфа-Капитал Еврооблигации               4376.87 (+1.22)
    # Сбербанк - Еврооблигации                  2483.85 (+0.49)
    # Сбербанк – Арендный бизнес                     nan (+nan)
    # Portfolio                                      nan (+nan)
    # Adjusted portfolio result                            +nan
    # Invested                                                0
    # Closed                                                  0
    
    pos =  user_data['tmp_list_pos']
    stats =  user_data['tmp_stats'].iloc[pos]

    assets_stats = stats.iloc[2:-4]

    assets_str = '\n'.join([f'{i}\n 💠 {j}' for i, j in assets_stats.items()])
    ans = f"Period: {stats['Start date'].strftime('%x')} - {stats['End date'].strftime('%x')}\n\n"\
          f"{assets_str}\n"\
          f"Portfolio: {stats['Portfolio']}\n"\
          f"Adjusted: {stats['Adjusted portfolio result']}\n"

    if stats['Invested'] > 0.0: 
        ans += f"Invested: {stats['Invested']}\n"
    if stats['Closed'] > 0.0: 
        ans += f"Closed: {stats['Closed']}"
          
    
    footer = [Button('Return', callback_data='done')]
    if pos-1 >= 0:
        footer.append(Button('<-', callback_data='prev'))
    if pos+1 < len(stats):
        footer.append(Button('->', callback_data='next'))

    

    reply_markup = Markup([footer])

    if callback:
        callback.edit_message_text(ans, reply_markup=reply_markup)
    else:
        update.message.reply_text(ans, reply_markup=reply_markup)

    return 'STATS'