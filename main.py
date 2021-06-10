import datetime
from pprint import pprint
from random import randint
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, \
    ConversationHandler

# from nlp import get_stems, check_stems
# from key_words import KeyWords
# from pycbrf_test import get_currency


from config import TOKEN
from key_words import KeyWords
from nlp import check_stems, get_stems

from soup import get_data


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Добро пожаловать! \n' +
                              'Я телеграм бот-помощник NLP-bank. Я могу показать информацию ' +
                              'о банке, посмотреть баланс, перевести деньги, забокировать ' +
                              'карту, написать в поддержку.')
    update.message.reply_text('Для начала работы введите номер вашей карты')

    return 1


def sort_by_profit(update: Update, context: CallbackContext, reverse=True,
                   period='12_monthly_growth',
                   start_index=0):
    """
    Print most profit actives per 12 week/month/year/month
    You can set reverse for sorting
    """
    global content_count_per_page
    if period == '12_monthly_growth':
        grow_period = 'годовой'
    elif period == 'yearly_growth':
        grow_period = 'с начала года'
    elif period == 'monthly_growth':
        grow_period = 'месячный'
    else:
        grow_period = 'недельный'

    most_profit_data = sorted(data.values(), key=lambda x: x[period], reverse=reverse)
    message = ''
    for i in range(start_index, start_index + content_count_per_page):
        message += f'{i + 1} "{most_profit_data[i]["name"]}" {grow_period} рост: {most_profit_data[i][period]}\n'

    update.message.reply_text(message)


def search_by_company_name(update: Update, context: CallbackContext, company_name):
    """
    This function print all information about any company by name

    """
    suffixes = ["", ' АО', '-АО', '. АО', ' АП', "-ГДР", "-П", " ЗАП", " ЗАО"]
    for suffix in suffixes:
        if data.get(company_name + suffix, False):
            company_name += suffix
            break
    else:
        update.message.reply_text('К сожалению компания по вашему запросу не найдена')
        return
    search_result = data[company_name]
    message = f"Акции компании {company_name} \n" \
              f"Время последней сделки: {search_result['upload_time']} \n" \
              f"Текущая стоимость: {search_result['cost']}руб\n" \
              f"Рост за неделю: {search_result['weekly_growth']}%\n" \
              f"Рост за месяц: {search_result['monthly_growth']}%\n" \
              f"Рост с начала года: {search_result['yearly_growth']}%\n" \
              f"Рост за 12 месяцев: {search_result['12_monthly_growth']}%\n" \
              f"Объем акций: {search_result['volume']}руб\n" \
              f"Изменение объема за год: {search_result['delta_volume']}%\n"

    update.message.reply_text(message)


def refresh_data(update: Update, context: CallbackContext):
    global data
    update.message.reply_text(f"Данные будут обновляться примерно 5 секунд")
    data = get_data()
    update.message.reply_text(f"Данные обновлены {datetime.datetime.today()}")


def set_content_count_per_page(update: Update, context: CallbackContext, count):
    global content_count_per_page
    content_count_per_page = count
    update.message.reply_text(f"Установлено кол-во просматриваемых акций в одном сообщении равное {count}")


def stream(update, context):
    """
    main handler for messages
    checking keywords in message
    """

    is_answered = False
    global content_count_per_page
    stems = get_stems(update.message.text)
    print(stems)

    # sorting by profit
    global period_gl, start_index_gl, reverse_gl
    reverse_gl = True
    if check_stems(stems, KeyWords.increase):
        reverse_gl = False
    if check_stems(stems, KeyWords.profit):
        start_index_gl = 0
        if check_stems(stems, KeyWords.week):
            period_gl = 'weekly_growth'
        elif check_stems(stems, KeyWords.month):
            period_gl = 'monthly_growth'
        elif check_stems(stems, KeyWords.year):
            period_gl = 'yearly_growth'
        else:
            period_gl = '12_monthly_growth'

        sort_by_profit(update, context, reverse=reverse_gl, period=period_gl,
                       start_index=start_index_gl)
    elif check_stems(stems, KeyWords.extra_content):
        start_index_gl += content_count_per_page
        sort_by_profit(update, context, reverse=reverse_gl, period=period_gl,
                       start_index=start_index_gl)

    # searching by company name
    elif check_stems(stems, KeyWords.search):
        if len(stems) == 2:
            for word in update.message.text.split():
                if get_stems(word)[0] not in KeyWords.search:
                    search_by_company_name(update, context, word.upper())

    elif check_stems(stems, KeyWords.refresh):
        """refresh data """
        refresh_data(update, context)

    elif check_stems(stems, KeyWords.set_content_count):
        """set content count per page"""
        for word in update.message.text.split():
            if word.isdigit():
                set_content_count_per_page(update, context, int(word))


def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    text_handler = MessageHandler(Filters.text, stream)

    dispatcher.add_handler(text_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    data = get_data()
    content_count_per_page = 15
    main()
