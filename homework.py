import logging
import os
import time

import requests
import telegram
from http import HTTPStatus
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    logging.info('Попытка отправки сообщения '
                 f'{TELEGRAM_CHAT_ID}: {message}')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(f'Ошибка при отправке сообщения: {error}')
    else:
        logging.debug('Сообщение успешно отправлено ')


def get_api_answer(timestamp):
    """Делает запрос к Практикуму."""
    payload = {'from_date': timestamp}
    logging.info(f'Отправка запроса на {ENDPOINT} с параметрами {payload}')
    try:
        response = requests.get(ENDPOINT,
                                headers=HEADERS,
                                params=payload,
                                )
    except Exception as error:
        logging.error(f'Ошибка при обращении к API: {error}')
        raise Exception(f'Ошибка при обращении к API: {error}')
    if response.status_code != HTTPStatus.OK:
        logging.error('Недоступность эндпоинта')
        raise Exception('Недоступность эндпоинта')
    try:
        api_response = response.json()
    except ValueError:
        logging.error('Ошибка парсинга')
        raise ValueError('Ошибка парсинга')
    return api_response


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        logging.error('Ответ API не словарь')
        raise TypeError('Ответ API не словарь')
    if 'homeworks' not in response:
        logging.error('В ответе отсутствует ключ "homeworks"')
        raise KeyError('В ответе отсутствует ключ "homeworks"')
    homework = response['homeworks']
    if not isinstance(homework, list):
        logging.error('В ответе под ключом homeworks - не список')
        raise TypeError('В ответе под ключом homeworks - не список')
    if len(homework) == 0:
        logging.error('Список домашек пуст')
        raise IndexError('Список домашек пуст')
    return homework[0]


def parse_status(homework):
    """Извлекает статус домашней работы."""
    if 'homework_name' not in homework:
        logging.error('В ответе API домашки нет ключа homework_name')
        raise KeyError('В ответе API домашки нет ключа homework_name')
    homework_name = homework['homework_name']
    status_homework = homework['status']
    if status_homework not in HOMEWORK_VERDICTS:
        logging.error(f'Некорректный статус работы: {status_homework}')
        raise KeyError(f'Некорректный статус работы: {status_homework}')
    verdict = HOMEWORK_VERDICTS[status_homework]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    first_status_message = ''

    if not check_tokens():
        logging.critical('Отсутствуют обязательные переменные окружения')
        raise Exception('Отсутствуют обязательные переменные окружения')

    while True:
        try:
            homework_response = get_api_answer(timestamp)
            homework = check_response(homework_response)
            message = parse_status(homework)
            if message != first_status_message:
                send_message(bot, message)
                first_status_message = message
        except telegram.error.TelegramError as error:
            message = f'Ошибка на стороне Telegram: {error}'
            send_message(bot, message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='main.log',
        filemode='w',
        format='%(asctime)s, %(levelname)s, %(message)s'
    )
    main()
