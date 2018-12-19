from telegram import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button

from ..main import db, logger
from ..util import build_menu

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
plt.style.use('seaborn')

def list_assets(bot, update, user_data):

    logger.info(f'menu pos = {user_data.get("list_pos")}')
    
    n_pos = 5

    callback = update.callback_query
    message = update.message

    if 'list_pos' not in user_data: 
        user_data['list_pos'] = 0
    
    portfolio = user_data["portfolio"][user_data["current_portfolio"]]

    if callback:
        data = callback.data

        if data == 'prev':
            user_data['list_pos'] -= n_pos
        elif data == 'next':
            user_data['list_pos'] += n_pos
        elif len(portfolio.get_asset_list()) > 0:
            assets = {item: key for key, item in dict(portfolio.get_asset_list()["name"]).items()}
            if data.endswith('_desc'):
                for asset in portfolio.asset_list:
                    if asset.id == assets[data[:-5]]:
                        asset.stats['price'].plot(figsize=(10,3))
                        plt.savefig('plot.png', bbox_inches='tight')
                        plt.close()
                        bot.send_photo(chat_id=callback.message.chat_id, photo=open('plot.png', 'rb'))
            else:
                if data in assets:
                    portfolio.remove_asset(assets[data])

    # обновление месседжа

    pos =  user_data['list_pos']
    items = portfolio.get_asset_list()
    if len(items) > 0:
        res = items["name"].values
        ans = f"Избранные ценные бумаги.\n"\
            "Чтобы убрать ЦБ из избранного, нажмите на нее."
        
        button_list = [[Button(x, callback_data=x+'_desc'),
                        Button('Remove', callback_data=x)] for x in res[pos:pos+n_pos]]

        footer = [Button('Return', callback_data='done')]
        if pos-n_pos >= 0:
            footer.append(Button('<-', callback_data='prev'))
        if pos+n_pos < len(res):
            footer.append(Button('->', callback_data='next'))
        button_list.append(footer)
        reply_markup = Markup( button_list)

    else:
        ans = 'Favorites list is empty :('
        reply_markup = Markup([[Button('Return', callback_data='done')]])

    if callback:
        callback.message.reply_text(ans, reply_markup=reply_markup)
        # callback.edit_message_text(ans, reply_markup=reply_markup)
    else:
        update.message.reply_text(ans, reply_markup=reply_markup)

    return 'LIST_ASSETS'
