# Macaque
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/70c7df3034b14a38921807023cf13e55)](https://www.codacy.com/app/bashkirtsevich/macaque?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bashkirtsevich/macaque&amp;utm_campaign=Badge_Grade)

Macaque -- сервер комментариев, выполняет задачи хранения комментариев к произвольным сущностям, а так же ведение истории изменений комментариев.

Сервис предоставляет возможность задать комментарий на какую-либо сущность, которая задается парой «тип» и «токен»; так же сервис предоставляет возможность отвечать на комментарии.

## Описание

Сервис представляет собой RESTfull веб-сервер.
Сервисные данные хранятся в реляционной БД (PostgreSQL, MySQL, и т.д.).
Для взаимодействия с БД используется кроссплатформенная, универсальная библиотека `SQLlchemy`, преимущество данной библиотеки в том, что составление запросов осуществляется в виде ORM-модели, не зависящей от нотаций БД, библиотека берет на себя обязательства по переводу ORM в SQL-запрос в соответствующей выбранной БД нотации.

## Схема БД

При проектировании были выделены следующие сущности:
* entity_type -- унифицированный справочник типов сущностей
* entity -- справочник всех комментируемых сущностей в системе
* user -- унифицированный справочник всех пользователей, которые когда-либо что-то комментировали (сущность/комментарий)
* comment -- таблица, определяющая какой пользователь и под чем оставил свой комментарий
* comment_text -- таблица с данными комментариев конкретного пользователя, в таблице хранится история создания и изменения комментариев (когда был создан, когда изменен и что было изменено)

### `entity_type`
* `id` -- идентификатор записи
* `name` -- наименование типа (строка)

### `entity`
* `id` -- идентификатор записи
* `type` -- ключ таблицы `entity_type`
* `token` -- уникальное строковое значение идентифицирующее сущность

### `user`
* `id` -- идентификатор записи
* `token` -- уникальное строковое значение идентифицирующее комментатора

### `comment`
* `id` -- идентификатор записи
* `entity` -- ключ таблицы `entity`
* `user` -- ключ таблицы `user`
* `comment` -- ключ таблицы `comment`, определяющий что это ответ под сущностью, или под чужим комментарием
* `key` -- уникальное строковое значение идентифицирующее комментарий (GUID)

### `comment_text`
* `id` -- идентификатор записи
* `comment` -- ключ таблицы `comment`
* `timestamp` -- временная отметка занесения комментария в систему
* `hash` -- хеш комментария, для предотвращения дублирования записей, при изменении комментария, когда измененный текст совпадает со старым
* `data` -- сам текст комментария

## Преимущества и недостатки
### Преимущества

К преимуществам можно отнести тот факт, что данные в БД представлены в достаточно нормализованном виде, что предотвращает повтор данных в БД, а так же обеспечивает удобство аналитики, удаление из системы непотребных данных.

Индексация полей таблиц, по которым происходит выборка, обеспечивает высокую скорость доступа к данным (за логарифмическое время).

Доступ к методам сервиса реализован через протокол `HTTP`, передача данных в формате `JSON`, тем самым запросы и ответы человекочитаемы.

Сервис работает в асинхронном резиме, в один поток, обеспечивает высокую пропускную способность. Нет необходимости в синхронизации потоков.

Можно запускать в `Docker`.

### Недостатки

К недостаткам можно отнести сложность составления запросов к БД, как в ORM модели, так и SQL из-за нормализации БД.

Неудобное и сложное в использовании средство ревизий БД -- `Alembic`.

## Методы
* `/api/reply/{type}/{entity}`

POST. Позволяет прокомментировать сущность, определяемую параметрами `{type}, {entity}`.

Дополнительно передаются JSON данные: `user_token` -- уникальный токен пользователя, `text` -- текст комментария.

* `/api/reply/{comment_token}`

POST. Позволяет ответить на существующий комментарий, определяемый параметром `{comment_token}`.

Дополнительно передаются JSON данные: `user_token` -- уникальный токен пользователя, `text` -- текст комментария.

* `/api/edit/{comment_token}/{user_token}`

POST. Позволяет отредактировать существующий комментарий, определяемый параметрами `{comment_token}, {user_token}`.

Дополнительно передаются JSON данные: `text` -- текст комментария.

* `/api/remove/{comment_token}`

POST. Позволяет удалить существующий комментарий, определяемый параметром `{comment_token}`.

Дополнительно передаются JSON данные: `user_token` -- уникальный токен пользователя.

* `/api/comments/{type}/{entity}`

GET. Позволяет получить перечень комментариев первого уровня сущности, определяемой параметрами `{type}, {entity}`.

Результат выдается в формате JSON.

* `/api/comments/{type}/{entity}/{limit}`

GET. Позволяет получить перечень комментариев первого уровня сущности, определяемой параметрами `{type}, {entity}`.

Параметр `{limit}` предоставляет возможность пагинации. Значение по умолчанию «1000».

Результат выдается в формате JSON.

* `/api/comments/{type}/{entity}/{offset}/{limit}`

GET. Позволяет получить перечень комментариев первого уровня сущности, определяемой параметрами `{type}, {entity}`.

Параметр `{offset}` предоставляет возможность пагинации. Значение по умолчанию «0».

Параметр `{limit}` предоставляет возможность пагинации. Значение по умолчанию «1000».

Результат выдается в формате JSON.

* `/api/comments/{user_token}`

GET. Позволяет получить перечень комментариев пользователя, определяемогр параметром `{user_token}`.

Результат выдается в формате JSON.

* `/api/replies/{comment_token}`

GET. Позволяет получить перечень ответов на комментарий пользователя, определяемогр параметром `{comment_token}`.

Результат выдается в формате JSON.

* `/api/replies/{type}/{entity}`

GET. Позволяет получить весь перечень комментариев оставленных под сущностью, в т.ч. комментарии на комментарии. Выборка определяется набором параметров `{type}, {entity}`.

Результат выдается в формате JSON.

* `/api/user/download/{user_token}`

GET. Позволяет скачать все комментарии пользователя, определяемого параметром `{user_token}`.

Результат выдается в виде XML файла.

* `/api/user/download/{user_token}/{timestamp_from}`

GET. Позволяет скачать все комментарии пользователя, определяемого параметром `{user_token}` оставленные с временной отметки, заданной параметром `{timestamp_from}`.

Результат выдается в виде XML файла.

* `/api/user/download/{user_token}/{timestamp_from}/{timestamp_to}`

GET. Позволяет скачать все комментарии пользователя, определяемого параметром `{user_token}` оставленные в период, заданный параметрами `{timestamp_from}, {timestamp_to}`.

Результат выдается в виде XML файла.

* `/api/download/{type}/{entity}`

GET. Позволяет скачать все комментарии сущности, заданной параметрамм `{type}, {entity}`.

Результат выдается в виде XML файла.

* `/api/download/{type}/{entity}/{timestamp_from}`

GET. Позволяет скачать все комментарии сущности, заданной параметрамм `{type}, {entity}` оставленные с временной отметки, заданной параметром `{timestamp_from}`.

Результат выдается в виде XML файла.

* `/api/download/{type}/{entity}/{timestamp_from}/{timestamp_to}`

GET. Позволяет скачать все комментарии сущности, заданной параметрамм `{type}, {entity}` оставленные в период, заданный параметрами `{timestamp_from}, {timestamp_to}`.

Результат выдается в виде XML файла.

## Разворачивание и запуск
### Разворачивание

В этой реализации зависимости настроены на работу с PostgreSQL (для использования прочих БД, в системе должны быть установлены соответствующие библиотеки драйверов для БД, например `pip install mysqlclient`).
```
pip install -r requirements.txt
```

Перед запуском необходимо создать соответствующуюю БД и развернуть схему. Для создание БД и схемы может быть использован скрипт `deployer.py`, запускаемый с параметром, представляющий собой строку подключения к БД под системным пользователем.
```
python deployer.py postgresql://rootuser:password@postgresql:port/databasse_name
```

### Запуск

Запуск сервиса осуществляется заданием переменной окружения `DATABASE_URL` и запуском скрипта `app.py`
```
export DATABASE_URL postgresql://capuchin:password@postgresql:port/monkey
python app.py
```

### Тесты

```
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=test -e POSTGRES_USER=test --name postgresql postgres
python deployer.py postgresql://test:test@192.168.0.38/test
export DATABASE_URL=postgresql://test:test@192.168.0.38/test
python test.py
```

Сервис открывает tcp-порт `8080` и готов к работе.