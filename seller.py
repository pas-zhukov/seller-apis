import io
import logging.config
import os
import re
import zipfile
from environs import Env

import pandas as pd
import requests

logger = logging.getLogger(__file__)


def get_product_list(last_id: str, client_id: str, seller_token: str) -> dict:
    """Получить список товаров магазина Ozon

    Делает запрос к API Ozon Seller, используя метод для получения списка товаров.
    Предусматривает пагинацию, чтобы было возможно перебрать все страницы с товарами.

    Args:
        last_id (str): Идентификатор последнего значения на странице.
        Оставьте это поле пустым при выполнении первого запроса.
        Чтобы получить следующие значения, укажите last_id из
        ответа предыдущего запроса.
        client_id (str): Идентификатор клиента Ozon
        seller_token (str): API-ключ Ozon Seller

    Returns:
        dict: Список карточек товаров с их свойствами

    Raises:
        HTTPError: Если в ответ на запрос не пришёл код 200

    Examples:

        >>> get_product_list("", client_id, seller_token)
        {
          "result": {
            "items": [
              {
                "product_id": 223681945,
                "offer_id": "136748"
              }
            ],
            "total": 1,
            "last_id": "bnVсbA=="
          }
        }

        >>> get_product_list("", client_id, seller_token)
        {
          "code": 0,
          "details": [
            {
              "typeUrl": "string",
              "value": "string"
            }
          ],
          "message": "string"
        }

    """
    url = "https://api-seller.ozon.ru/v2/product/list"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {
        "filter": {
            "visibility": "ALL",
        },
        "last_id": last_id,
        "limit": 1000,
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    response_object = response.json()
    return response_object.get("result")


def get_offer_ids(client_id: str, seller_token: str) -> list:
    """Получить артикулы товаров магазина Ozon

    Собирает артикулы всех товаров продавца, используя
    запросы к API и пагинацию.

    Args:
        client_id (str): Идентификатор клиента Ozon
        seller_token (str): API-ключ Ozon Seller

    Returns:
        list: Перечень артикулов товаров с Ozon

    Examples:
        >>> get_offer_ids(client_id, seller_token)
        ['1234567', '1234568', '1234570']
    """
    last_id = ""
    product_list = []
    while True:
        some_prod = get_product_list(last_id, client_id, seller_token)
        product_list.extend(some_prod.get("items"))
        total = some_prod.get("total")
        last_id = some_prod.get("last_id")
        if total == len(product_list):
            break
    offer_ids = []
    for product in product_list:
        offer_ids.append(product.get("offer_id"))
    return offer_ids


def update_price(prices: list, client_id, seller_token):
    """Обновить цены товаров"""
    url = "https://api-seller.ozon.ru/v1/product/import/prices"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {"prices": prices}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def update_stocks(stocks: list, client_id: str, seller_token: str) -> dict:
    """Обновить кол-во товаров в наличии на Ozon

    Args:
        stocks (list): Список словарей с артикулами и кол-вом товаров в наличии
        client_id (str): Идентификатор клиента Ozon
        seller_token (str): API-ключ Ozon Seller

    Returns:
        dict: Ответ API Ozon в виде json-структуры

    Raises:
        HTTPError: Если в ответ на запрос не пришёл код 200

    Examples:
        >>> update_stocks(stocks, client_id, seller_token)
        {
          "result": [
            {
              "product_id": 55946,
              "offer_id": "PG-2404С1",
              "updated": true,
              "errors": []
            }
          ]
        }

        >>> update_stocks(stocks, client_id, seller_token)
        {
          "code": 0,
          "details": [
            {
              "typeUrl": "string",
              "value": "string"
            }
          ],
          "message": "string"
        }

    """
    url = "https://api-seller.ozon.ru/v1/product/import/stocks"
    headers = {
        "Client-Id": client_id,
        "Api-Key": seller_token,
    }
    payload = {"stocks": stocks}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def download_stock() -> list[dict]:
    """Скачать файл `ostatki` с сайта casio

    Returns:
        list[dict]: Список карточек товаров

    Examples:
        >>> download_stock()
        [
          {
            "Код": 48852,
            "Наименование товара": "B 4204 LSSF",
            "Изображение": "Показать",
            "Цена": "24'570.00 руб.",
            "Количество": 2,
            "Заказ": ""
          }
        ]

    """
    # Скачать остатки с сайта
    casio_url = "https://timeworld.ru/upload/files/ostatki.zip"
    session = requests.Session()
    response = session.get(casio_url)
    response.raise_for_status()
    with response, zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        archive.extractall(".")
    # Создаем список остатков часов:
    excel_file = "ostatki.xls"
    watch_remnants = pd.read_excel(
        io=excel_file,
        na_values=None,
        keep_default_na=False,
        header=17,
    ).to_dict(orient="records")
    os.remove("./ostatki.xls")  # Удалить файл
    return watch_remnants


def create_stocks(watch_remnants: list[dict], offer_ids: list) -> list[dict]:
    """Создать список товаров с количеством в наличии.

    Args:
        watch_remnants (list[dict]): Список карточек товаров
        offer_ids (list): Перечень артикулов товаров с Ozon

    Returns:
        list: Список словарей с артикулами и кол-вом товаров в наличии

    Examples:
        >>> create_stocks(watch_remnants, offer_ids)
        [{"offer_id": "1234567", "stock": 10}]

    """
    # Уберем то, что не загружено в seller
    stocks = []
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            count = str(watch.get("Количество"))
            if count == ">10":
                stock = 100
            elif count == "1":
                stock = 0
            else:
                stock = int(watch.get("Количество"))
            stocks.append({"offer_id": str(watch.get("Код")), "stock": stock})
            offer_ids.remove(str(watch.get("Код")))
    # Добавим недостающее из загруженного:
    for offer_id in offer_ids:
        stocks.append({"offer_id": offer_id, "stock": 0})
    return stocks


def create_prices(watch_remnants: list[dict], offer_ids: list) -> list[dict]:
    """Получить цены на товары по артикулу.

    Создает список словарей с информацией о стоимости часов
    для каждого из артикулов, извлекая данные о цене
    из списка остатков товара на складе.

    Args:
        watch_remnants (list[dict]): Список товаров
        offer_ids (list): Перечень артикулов товаров с Ozon

    Returns:
        str[dict]: Список товаров с информацией о стоимости

    Examples:

        >>> create_prices(watch_remnants, offer_ids)
        [{"auto_action_enabled": "UNKNOWN",
        "currency_code": "RUB",
        "offer_id": "1234567",
        "old_price": "0",
        "price": "1990"}]

    """
    prices = []
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            price = {
                "auto_action_enabled": "UNKNOWN",
                "currency_code": "RUB",
                "offer_id": str(watch.get("Код")),
                "old_price": "0",
                "price": price_conversion(watch.get("Цена")),
            }
            prices.append(price)
    return prices


def price_conversion(price: str) -> str:
    """Преобразовать цену, исключив лишние символы.

    Args:
        price (str): Цена в исходном формате

    Returns:
        str: Цена, очищенная от символов

    Examples:
        >>> price_conversion(r"5'990.00 руб.")
        '5990'

    """
    return re.sub("[^0-9]", "", price.split(".")[0])


def divide(lst: list, n: int) -> list:
    """Разделить список lst на части по n элементов

    Args:
        lst (list): Список для разделения
        n (int): Количество элементов в каждой части

    Returns:
        list: Одна из частей в виде списка

    Examples:
        tuple(divide([1, 2, 3, 4], 2))
        ([1, 2], [3, 4])
    """
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


async def upload_prices(watch_remnants, client_id, seller_token):
    offer_ids = get_offer_ids(client_id, seller_token)
    prices = create_prices(watch_remnants, offer_ids)
    for some_price in list(divide(prices, 1000)):
        update_price(some_price, client_id, seller_token)
    return prices


async def upload_stocks(watch_remnants, client_id, seller_token):
    offer_ids = get_offer_ids(client_id, seller_token)
    stocks = create_stocks(watch_remnants, offer_ids)
    for some_stock in list(divide(stocks, 100)):
        update_stocks(some_stock, client_id, seller_token)
    not_empty = list(filter(lambda stock: (stock.get("stock") != 0), stocks))
    return not_empty, stocks


def main():
    env = Env()
    seller_token = env.str("SELLER_TOKEN")
    client_id = env.str("CLIENT_ID")
    try:
        offer_ids = get_offer_ids(client_id, seller_token)
        watch_remnants = download_stock()
        # Обновить остатки
        stocks = create_stocks(watch_remnants, offer_ids)
        for some_stock in list(divide(stocks, 100)):
            update_stocks(some_stock, client_id, seller_token)
        # Поменять цены
        prices = create_prices(watch_remnants, offer_ids)
        for some_price in list(divide(prices, 900)):
            update_price(some_price, client_id, seller_token)
    except requests.exceptions.ReadTimeout:
        print("Превышено время ожидания...")
    except requests.exceptions.ConnectionError as error:
        print(error, "Ошибка соединения")
    except Exception as error:
        print(error, "ERROR_2")


if __name__ == "__main__":
    main()
