# qrmenu-desktop

QR Menu Builder Desktop App

## Backend

The desktop client reads `QRMENU_API_BASE_URL` and defaults to:

```text
https://qrmenu.dovanay.com/api/v1
```

The login and register screens also include a `Backend API URL` field. Use the API base URL there, not the QR menu URL. The QR base URL is the customer-facing menu URL for the business profile.

Currently wired backend features:

- Business register: `POST /business/auth/register`
- Business login: `POST /business/auth/login`
- Business edit: `PUT /business/auth/edit`
- Category CRUD: `/business/categories`
