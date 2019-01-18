import telegram
import logging
import backend.api.telegram

from backend import constants
from backend.scheduler.jobs import catalogue
from backend.commands.wrapper import send_typing_action, send_upload_photo_action, send_upload_video_action
from backend.database.statement import insert, select, update as update_db
from backend.commands.command import television, movies
from backend.commands import checker

@send_typing_action
def access(bot, update):
    if(checker.checkAdminAllowed(update)):
        keyboard = []
        for status in range(len(constants.ACCOUNT_STATUS)):
            keyboard.append([telegram.InlineKeyboardButton(constants.ACCOUNT_STATUS[status], callback_data=constants.ADMIN_ACCESS_TYPE_CALLBACK+constants.ACCOUNT_STATUS[status])])
        reply_markup = telegram.InlineKeyboardMarkup(keyboard)
        update.message.reply_text(constants.ADMIN_ACCESS_START_MSG, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)

def accessTypeCallback(bot, update):
    status = update.callback_query.data[len(constants.ADMIN_ACCESS_TYPE_CALLBACK):]
    status_code = constants.ACCOUNT_STATUS.index(status)
    users = select.getUsersWithStatus(status_code)
    keyboard = []
    for user in users:
        text = str(user[0])+": "+user[5]
        keyboard.append([telegram.InlineKeyboardButton(text, callback_data=constants.ADMIN_ACCESS_USER_CALLBACK+str(user[0]))])
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(text=constants.ADMIN_ACCESS_USERS_MSG.format(status.lower()), reply_markup=reply_markup, chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, parse_mode=telegram.ParseMode.MARKDOWN)
    
def accessUserCallback(bot, update):
    telegram_id = update.callback_query.data[len(constants.ADMIN_ACCESS_TYPE_CALLBACK):]
    keyboard = []
    for status in constants.ACCOUNT_STATUS:
        keyboard.append([telegram.InlineKeyboardButton(status, callback_data=constants.ADMIN_ACCESS_SET_CALLBACK+str(telegram_id)+","+status)])
    reply_markup = telegram.InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(text=constants.ADMIN_ACCESS_SET_MSG, reply_markup=reply_markup, chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, parse_mode=telegram.ParseMode.MARKDOWN)
    
def accessSetCallback(bot, update):
    results =  update.callback_query.data[len(constants.ADMIN_ACCESS_SET_CALLBACK):].split(",")
    status_code = constants.ACCOUNT_STATUS.index(results[1])
    user = select.getUser(results[0])
    msg = constants.ADMIN_ACCESS_SUCCESS.format(user[0], user[5], results[1].lower())
    update_db.updateUserStatus(user[0], status_code)
    bot.edit_message_text(text=msg, chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id, parse_mode=telegram.ParseMode.MARKDOWN)
    logging.getLogger(__name__).info(msg[1:-1])
    bot.send_message(chat_id=user[0], text=constants.ACCOUNT_STATUS_MSG[status_code], parse_mode=telegram.ParseMode.MARKDOWN)

# Force update the database(s)
@send_typing_action
def forceUpdate(bot, update, args):
    if(checker.checkAdminAllowed(update)):
        if(len(args) == 1):
            if(args[0] == "shows"):
                television.forceUpdate(bot, update)
            elif(args[0] == "movies"):
                movies.forceUpdate(bot, update)
            elif(args[0] == "all"):
                television.forceUpdate(bot, update)
                movies.forceUpdate(bot, update)
            else:
                update.message.reply_text(constants.ADMIN_FORCEUPDATE_FAILED_TYPE, parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            update.message.reply_text(constants.ADMIN_FORCEUPDATE_FAILED_ARGS, parse_mode=telegram.ParseMode.MARKDOWN)