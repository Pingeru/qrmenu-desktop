# qrmenu-desktop

QR Menu Builder Desktop App

## Backend

The desktop client reads `QRMENU_API_BASE_URL` and defaults to:

```text
https://qrmenu.dovanay.com/api/v1
```

The login and register screens also include a `Backend API URL` field. Use the API base URL there,
not the QR menu URL. The QR base URL is the customer-facing menu URL for the business profile.

Currently wired backend features:

- Business register: `POST /business/auth/register`
- Business login: `POST /business/auth/login`
- Business token refresh: `POST /business/auth/refresh`
- Business edit: `PUT /business/auth/edit`
- Business delete: `DELETE /business/auth/delete`
- Category CRUD: `/business/categories`
- Product create/update/delete/get/list-by-category: `/business/products`

The backend currently returns all categories from `GET /business/categories`, so the desktop app
filters category and product screens to the logged-in business before showing editable rows.

The backend also exposes `/client/auth` routes, but this desktop app is the business/admin client
and does not currently have client-user auth screens.

The current `pingeru/qrmenu-api` repo does not expose order or analytics routes. Those desktop
tabs intentionally stay empty/read-only until matching backend endpoints exist.
