# qrmenu-desktop

QR Menu Builder Desktop App

## Backend

The desktop client reads `QRMENU_API_BASE_URL` and defaults to:

```text
http://localhost:3005/api/v1
```

Currently wired backend features:

- Business register: `POST /business/auth/register`
- Business login: `POST /business/auth/login`
- Business edit: `PUT /business/auth/edit`
- Category CRUD: `/business/categories`
