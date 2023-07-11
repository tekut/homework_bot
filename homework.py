import telegram
import os
from telegram import Bot
from telegram.ext import Updater
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения,
    которые необходимы для работы программы."""
    var_names = ["PRACTICUM_TOKEN", "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID"]
    var_values = [os.getenv(var_name) for var_name in var_names]
    for var_name, var_value in zip(var_names, var_values):
        print(f"Переменная окружения {var_name} недоступна.")
    else:
        print(f"Значение переменной окружения {var_name}: {var_value}")


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат"""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение отправлено '
                      f'{TELEGRAM_CHAT_ID}: {message}')
        logger.debug('Сообщение отправлено ')
    except Exception as error:
        logging.error(f'Ошибка при отправке сообщения: {error}')


def get_api_answer(timestamp):
    """Делает запрос к Практикуму"""
    payload = {'from_date': timestamp}
    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=payload)
    response = homework_statuses.json()
    return response

#def check_response(response):
#    """Проверяет ответ API на соответствие документации"""
#    ...


def parse_status(homework):
    """Извлекает из информации о конкретной
    домашней работе статус этой работы"""
    homework_name = homework['homework_name']
    status_homework = homework['status']
    verdict = HOMEWORK_VERDICTS[status_homework]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())



    while True:
        try:

            ...

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
        ...


if __name__ == '__main__':
    main()
