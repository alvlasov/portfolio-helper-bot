
from telegram import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button

from ..AssetUtils import AssetPortfolio
from ..main import db
from ..util import parse_date


def create_portfolio(bot, update, user_data):

    if update.callback_query:
        reply = update.callback_query.edit_message_text
    else:
        reply = update.message.reply_text

    callback = update.callback_query
    message = update.message

    if callback:
        data = callback.data
        # if data == 'create':

    if user_data['callback'] == 'ask_name':
        ans = f'Вы назвали свой портфель "{message.text}".'\
               'Теперь выберите дату его создания. Котировки ценных бумаг будут загружаться начиная с этой даты.'\
               'Кроме того, вы не сможете добавлять операции с меньшей датой.'
        user_data['new_portfolio_name'] = message.text
        user_data['callback'] = 'ask_date'

    elif user_data['callback'] == 'ask_date':
        try:
            date = parse_date(message.text)
            date_str = date.strftime("%x")
            ans = f'Дата создания - {date_str}. Отлично, теперь у вас есть портфель! Теперь давайте перейдем в главное меню!'
            if 'portfolio' not in user_data:
                user_data['portfolio'] = {}

            name = user_data['new_portfolio_name']
            user_data['portfolio'][name] = AssetPortfolio(db, date)
            user_data['current_portfolio'] = name

            reply_markup = Markup([[Button('В меню!', callback_data='menu')]])

            reply(ans,reply_markup=reply_markup)
            del user_data['callback']
            return 'MENU'

        except (ValueError, AttributeError):
            ans = f'У меня не получилось определить, какую дату вы назвали... Можете уточнить?'

        
    reply(ans)

    return 'CREATE_PORTFOLIO'