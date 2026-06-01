# qrmenu-desktop

QR Menu Builder Desktop App

## Backend

The desktop client reads `QRMENU_API_BASE_URL` and defaults to:

```text
https://qrmenu.dovanay.com/api/v1
```

Login and register use that configured backend URL directly. The app no longer asks for a backend
URL on the auth screens. The QR URL field is only a local preview until the backend exposes a
persisted business menu URL.

Currently wired backend features:

- Business register: `POST /business/auth/register`
- Business login: `POST /business/auth/login`
- Business token refresh: `POST /business/auth/refresh`
- Business edit: `PUT /business/auth/edit`
- Business delete: `DELETE /business/auth/delete`
- Category CRUD: `/business/categories`
- Product create/update/delete/get/list/filter: `/business/products`
- Live business orders list/update/delete with enriched customer/product fields: `/business/orders`
- Business analytics summary and rankings: `/business/analytics`

The backend currently returns all categories from `GET /business/categories`, so the desktop app
filters category and product screens to the logged-in business before showing editable rows.

The backend also exposes `/client/auth` routes, but this desktop app is the business/admin client
and does not currently have client-user auth screens.

The current `pingeru/qrmenu-api` repo exposes business analytics and filtered product listing.
The desktop app still keeps an order-based analytics fallback in case an older backend deployment
does not have `/business/analytics` yet.
