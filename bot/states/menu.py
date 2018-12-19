
from telegram import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button



def menu(bot, update, user_data):

    # удаление временных данных пользователя
    # < deprecated
    tmp_data = ['search_query', 'search_result', 'search_result_pos', 
                'search_result_dict', 'new_portfolio_name', 'list_pos', 'callback']
    for i in tmp_data:
        if i in user_data:
            del user_data[i]
    # deprecated >

    user_data_keys = list(user_data.keys())
    for i in user_data_keys:
        if i.startswith('tmp_'):
            del user_data[i]
    

    callback = update.callback_query
    if callback:
        reply = callback.edit_message_text
    else:
        reply = update.message.reply_text

    # формирование меню
    button_list = [
        [Button('Contents', callback_data='info'), Button('Update', callback_data='update')],
        [Button('Buy', callback_data='buy'), Button('Sell', callback_data='sell')],
        # [Button('Заплатить комиссию', callback_data='fee')],
        [Button('Stats', callback_data='stats')],
        [Button('Favourites', callback_data='fav'),
         Button('+ Add', callback_data='search')],
    ]

    reply_markup = Markup(button_list)

    pf = user_data["portfolio"][user_data["current_portfolio"]]

    stats = pf.get_alltime_stats().iloc[0]

    ans = f'Hi! I\'m the investment portfolio helper. '\
          f'I collect statistics, make reports and draw plots. \n\n'\
          f'Current portfolio: {user_data["current_portfolio"]}\n'\
          f'Creation date: {pf.creation_date.strftime("%x")}.\n'\
          f'{len(pf.asset_list)} assets in favourites.\n'\
          f'Positions open: {(pf.get_position_list()["Type"] == "buy").values.sum()} ({stats["Invested"]} RUB).\n'\
          f'Positions closed: {(pf.get_position_list()["Type"] == "sell").values.sum()} ({stats["Closed"]} RUB).\n\n'\
          f'Current portfolio price: {stats["Current portfolio price"]:.1f} RUB\n'\
          f'Result: {stats["Result"]:.1f} RUB ({stats["Result %"]:.1f}%)\n\n'\
          f'Last updated: {pf.last_updated.strftime("%x")}.\n'\
          
    reply(ans, reply_markup=reply_markup)

    return 'MENU'