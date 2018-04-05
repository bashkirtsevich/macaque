# Macaque
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/70c7df3034b14a38921807023cf13e55)](https://www.codacy.com/app/bashkirtsevich/macaque?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bashkirtsevich/macaque&amp;utm_campaign=Badge_Grade)

Macaque -- сервер комментариев, выполняет задачи хранения комментариев к произвольным сущностям, а так же ведение истории изменений комментариев.

Сервис предоставляет возможность задать комментарий на какую-либо сущность, которая задается парой «тип» и «токен»; так же сервис предоставляет возможность отвечать на комментарии.

## Методы
* `/api/reply/{type}/{entity}`
POST. Позволяет прокомментировать сущность, определяемую параметрами `{type}, {entity}`

Дополнительно передаются JSON данные: `user_token` -- уникальный токен пользователя, `text` -- текст комментария.

* `/api/reply/{comment_token}`
POST. Позволяет ответить на существующий комментарий, определяемый параметром `{comment_token}`

Дополнительно передаются JSON данные: `user_token` -- уникальный токен пользователя, `text` -- текст комментария.

* `/api/edit/{comment_token}/{user_token}`
POST. Позволяет отредактировать существующий комментарий, определяемый параметрами `{comment_token}, {user_token}`

Дополнительно передаются JSON данные: `text` -- текст комментария.

* `/api/remove/{comment_token}`
POST. Позволяет удалить существующий комментарий, определяемый параметром `{comment_token}`

Дополнительно передаются JSON данные: `user_token` -- уникальный токен пользователя.

* `/api/comments/{type}/{entity}`
GET. Позволяет получить перечень комментариев первого уровня сущности, определяемой параметрами `{type}, {entity}`

Результат выдается в формате JSON.

* `/api/comments/{type}/{entity}/{limit}`
GET. Позволяет получить перечень комментариев первого уровня сущности, определяемой параметрами `{type}, {entity}`

Параметр `{limit}` предоставляет возможность пагинации. Значение по умолчанию «1000»

Результат выдается в формате JSON.

* `/api/comments/{type}/{entity}/{offset}/{limit}`
GET. Позволяет получить перечень комментариев первого уровня сущности, определяемой параметрами `{type}, {entity}`

Параметр `{offset}` предоставляет возможность пагинации. Значение по умолчанию «0»

Параметр `{limit}` предоставляет возможность пагинации. Значение по умолчанию «1000»

Результат выдается в формате JSON.

* `/api/comments/{user_token}`
* `/api/replies/{comment_token}`
* `/api/replies/{type}/{entity}`
* `/api/user/download/{user_token}`
* `/api/user/download/{user_token}/{timestamp_from}`
* `/api/user/download/{user_token}/{timestamp_from}/{timestamp_to}`
* `/api/download/{type}/{entity}`
* `/api/download/{type}/{entity}/{timestamp_from}`
* `/api/download/{type}/{entity}/{timestamp_from}/{timestamp_to}`
