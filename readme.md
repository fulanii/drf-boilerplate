# 🚀 drf-boilerplate 

This is a production-ready template for a Django REST Framework apps with a different frontend like react etc, featuring a custom user model where users can sign up, login, verify email and reset password. Authentication using JWT authentication via `djangorestframework-simplejwt`, auto generated docs with `drf_spectacular` email code verifictions using resend and separated configuration for local development and production deployment.


### Tech Stack
- `django djangorestframework`
- `djangorestframework-simplejwt`
- `drf_spectacular`
- `resend`
- `pytest pytest-django`


### Core Features

| Feature | Details | Key Libraries |
| :--- | :---: | ---: |
| Custom User Authentication | Allows users to sign up, log in, verify email, and reset passwords using a flexible email and username-based custom user model. | `AbstractUser` |
| Secure Token Access (JWT) | Authentication is handled via stateless JSON Web Tokens (JWT), providing secure access and refresh tokens. | `djangorestframework-simplejwt` |
| API Documentation | Automatic, interactive API documentation (Swagger/Redoc) that is generated directly from your code. | `drf-spectacular`
| Environments | Clean separation of configuration for development, and production using environment variables. | `django-environ`
| Email | Email verification and password reset | `resend`


### API Capabilities

User Model
The custom user model is based on AbstractUser and requires:
- email (used for login and primary identity)
- username (optional login method)
- password (securely hashed)

| Flow | Required Field | Success Outcome
| :--- | :---:  | ---:
| Registration | `email`, `username`, `password` | User account created and immediately verification email sent.|
| Login | Either `email` or `username`, plus `password`. | Successful login returns user data, an Access Token, and a Refresh Token. |
| Email Code | `email` | Using user email to confirm their identity and set is_verified = True. |
| Resend Email Verification Code | `email` | Using user email to generate new verification code and set it to user email. |
| Password Reset Request| `email` | User receives an email with a unique code to set a new password. |
| Password Reset | `email` `code` `new password` | User reset password with code and new password. |



### Setup & Customization Guide

Before starting, clone the repository and navigate into the root directory.

1. Project Renaming (Crucial Step)
The internal configuration package is likely named config. To personalize your project, rename this directory and update all references.
    - Rename the main configuration folder (e.g., mv config my_project_name).
    - Globally Search and Replace the old package name (e.g., config) with your new name across all files (especially manage.py, wsgi.py, and any app imports).

2. Environment Variables (.env)
    - Create a `.env` file in the root directory based on the provided [.env.example](./.env.example) This file stores all secrets and environment-specific variables.
    - Update database info
    - Add your `RESEND_API_KEY` `FROM_NAME` and `FROM_EMAIL` in `.env` for sending verification codes user email 

3. Generate New Secret Keys
    - Never use the default keys. Run the commands below in a Django shell and copy the output directly into your .env file.
```bash
   python manage.py shell
   >>> from django.core.management.utils import get_random_secret_key
   >>> print(get_random_secret_key()) # (Copy this output into your .env SECRET_KEY)
```

1. Adjust Settings Modules
    - Your settings are split across modules. You primarily interact with environment variables, but can adjust framework settings here:

   | File |Customization Focus |
   | :--- | ---:  | 
   | `config/settings/base.py `| Update SPECTACULAR_SETTINGS and SIMPLE_JWT to match your application's requirements. | 
   | `config/settings/development.py` | Use this for local-only tools. | 
   | `config/settings/production.py` | Review security settings (SECURE_SSL_REDIRECT, CORS etc.) before deployment.. | 

2. Running the Application
    - To ensure you use the correct configuration:

   | Environment | `.env` |
   | :---: | :---:  | 
   | development | `DJANGO_SETTINGS_MODULE=config.settings.development` |
   | production | `DJANGO_SETTINGS_MODULE=config.settings.production` |


### Project Structure
```
├── authentication
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── __init__.py
│   ├── models.py
│   ├── serializer.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── config
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── .env.example
├── manage.py
├── readme.md
└── requirements.txt
```


### Setup and Installation
```bash
python -m venv venv
source venv/bin/activate
git clone https://github.com/fulanii/drf-boilerplate/
cd drf-boilerplate
pip install -r requirements.txt
python manage.py makemigrations 
python manage.py migrate
git remote set-url github.com/you-username/your-repo 
```

### Contribute and Support 

We welcome contributions and feedback! If you find a bug, have a suggestion for an improvement, or want to add a new feature:

1.  **Open an Issue** to discuss the bug or feature idea.
2.  **Fork the repository** and submit a **Pull Request** (PR) with your changes.

If this boilerplate saved you time, consider giving the repository a star ⭐!