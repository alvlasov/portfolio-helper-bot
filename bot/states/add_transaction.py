
from telegram import InlineKeyboardMarkup as Markup, InlineKeyboardButton as Button
from ..util import parse_date, parse_amount, build_menu

from ..main import logger

N_POS = 5

def add_transaction(bot, update, user_data):


    
    if 'tmp_state' not in user_data:
        user_data['tmp_state'] = 'ask_asset'

    callback = update.callback_query

    if callback:
        if callback.data in ['buy', 'sell']:
            user_data['tmp_pos_type'] = callback.data

    if user_data['tmp_state'] == 'ask_asset':
        return ask_asset(bot, update, user_data)

    elif user_data['tmp_state'] == 'ask_date':
        return ask_date(bot, update, user_data)

    elif user_data['tmp_state'] == 'ask_amount':
        return ask_amount(bot, update, user_data)
    elif user_data['tmp_state'] == 'ask_price':
        return ask_price(bot, update, user_data)

    elif user_data['tmp_state'] == 'confirm':
        return confirm(bot, update, user_data)

    return 'ADD_TRANSACTION'


def ask_asset(bot, update, user_data):

    if 'tmp_list_pos' not in user_data: 
        user_data['tmp_list_pos'] = 0
    
    pos =  user_data['tmp_list_pos']
    pf = user_data["portfolio"]
    nm = user_data["current_portfolio"]
    res = pf[nm].get_asset_list()["name"].values

    callback = update.callback_query

    if callback:
        if callback.data == 'prev':
            user_data['tmp_list_pos'] -= N_POS
        elif callback.data == 'next':
            user_data['tmp_list_pos'] += N_POS
        elif callback.data in res:
            user_data['tmp_asset'] = callback.data
            user_data['tmp_state'] = 'ask_date'
            return ask_date(bot, update, user_data)

    ans = f"Choose the asset from your favorites:"

    
    button_list = [Button(x, callback_data=x) for x in res[pos:pos+N_POS]]

    footer = [Button('Return', callback_data='done')]
    if pos-N_POS >= 0:
        footer.append(Button('<-', callback_data='prev'))
    if pos+N_POS < len(res):
        footer.append(Button('->', callback_data='next'))

    reply_markup = Markup(
        build_menu(button_list, n_cols=1, footer_buttons=footer)
    )

    if callback:
        callback.edit_message_text(ans, reply_markup=reply_markup)
    else:
        update.message.reply_text(ans, reply_markup=reply_markup)

    return 'ADD_TRANSACTION'

def ask_date(bot, update, user_data):
    callback = update.callback_query
    message = update.message

    if callback:
        data = callback.data
        user_data['tmp_asset'] = data#[6:]
        ans = f'You have chosen "{user_data["tmp_asset"]}"!\n\n'\
                'Now let\'s find out what\'s the date of your transaction. '\
                'Use any format to specify the date. I\'ll understand, I promise!'
        callback.edit_message_text(ans)

    if message:
        try:
            date = parse_date(message.text)

            portfolio = user_data["portfolio"][user_data["current_portfolio"]]
            if date < portfolio.creation_date:
                ans = f'The date is earlier than portfolio creation time! '\
                      f'Please specify the date later than {portfolio.creation_date.strftime("%x")}.'
            # TODO date >= today: error
            else:

                date_str = date.strftime("%x")
                ans = f'The date is {date_str}.\n\n'\
                    'Now specify the transaction amount.'
                user_data['tmp_date'] = date
                user_data['tmp_state'] = 'ask_amount'

        except (ValueError, AttributeError):
            ans = f'Unfortunately I couldn\'t understand you... Let\'s try again. '\
                   'Please tell me the date of the transaction!'

        update.message.reply_text(ans)

    return 'ADD_TRANSACTION'

def ask_amount(bot, update, user_data):

    message = update.message

    if message:
        try:
            amt = parse_amount(message.text)

            portfolio = user_data["portfolio"][user_data["current_portfolio"]]

            asset = [i for i in  portfolio.asset_list if i.name==user_data['tmp_asset']][0]
            

            ans = f'The amount is {amt}.\n\n'\
                  f'Now specify the transaction price.\nThe closing price at this day was {asset.get_price(user_data["tmp_date"])}.'
            user_data['tmp_amt'] = amt
            user_data['tmp_state'] = 'ask_price'

        except (ValueError, AttributeError):
            ans = f'Unfortunately I couldn\'t understand you... Let\'s try again. '\
                   'Please tell me the amount of your transaction!'

        update.message.reply_text(ans)

    return 'ADD_TRANSACTION'

def ask_price(bot, update, user_data):

    message = update.message

    if message:
        try:
            price = parse_amount(message.text)
            
            user_data['tmp_price'] = price
            ans = f'We\'re almost done!.\n\n'\
                   'Let\'s check the transaction atttibutes. '\
                  f"You want to {user_data['tmp_pos_type']} {user_data['tmp_amt']} units of {user_data['tmp_asset']}. "\
                  f"The transaction occured {user_data['tmp_date'].strftime('%x')} when the asset price was {user_data['tmp_price']}.\n\n"\
                   "Is everything correct?"
            user_data['tmp_state'] = 'confirm'
            reply_markup = Markup([[Button('Yes!', callback_data='yes'), Button('No..', callback_data='no')]])
            message.reply_text(ans, reply_markup=reply_markup)

        except (ValueError, AttributeError):
            ans = f'Unfortunately I couldn\'t understand you... Let\'s try again. '\
                   'Please tell me the price of your transaction!'
            message.reply_text(ans)

        
    return 'ADD_TRANSACTION'

def confirm(bot, update, user_data):

    callback = update.callback_query

    if callback:
        if callback.data == 'yes':
            ans = 'Great! The position was added succesfully!'

            portfolio = user_data["portfolio"][user_data["current_portfolio"]]


            assets = {item: key for key, item in dict(portfolio.get_asset_list()["name"]).items()}

            if user_data['tmp_pos_type'] == 'buy':
                transaction = portfolio.buy
            elif user_data['tmp_pos_type'] == 'sell':
                transaction = portfolio.sell

            transaction(assets[user_data['tmp_asset']], 
                        user_data['tmp_date'].strftime('%Y-%m-%d'), 
                        user_data['tmp_price'], 
                        user_data['tmp_amt'], 
                        0)

        elif callback.data == 'no':
            ans = ':( What a shame.. Let\'s go back to the menu..'
        
        reply_markup = Markup([[Button('Return to menu!', callback_data='done')]])    
        callback.edit_message_text(ans, reply_markup=reply_markup)

    return 'ADD_TRANSACTION'