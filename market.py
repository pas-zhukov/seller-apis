import datetime
import logging.config
from environs import Env
from seller import download_stock

import requests

from seller import divide, price_conversion

logger = logging.getLogger(__file__)


def get_product_list(page: str, campaign_id: str, access_token: str) -> dict:
    """Получить список товаров в Яндекс.Маркет.

    Args:
        page (str): Идентификатор (номер) страницы
        campaign_id (str): Идентификатор кампании и идентификатор магазина Яндекс.Маркет
        access_token (str): API-ключ продавца Яндекс.Маркет

    Returns:
        dict: Ответ API ЯМ со списком карточек товаров

    Raises:
        HTTPError: Если в ответ на запрос не пришёл код 200

    Examples:
        >>> get_product_list("", campaign_id, access_token)
        {
          "paging": {
            "nextPageToken": "string",
            "prevPageToken": "string"
          },
          "offers": [
            {
              "offerId": "string",
              "quantum": {
                "minQuantity": 0,
                "stepQuantity": 0
              },
              "available": false,
              "basicPrice": {
                "value": 0,
                "currencyId": "RUR",
                "discountBase": 0,
                "updatedAt": "2022-12-29T18:02:01Z"
              },
              "campaignPrice": {
                "value": 0,
                "discountBase": 0,
                "currencyId": "RUR",
                "vat": 0,
                "updatedAt": "2022-12-29T18:02:01Z"
              },
              "status": "PUBLISHED",
              "errors": [
                {
                  "message": "string",
                  "comment": "string"
                }
              ],
              "warnings": [
                {
                  "message": "string",
                  "comment": "string"
                }
              ]
            }
          ]
        }

        >>> get_product_list("", campaign_id, access_token)
        {
            "status": "OK",
            "errors": [
                {
                    "code": "string",
                    "message": "string"
                }
            ]
        }

    """
    endpoint_url = "https://api.partner.market.yandex.ru/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Host": "api.partner.market.yandex.ru",
    }
    payload = {
        "page_token": page,
        "limit": 200,
    }
    url = endpoint_url + f"campaigns/{campaign_id}/offer-mapping-entries"
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    response_object = response.json()
    return response_object.get("result")


def update_stocks(stocks: list[dict], campaign_id: str, access_token: str) -> dict:
    """Обновить кол-во товаров в наличии на Яндекс.Маркет.

    Args:
        stocks (list[dict]): Список словарей с артикулами и кол-вом товаров в наличии
        campaign_id (str): Идентификатор кампании и идентификатор магазина Яндекс.Маркет
        access_token (str): API-ключ продавца Яндекс.Маркет

    Returns:
        dict: Ответ API Яндекс.Маркет в виде json-структуры

    Raises:
        HTTPError: Если в ответ на запрос не пришёл код 200

    Examples:
        >>> update_stocks(stocks, campaign_id, access_token)
        {
            "status": "OK"
        }

        >>> update_stocks(stocks, campaign_id, access_token)
        {
            "status": "OK",
            "errors": [
                {
                    "code": "string",
                    "message": "string"
                }
            ]
        }

    """
    endpoint_url = "https://api.partner.market.yandex.ru/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Host": "api.partner.market.yandex.ru",
    }
    payload = {"skus": stocks}
    url = endpoint_url + f"campaigns/{campaign_id}/offers/stocks"
    response = requests.put(url, headers=headers, json=payload)
    response.raise_for_status()
    response_object = response.json()
    return response_object


def update_price(prices: list[dict], campaign_id: str, access_token: str) -> dict:
    """Обновить цены товаров на Яндекс.Маркет.

    Args:
        prices (list): Список товаров с информацией о стоимости
        campaign_id (str): Идентификатор кампании и идентификатор магазина Яндекс.Маркет
        access_token (str): API-ключ продавца Яндекс.Маркет

    Returns:
        dict: Ответ API Яндекс.Маркет в виде json-структуры

    Raises:
        HTTPError: Если в ответ на запрос не пришёл код 200

    Examples:
        >>> update_price(prices, campaign_id, access_token)
        {
            "status": "OK"
        }

        >>> update_price(prices, campaign_id, access_token)
        {
            "status": "OK",
            "errors": [
                {
                    "code": "string",
                    "message": "string"
                }
            ]
        }

    """
    endpoint_url = "https://api.partner.market.yandex.ru/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Host": "api.partner.market.yandex.ru",
    }
    payload = {"offers": prices}
    url = endpoint_url + f"campaigns/{campaign_id}/offer-prices/updates"
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    response_object = response.json()
    return response_object


def get_offer_ids(campaign_id: str, market_token: str) -> list[str]:
    """Получить артикулы товаров Яндекс маркета.

    Args:
        campaign_id (str): Идентификатор кампании и идентификатор магазина Яндекс.Маркет
        market_token (str): API-ключ продавца Яндекс.Маркет

    Returns:
        list: Список с артикулами товаров на Яндекс.Маркет

    Examples:
        >>> get_offer_ids(campaign_id, market_token)
        ['123456', '123457']

    """
    page = ""
    product_list = []
    while True:
        some_prod = get_product_list(page, campaign_id, market_token)
        product_list.extend(some_prod.get("offerMappingEntries"))
        page = some_prod.get("paging").get("nextPageToken")
        if not page:
            break
    offer_ids = []
    for product in product_list:
        offer_ids.append(product.get("offer").get("shopSku"))
    return offer_ids


def create_stocks(watch_remnants: list[dict], offer_ids: list, warehouse_id: str) -> list[dict]:
    """Создать список товаров с количеством в наличии.

    Args:
        watch_remnants (list[dict]): Список карточек товаров
        offer_ids (list): Список с артикулами товаров на Яндекс.Маркет
        warehouse_id (str): ID склада

    Returns:
        list: Список словарей с артикулами и кол-вом товаров в наличии

    Examples:
        >>> create_stocks(watch_remnants, offer_ids, warehouse_id)
        [{
          "sku": 123123,
          "warehouseId": 1234567,
          "items": [
            {
              "count": 100,
              "type": "FIT",
              "updatedAt": "2008-09-22T14:01:54.9571247Z"
            }
          ]
        }]

    """
    # Уберем то, что не загружено в market
    stocks = list()
    date = str(datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z")
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            count = str(watch.get("Количество"))
            if count == ">10":
                stock = 100
            elif count == "1":
                stock = 0
            else:
                stock = int(watch.get("Количество"))
            stocks.append(
                {
                    "sku": str(watch.get("Код")),
                    "warehouseId": warehouse_id,
                    "items": [
                        {
                            "count": stock,
                            "type": "FIT",
                            "updatedAt": date,
                        }
                    ],
                }
            )
            offer_ids.remove(str(watch.get("Код")))
    # Добавим недостающее из загруженного:
    for offer_id in offer_ids:
        stocks.append(
            {
                "sku": offer_id,
                "warehouseId": warehouse_id,
                "items": [
                    {
                        "count": 0,
                        "type": "FIT",
                        "updatedAt": date,
                    }
                ],
            }
        )
    return stocks


def create_prices(watch_remnants: list[dict], offer_ids: list) -> list[dict]:
    """Получить цены на товары по артикулу.

    Args:
        watch_remnants (list[dict]): Список карточек товаров
        offer_ids (list): Список с артикулами товаров на Яндекс.Маркет

    Returns:
        list[dict]: Список товаров с информацией о стоимости

    Examples:
        >>> create_prices(watch_remnants, offer_ids)
        [
          {
            "id": "123456",
            "price": {
              "value": 1500,
              "currencyId": "RUR"
            }
          }
        ]

    """
    prices = []
    for watch in watch_remnants:
        if str(watch.get("Код")) in offer_ids:
            price = {
                "id": str(watch.get("Код")),
                # "feed": {"id": 0},
                "price": {
                    "value": int(price_conversion(watch.get("Цена"))),
                    # "discountBase": 0,
                    "currencyId": "RUR",
                    # "vat": 0,
                },
                # "marketSku": 0,
                # "shopSku": "string",
            }
            prices.append(price)
    return prices


async def upload_prices(watch_remnants: list[dict], campaign_id: str, market_token: str) -> list[dict]:
    """Обновить цены товаров на Яндекс.Маркет.

    Args:
        watch_remnants (list[dict]): Список карточек товаров
        campaign_id (str): Идентификатор кампании и идентификатор магазина Яндекс.Маркет
        market_token (str): API-ключ продавца Яндекс.Маркет

    Returns:
        list[dict]: Список товаров с информацией о стоимости

    Examples:
        >>> create_prices(watch_remnants, campaign_id, market_token)
        [
          {
            "id": "123456",
            "price": {
              "value": 1500,
              "currencyId": "RUR"
            }
          }
        ]

    """
    offer_ids = get_offer_ids(campaign_id, market_token)
    prices = create_prices(watch_remnants, offer_ids)
    for some_prices in list(divide(prices, 500)):
        update_price(some_prices, campaign_id, market_token)
    return prices


async def upload_stocks(watch_remnants: list[dict], campaign_id: str, market_token: str, warehouse_id: str) -> tuple[list, list]:
    """Обновить данные о кол-ве товаров на Яндекс.Маркет.

    Args:
        watch_remnants (list[dict]): Список карточек товаров
        campaign_id (str): Идентификатор кампании и идентификатор магазина Яндекс.Маркет
        market_token (str): API-ключ продавца Яндекс.Маркет
        warehouse_id (str): ID склада

    Returns:
        tuple[list, list]: Список товаров, с артикулами и кол-вом, которые есть в наличии;
        список всех товаров с артикулами и кол-вом.

    Examples:
        >>> update_stocks(watch_remnants, campaign_id, market_token, warehouse_id)
        (
          [
            {
              "sku": 123123,
              "warehouseId": 1234567,
              "items": [
                {
                  "count": 100,
                  "type": "FIT",
                  "updatedAt": "2008-09-22T14:01:54.9571247Z"
                }
              ]
            }
          ],
          [
            [
              {
                "sku": 123123,
                "warehouseId": 1234567,
                "items": [
                  {
                    "count": 100,
                    "type": "FIT",
                    "updatedAt": "2008-09-22T14:01:54.9571247Z"
                  }
                ]
              }
            ],
            [
              {
                "sku": 123124,
                "warehouseId": 1234567,
                "items": [
                  {
                    "count": 0,
                    "type": "FIT",
                    "updatedAt": "2008-09-22T14:01:54.9571247Z"
                  }
                ]
              }
            ]
          ]
        )

    """
    offer_ids = get_offer_ids(campaign_id, market_token)
    stocks = create_stocks(watch_remnants, offer_ids, warehouse_id)
    for some_stock in list(divide(stocks, 2000)):
        update_stocks(some_stock, campaign_id, market_token)
    not_empty = list(
        filter(lambda stock: (stock.get("items")[0].get("count") != 0), stocks)
    )
    return not_empty, stocks


def main():
    env = Env()
    market_token = env.str("MARKET_TOKEN")
    campaign_fbs_id = env.str("FBS_ID")
    campaign_dbs_id = env.str("DBS_ID")
    warehouse_fbs_id = env.str("WAREHOUSE_FBS_ID")
    warehouse_dbs_id = env.str("WAREHOUSE_DBS_ID")

    watch_remnants = download_stock()
    try:
        # FBS
        offer_ids = get_offer_ids(campaign_fbs_id, market_token)
        # Обновить остатки FBS
        stocks = create_stocks(watch_remnants, offer_ids, warehouse_fbs_id)
        for some_stock in list(divide(stocks, 2000)):
            update_stocks(some_stock, campaign_fbs_id, market_token)
        # Поменять цены FBS
        upload_prices(watch_remnants, campaign_fbs_id, market_token)

        # DBS
        offer_ids = get_offer_ids(campaign_dbs_id, market_token)
        # Обновить остатки DBS
        stocks = create_stocks(watch_remnants, offer_ids, warehouse_dbs_id)
        for some_stock in list(divide(stocks, 2000)):
            update_stocks(some_stock, campaign_dbs_id, market_token)
        # Поменять цены DBS
        upload_prices(watch_remnants, campaign_dbs_id, market_token)
    except requests.exceptions.ReadTimeout:
        print("Превышено время ожидания...")
    except requests.exceptions.ConnectionError as error:
        print(error, "Ошибка соединения")
    except Exception as error:
        print(error, "ERROR_2")


if __name__ == "__main__":
    main()
