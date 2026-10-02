# FindMeApartment — Frontend

React + TypeScript + Tailwind CSS single-page application for the FindMeApartment DRF backend
(Django 6.1 + Gunicorn + Nginx + MySQL 8.4, fully containerized with Docker). The visual style follows
Booking.com: a deep navy navigation bar, vivid blue calls to action, and clean white and gray surfaces.

## Getting Started

```bash
npm ci               # installs the exact versions pinned in package-lock.json
npm run dev          # http://localhost:5173 — proxies /api, /admin, /media and /static to :8000
npm run typecheck    # TypeScript type checking (kept separate from the build)
npm run build        # production build into dist/
```

In Docker, the frontend is built by `frontend/Dockerfile` (a Node build stage followed by
`nginx:alpine`) and served by the `frontend` container. The root `nginx.conf` forwards only
`^/(api|admin)/` to Django; every other route is handled by this SPA. `.dockerignore` keeps
`node_modules` and `dist` out of the build context.

> When changing dependencies, use `npm install <package>` / `npm uninstall <package>` and commit the
> updated `package-lock.json` — `npm ci` in Docker and CI fails if the lockfile is out of sync.

## API Routing

The whole backend is mounted under `/api/`. In `lib/apiClient.ts`, `baseURL = '/api'` (or
`${VITE_API_BASE_URL}/api` when the API lives on a different domain), and paths in `api/*.ts` are
written without the prefix: `apiClient.get('/listings/')` → `GET /api/listings/`. This also keeps the
SPA route `/listings/:id` and the API route `/api/listings/<uuid>/` from colliding.

## Project Structure

```
src/
  types/       — TypeScript types mirroring the DRF serializers (choices.ts, models.ts)
  lib/         — Axios client with JWT refresh, parser for drf-standardized-errors responses
  api/         — one module per Django app (auth, users, listings, photos, bookings, reviews)
  context/     — AuthContext: current user, real role, login/logout/becomeLandlord/deleteAccount
  components/  — UI primitives, catalog, booking widget, profile, landlord dashboard
  pages/       — Home, PropertyDetail, Profile, Dashboard, Login, Register
```

## Key Decisions Tied to the Backend

- **Landlord role** is detected by calling `GET /api/bookings/analytics/` (protected by `IsLandLord`):
  `200` means landlord, `403` means tenant. The user serializer does not expose groups, and guessing
  the role from the number of listings fails for a landlord without listings on a new device.
- **Becoming a landlord** goes through `BecomeLandlordButton`, which requires explicit confirmation that
  booking stays will no longer be possible (the Tenant group is removed). Tokens stay the same: groups
  are not part of the JWT claims.
- **Booking** is blocked in the UI for landlords, for the listing owner and for hidden listings.
- **Landlords see their own trips and guests' bookings** in a single list
  (`Q(listing__user) | Q(user)`), so the profile shows only bookings where `booking.user === me`, and
  the dashboard shows the rest.
- **Approval** is available until the arrival date inclusive — same-day bookings can be confirmed.
  Requests whose arrival date has passed are shown as expired; the nightly backend job cancels them.
- **Check-in** is available from `date_from` inclusive until `date_to` exclusive.
- **Hidden address**: until a booking is confirmed, `street` arrives as
  `"Hidden until booking confirmation"` and the numbers as `"X"`; the property page explains when the
  exact address becomes visible.
- **Errors**: `attr: "__all__"` (string errors from `Model.clean()`), `"non_field_errors"` and
  `"detail"` are treated as general form errors; `parseApiError()` returns `generalMessage` separately
  from field errors so that general messages are never lost.
- **Reviews**: an existing review is looked up via `GET /api/reviews/?booking=<id>`. Editing (`PATCH`) is
  restricted to administrators, so the author deletes the review and writes a new one — the backend
  restores the archived record with the new content.
- **Photos**: the catalog and the property page use the nested `listing.photos`; the dashboard
  additionally filters `/api/photos/` by `is_deleted` on the client.
- **Password change** goes only through `POST /api/users/me/` with `old_password` and `refresh`; the
  profile `PATCH` (`ProfileUpdateSerializer`) accepts neither the password nor the email.

## Quick Filters on the Home Page

Ten presets below the search bar are built from `ListingFilter` fields and verified against the
`create_initial_listings` seed data. Guest capacity uses the `guests` parameter ("at least N guests"),
and `min_price`/`max_price` filter by the discounted price.

# FindMeApartment — Frontend

React + TypeScript + Tailwind CSS фронтенд для DRF-бэкенда FindMeApartment (Django 6.1 + Gunicorn +
Nginx + MySQL 8.4, всё в Docker). Тема оформления —
в стиле Booking.com: тёмно-синяя навигация, яркий синий CTA, белые и серые поверхности.

## Запуск

```bash
npm ci               # Устанавливает точные версии закрепленные в package-lock.json
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