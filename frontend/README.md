# FindMeApartment — Frontend

React + TypeScript + Tailwind CSS фронтенд для DRF-бэкенда FindMeApartment (Django 6.1 + Gunicorn +
Nginx + MySQL 8, всё в Docker). Тема оформления —
в стиле Booking.com: тёмно-синяя навигация, яркий синий CTA, белые и серые поверхности.

## Запуск

```bash
npm install
npm run dev          # http://localhost:5173, проксирует /api, /admin, /media, /static на :8000
npm run typecheck    # проверка типов (отдельно от сборки)
npm run build        # production-сборка в dist/
```

В Docker фронтенд собирается `frontend/Dockerfile` (node → nginx:alpine) и отдаётся контейнером
`frontend`; корневой `nginx.conf` отправляет в Django только `^/(api|admin)/`, всё остальное — сюда.
`.dockerignore` исключает `node_modules` и `dist` из контекста сборки.

## Маршрутизация API

Весь бэкенд смонтирован под `/api/`. В `lib/apiClient.ts` `baseURL = '/api'` (или
`${VITE_API_BASE_URL}/api`, если API живёт на другом домене), а пути в `api/*.ts` пишутся без
префикса: `apiClient.get('/listings/')` → `GET /api/listings/`. SPA-роут `/listings/:id` и API-роут
`/api/listings/<uuid>/` больше не конфликтуют.

## Структура

```
src/
  types/       — TS-типы по Serializer.Meta.fields (choices.ts, models.ts)
  lib/         — axios-клиент с JWT refresh, парсер ошибок drf-standardized-errors
  api/         — по модулю на Django app (auth, users, listings, photos, bookings, reviews)
  context/     — AuthContext: пользователь, реальная роль, login/logout/becomeLandlord/deleteAccount
  components/  — UI-примитивы, каталог, бронирование, профиль, дашборд лендлорда
  pages/       — Home, PropertyDetail, Profile, Dashboard, Login, Register
```

## Ключевые решения, привязанные к бэкенду

- **Роль лендлорда** определяется запросом к `GET /api/bookings/analytics/` (защищён `IsLandLord`):
  200 — лендлорд, 403 — нет. `UserListSerializer` группы не отдаёт, а прежняя эвристика по числу
  объявлений ошибалась для лендлорда без объявлений на новом устройстве.
- **Стать арендодателем** — `BecomeLandlordButton` с обязательным подтверждением, что бронировать
  жильё после этого будет нельзя (группа Tenant снимается). Токены не меняются: группы не входят в JWT.
- **Бронирование** блокируется в UI для лендлордов, владельца объекта и скрытых объявлений.
- **Лендлорд видит и свои поездки, и брони гостей** одним списком (`Q(listing__user) | Q(user)`),
  поэтому профиль показывает только брони, где `booking.user === me`, а дашборд — остальные.
- **Заселение** доступно с `date_from` включительно до `date_to` не включительно.
- **Скрытый адрес**: пока бронь не подтверждена, `street` приходит как
  `"Hidden until booking confirmation"`, а номера — как `"X"`; страница объекта показывает пояснение.
- **Ошибки**: `attr: "__all__"` (строковые ошибки из `Model.clean()`), `"non_field_errors"` и
  `"detail"` считаются общими ошибками формы; `parseApiError()` отдаёт `generalMessage` отдельно от
  ошибок полей, чтобы общие сообщения не терялись.
- **Отзывы**: наличие отзыва проверяется через `GET /api/reviews/?booking=<id>`. Редактирование
  (`PATCH`) на бэке доступно только администратору, поэтому автор может удалить отзыв и написать
  заново — `perform_create` восстановит удалённую запись с новыми данными.
- **Фото**: в каталоге и на странице объекта берутся из вложенного `listing.photos`; в дашборде
  `/api/photos/` дополнительно фильтруется по `is_deleted` на клиенте.
- **Смена пароля** — только через `POST /api/users/me/` с `old_password` и `refresh`; `PATCH` профиля
  (`ProfileUpdateSerializer`) не принимает ни пароль, ни email.

## Быстрые фильтры на главной

10 пресетов под строкой поиска собраны из полей `ListingFilter` и проверены на сид-данных
`create_initial_listings`. Вместимость фильтруется параметром `guests` («от N гостей»), а
`min_price`/`max_price` — по цене со скидкой.

## Примечание

В среде, где собирался проект, не было доступа к npm-реестру: код проверен синтаксическим
разбором TypeScript и проверкой всех внутренних импортов, но `npm install` и `npm run typecheck`
нужно прогнать локально перед первым деплоем.
