# Seller Apis

Набор скриптов для работы с маркетплейсами Ozon и Яндекс.Маркет, предназначен для продавцов.

Скрипты позволяют автоматизированно обновлять информацию о наличии товаров и их ценах, опираясь на данные о товарах на складе.

## Установка зависимостей
Для работы со скриптами необходимо самостоятельно установить на компьютер [Python3.10](https://www.python.org/downloads/).

Далее устанавливаем зависимости.

Первым делом, скачайте код:
``` 
git clone https://github.com/pas-zhukov/seller-apis.git
```
Для работы скрипта понадобятся библиотеки, перечисленные в `reqirements.txt`.
Устанавливаем их командой:
```
pip install -r requirements.txt
```

## Переменные окружения

Для работы скриптов, в системе должны быть сконфигурированы некоторые переменные окружения.

Для работы с Ozon:

- `SELLER_TOKEN` - API-ключ Ozon Seller. [Как получить](https://docs.ozon.ru/api/seller/#tag/Auth)
- `CLIENT_ID` - Идентификатор клиента Ozon. [Как найти](https://sellerstats.ru/help/api_key_ozon)

Для работы с Яндекс.Маркет:

- `MARKET_TOKEN` - API-ключ продавца Яндекс.Маркет. [Как получить](https://yandex.ru/dev/market/partner-api/doc/ru/concepts/authorization)
- `FBS_ID` - Идентификатор кампании и идентификатор магазина с FBS моделью. [Как найти](https://yandex.ru/dev/market/partner-api/doc/ru/reference/campaigns/getCampaign#path-parameters). [О моделях](https://yandex.ru/support/marketplace/introduction/models.html)
- `DBS_ID` - Идентификатор кампании и идентификатор магазина с DBS моделью. [Как найти](https://yandex.ru/dev/market/partner-api/doc/ru/reference/campaigns/getCampaign#path-parameters)
- `WAREHOUSE_FBS_ID` - Идентификатор склада FBS. [Как найти](https://yandex.ru/dev/market/partner-api/doc/ru/reference/stocks/updateStocks#stockdto)
- `WAREHOUSE_DBS_ID` - Идентификатор склада DBS. [Как найти](https://yandex.ru/dev/market/partner-api/doc/ru/reference/stocks/updateStocks#stockdto)

[_Статья, где описано получение и поиск ID для Яндекс.Маркета_](https://academy.rdv-it.ru/home/samostoyatel-noe-podklyuchenie/shag-3-nastrojki-podklyucheniya-marketplejsov/nastrojka-podklyucheniya-k-marketplejsu-yandeks-market/nastrojka-podklyucheniya-k-lk-yandeks-market)

## Скрипт `seller.py`

Скрипт обновляет сведения о количестве товаров и их стоимости на Ozon, используя данные об остатках и ценах на складе, полученных с сайта timeworld.ru.

### Запуск

Запускается скрипт командой:

```shell
python seller.py
```