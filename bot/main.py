
import locale
import logging


logging.basicConfig(level=logging.INFO)
import os
import sys
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler,
                          PicklePersistence, RegexHandler, Updater, Job,
                          RegexHandler)

from . import AssetUtils

db = AssetUtils.AssetDatabase()

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor()
futures = {}

from .states import create_portfolio, menu, search, list_assets, add_transaction, stats, info

# locale.setlocale(locale.LC_ALL, 'ru_RU')

def start(bot, update, user_data):
    logger.info(f"start, user data = {user_data}")

    if 'portfolio' in user_data:
        return menu(bot, update, user_data)
    else:

        ans = 'Привет! Я - помощник по инвестиционному портфелю. '\
              'Я собираю статистику, строю отчеты и графики. '\
              'Чтобы начать пользоваться, создайте свой первый портфель! '\
              'Для начала, придумайте ему название:'

        update.message.reply_text(ans)
        user_data['callback'] = 'ask_name'
        return 'CREATE_PORTFOLIO'

def show_data(bot, update, user_data):
    update.message.reply_text(f"User data: {user_data}")

def done(bot, update):
    update.message.reply_text("Bye!")
    return ConversationHandler.END

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


REQUEST_KWARGS={
    'proxy_url': 'socks5://vysyj.tgvpnproxy.me:1080',
    # Optional, if you need authentication:
    'urllib3_proxy_kwargs': {
        'username': 'telegram',
        'password': 'telegram',
    }
}

def update_job(bot, job : Job):
    pf = job.context
    pf.update()
    
def update_portfolio(bot, update, user_data, job_queue):
    callback = update.callback_query
    if 'portfolio_update_job' not in user_data:
        pf = user_data["portfolio"][user_data["current_portfolio"]]
        job_queue.run_repeating(update_job, 60, context=pf, name='portfolio_update_job', first=0)
        user_data['portfolio_update_job'] = 'portfolio_update_job'
        callback.answer('Portfolio update scheduled')
    else:
        jobs = job_queue.get_jobs_by_name(user_data['portfolio_update_job'])
        for j in jobs:
            j.schedule_removal()
        callback.answer('Portfolio update unscheduled')
        del user_data['portfolio_update_job']
    
def main():
    
    db.load_database('asset_database')

    pp = PicklePersistence(filename='bot_data')
    updater = Updater(token='475109240:AAFQFPD6z10fOIcHyOlAnU046KJkvKE7hj8', persistence=pp,
                     request_kwargs=REQUEST_KWARGS)

    dp = updater.dispatcher 
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start, pass_user_data=True),
        ],
        states={
            'MENU': [
                CommandHandler('start', menu, pass_user_data=True),
                CallbackQueryHandler(menu, pattern='^menu$', pass_user_data=True),
                CallbackQueryHandler(search, pattern='^search$', pass_user_data=True),
                CallbackQueryHandler(list_assets, pattern='^fav$', pass_user_data=True),
                CallbackQueryHandler(add_transaction, pattern='^buy$|^sell$', pass_user_data=True),
                CallbackQueryHandler(update_portfolio, pattern='^update$', pass_user_data=True, pass_job_queue=True),
                CallbackQueryHandler(stats, pattern='^stats$', pass_user_data=True),
                CallbackQueryHandler(info, pattern='^info$', pass_user_data=True),
                RegexHandler('.*search.*', search, pass_user_data=True),
                RegexHandler('.*favourites.*', list_assets, pass_user_data=True),
                RegexHandler('.*stat.*', stats, pass_user_data=True),
                RegexHandler('.*[info|inside|content].*', info, pass_user_data=True),
                MessageHandler(Filters.text, menu, pass_user_data=True),
            ],
            'CREATE_PORTFOLIO': [
                CallbackQueryHandler(create_portfolio, pattern='^create$', pass_user_data=True),
                MessageHandler(Filters.text, create_portfolio, pass_user_data=True),
            ],
            'SEARCH': [
                MessageHandler(Filters.text, search, pass_user_data=True),
                CallbackQueryHandler(menu, pattern='^done$', pass_user_data=True),
                CallbackQueryHandler(search, pass_user_data=True),
                RegexHandler('.*[back|done].*', menu, pass_user_data=True),
            ],
            'LIST_ASSETS': [
                RegexHandler('.*[back|done].*', menu, pass_user_data=True),
                CallbackQueryHandler(menu, pattern='^done$', pass_user_data=True),
                CallbackQueryHandler(list_assets, pass_user_data=True),

            ],
            'ADD_TRANSACTION': [
                CallbackQueryHandler(menu, pattern='^done$', pass_user_data=True),
                CallbackQueryHandler(add_transaction, pass_user_data=True),
                MessageHandler(Filters.text, add_transaction, pass_user_data=True),

            ],
            'STATS': [
                RegexHandler('.*[back|done].*', menu, pass_user_data=True),
                CallbackQueryHandler(menu, pattern='^done$', pass_user_data=True),
                CallbackQueryHandler(stats, pass_user_data=True),
            ],
            'INFO': [
                RegexHandler('.*[back|done].*', menu, pass_user_data=True),
                CallbackQueryHandler(menu, pattern='^done$', pass_user_data=True),
            ]

        },

        fallbacks=[RegexHandler('^Done$', done)],
    )

    dp.add_handler(conv_handler)

    show_data_handler = CommandHandler('show_data', show_data, pass_user_data=True)
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(show_data_handler)

    # log all errors
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()
