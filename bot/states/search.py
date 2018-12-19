
from telegram import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button

from ..main import logger, db
from ..util import build_menu


def search(bot, update, user_data):
    
    n_pos = 5
    callback = update.callback_query
    message = update.message

    # обработать сообщение пользователя
    if message:
        result = db.find(message.text)
        user_data['search_query'] = message.text
        user_data['search_result'] = result.reset_index()['name'].values
        user_data['tmp_search_result_ix'] = result.index.values
        user_data['search_result_pos'] = 0

    # обработать нажатие кнопки
    if callback:
        data = callback.data

        if data == 'search':
            ans = 'Давайте поищем ценные бумаги в моем каталоге. Напишите поисковой запрос!'
            callback.edit_message_text(ans)
            return 'SEARCH'
        elif data == 'prev':
            user_data['search_result_pos'] -= n_pos
        elif data == 'next':
            user_data['search_result_pos'] += n_pos
        else:
            portfolio = user_data['portfolio'][user_data['current_portfolio']] 
            id = user_data['tmp_search_result_ix'][int(data)]
            portfolio.add_asset(id)
            res = user_data['search_result']
            name = user_data['search_result'][int(data)]
            callback.answer(f'{name} добавлено в портфель')
            user_data['search_result'] = res[res != name]
            portfolio.update()
            
    # формирование меню
    pos =  user_data['search_result_pos']
    res = user_data['search_result']
    
    # обновление месседжа
    if len(res) > 0:
        button_list = [Button(x, callback_data=i+pos) for i,x in enumerate(res[pos:pos+n_pos])]

        footer = [Button('Вернуться', callback_data='done')]
        if pos-n_pos >= 0:
            footer.append(Button('<-', callback_data='prev'))
        if pos+n_pos < len(res):
            footer.append(Button('->', callback_data='next'))

        reply_markup = Markup(
            build_menu(button_list, n_cols=1, footer_buttons=footer)
        )

        ans = f"Вот результаты по запросу '{user_data['search_query']}'. \n"\
            "Если нужно поискать что-то еще, просто напиши мне."
    else:
        ans = f"По запросу '{user_data['search_query']}' нет результатов... Поищем что-нибудь другое?"

    if callback:
        callback.edit_message_text(ans, reply_markup=reply_markup)
    else:
        update.message.reply_text(ans, reply_markup=reply_markup)

    return 'SEARCH'
