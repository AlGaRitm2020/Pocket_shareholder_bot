import datetime

from pprint import pprint
from random import randint
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, \
    ConversationHandler

from config import TOKEN
from key_words import KeyWords
from nlp import check_stems, get_stems

from soup import get_data


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Добро пожаловать! \n' +
                              'Я телеграм бот-помощник Smart invest bot.'
                              'Я могу выдавать вам информацию о акциях российский компаний '
                              'и сортировать акции по доходности на разные временные интервалы и по объему.'
                              'Кроме этого я могу искать акцию конкретной компании и сохранять ее в закладки.'
                              )

    return


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
    if start_index + content_count_per_page > 250:
        content_count_per_page = 250 - start_index
    for i in range(start_index, start_index + content_count_per_page):
        message += f'{i + 1} "{most_profit_data[i]["name"]}" {grow_period} рост: {most_profit_data[i][period]}\n'

    global start_index_gl
    start_index_gl += content_count_per_page
    update.message.reply_text(message)


def sort_by_volume(update: Update, context: CallbackContext, reverse=True, start_index=0):
    """
    Print most profit actives per 12 week/month/year/month
    You can set reverse for sorting
    """
    global content_count_per_page

    sorted_data = sorted(data.values(), key=lambda x: x['volume'], reverse=reverse)
    message = ''
    for i in range(start_index, start_index + content_count_per_page):
        message += f'{i + 1} "{sorted_data[i]["name"]}" объем акций: {sorted_data[i]["volume"]}млн руб, рост объема:{sorted_data[i]["delta_volume"]}% в год \n'

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

    global search_result
    search_result = data[company_name]
    message = f"Акции компании {company_name} \n" \
              f"Время последней сделки: {search_result['upload_time']} \n" \
              f"Текущая стоимость: {search_result['cost']}руб\n" \
              f"Рост за неделю: {search_result['weekly_growth']}%\n" \
              f"Рост за месяц: {search_result['monthly_growth']}%\n" \
              f"Рост с начала года: {search_result['yearly_growth']}%\n" \
              f"Рост за 12 месяцев: {search_result['12_monthly_growth']}%\n" \
              f"Объем акций: {search_result['volume']}млн руб\n" \
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
    update.message.reply_text(
        f"Установлено кол-во просматриваемых акций в одном сообщении равное {count}")


def start_choice(update: Update, context: CallbackContext):
    return 1


def ask_about_sum(update: Update, context: CallbackContext):
    update.message.reply_text(f"Какой сумму вы готовы инвестировать? (в рублях)")
    print(12)
    return 2


def enter_sum(update: Update, context: CallbackContext):
    global summ
    summ = update.message.text
    if not summ.isdigit():
        update.message.reply_text(f"Сумма должна быть в виде целого числа")
        return 2
    update.message.reply_text(
        f"Какой минимальный годовой рост должен быть у компании в которую вы будете инвестировать?")
    return 3


def enter_min_growth(update: Update, context: CallbackContext):
    global min_growth
    min_growth = update.message.text
    stems = get_stems(min_growth)
    if check_stems(stems, KeyWords.skip):
        min_growth = str(-100)
    elif not min_growth.isdigit():
        update.message.reply_text(f"Минимальный годовой рост должен быть в виде целого числа")
        return 3

    update.message.reply_text(
        f"Какой максимальный годовой рост должен быть у компании в которую вы будете инвестировать?")
    return 4


def enter_max_growth(update: Update, context: CallbackContext):
    global max_growth
    max_growth = update.message.text
    stems = get_stems(max_growth)
    if check_stems(stems, KeyWords.skip):
        max_growth = float('inf')

    elif not max_growth.isdigit():

        update.message.reply_text(f"Максимальный годовой рост должен быть в виде целого числа")
        return 4

    update.message.reply_text(
        f"Какой минимальный объем акций должен быть у компании в которую вы будете инвестировать? (млн руб)")
    return 5


def enter_min_volume(update: Update, context: CallbackContext):
    global min_volume
    min_volume = update.message.text
    stems = get_stems(min_volume)
    if check_stems(stems, KeyWords.skip):
        min_volume = float('inf')

    elif not min_volume.isdigit():
        update.message.reply_text(f"Минимальный объем должен быть в виде целого числа")
        return 5

    update.message.reply_text(
        f"Какой максимальный объем акций должен быть у компании в которую вы будете инвестировать? (млн руб)")
    return 6


def choice_result(update: Update, context: CallbackContext, summ, min_growth, max_growth, min_volume, max_volume):
    update.message.reply_text(f"Choice result")


def enter_max_volume(update: Update, context: CallbackContext):
    global summ, max_volume, min_volume, max_growth, min_growth
    max_volume = update.message.text
    stems = get_stems(max_volume)
    if check_stems(stems, KeyWords.skip):
        max_volume = float('inf')

    elif not max_volume.isdigit():
        update.message.reply_text(f"Максимальный объем должен быть в виде целого числа")
        return 6

    choice_result(update, context, summ, min_growth, max_growth, min_volume, max_volume)


def show_bookmarks(update: Update, context: CallbackContext):
    global bookmarks
    message = "Закладки:\n"
    if not bookmarks:
        message += 'Здесь пока пусто'
    for i, bookmark in enumerate(bookmarks):
        message += f"{i + 1}. {bookmark['name']} стоимость: {bookmark['cost']}рублей\n"
    update.message.reply_text(message)


def delete_bookmark(update: Update, context: CallbackContext, bookmark):
    global bookmarks
    for i, elem in enumerate(bookmarks):
        if elem == bookmark:
            del bookmarks[i]
    update.message.reply_text(f"Закладка {bookmark['name']} успешно удалена")


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
    global search_result, bookmarks
    reverse_gl = True
    if check_stems(stems, KeyWords.increase):
        reverse_gl = False

    if check_stems(stems, KeyWords.volume):
        start_index_gl = 0
        sort_by_volume(update, context, reverse=reverse_gl, start_index=start_index_gl)

    elif check_stems(stems, KeyWords.profit):
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

        sort_by_profit(update, context, reverse=reverse_gl, period=period_gl,
                       start_index=start_index_gl)

    elif check_stems(stems, KeyWords.save):
        bookmarks.append(search_result)
        update.message.reply_text(f'{search_result["name"]} добавлен в закладки')

    elif check_stems(stems, KeyWords.delete):
        delete_bookmark(update, context, search_result)

    elif check_stems(stems, KeyWords.bookmarks):
        show_bookmarks(update, context)

    # searching by company name
    elif check_stems(stems, KeyWords.search):
        if len(stems) == 2:
            for word in update.message.text.split():
                if get_stems(word)[0] not in KeyWords.search:
                    search_by_company_name(update, context, word.upper())
    elif check_stems(stems, KeyWords.start_choice):
        start_choice(update, context)

    elif check_stems(stems, KeyWords.refresh):
        """refresh data"""
        refresh_data(update, context)

    elif check_stems(stems, KeyWords.set_content_count):
        """set content count per page"""
        for word in update.message.text.split():
            if word.isdigit():
                set_content_count_per_page(update, context, int(word))


def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dialog_choice = ConversationHandler(
        entry_points=[CommandHandler('start_choice', ask_about_sum)],
        states={
            # 1: [MessageHandler(Filters.text, ask_about_sum)],
            2: [MessageHandler(Filters.text, enter_sum)],
            3: [MessageHandler(Filters.text, enter_min_growth)],
            4: [MessageHandler(Filters.text, enter_max_growth)],
            5: [MessageHandler(Filters.text, enter_min_volume)],
            6: [MessageHandler(Filters.text, enter_max_volume)],

        },
        fallbacks=[MessageHandler(Filters.text, start)]
    )

    dispatcher.add_handler(dialog_choice)

    text_handler = MessageHandler(Filters.text, stream)
    dispatcher.add_handler(text_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    data = get_data()
    bookmarks = []
    content_count_per_page = 15
    main()
