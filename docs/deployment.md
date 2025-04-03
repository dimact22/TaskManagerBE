# Розгортання FastAPI у Production

## Вимоги до середовища

1. **Операційна система**: Ubuntu 22.04 / Debian 11 / CentOS 8.
2. **CPU**: Мінімум 2 ядра (рекомендовано 4).
3. **RAM**: Мінімум 4GB (рекомендовано 8GB).
4. **Диск**: Мінімум 20GB SSD (рекомендовано для великих даних 50GB).

## Необхідне програмне забезпечення

1. **Python 3.9+**: Для запуску FastAPI додатку.
2. **Nginx**: Для обробки запитів та балансування навантаження.
3. **Gunicorn**: WSGI сервер для запуску FastAPI.
4. **MongoDB**: Для зберігання даних.
5. **Redis (опційно)**: Для кешування.
6. **Certbot (опційно)**: Для налаштування SSL сертифікатів.

## Налаштування мережі

1. Переконайтесь, що порт 80 (HTTP) та 443 (HTTPS) відкриті на сервері.
2. Відкрийте порт 27017 для підключення до MongoDB, якщо ви використовуєте віддалену базу даних.

## Конфігурація серверів

1. **Nginx**: Конфігурація для проксирування запитів до Gunicorn:
    - Налаштуйте сервер для проксирування запитів на Gunicorn.
    - Додайте налаштування для автоматичного перезавантаження Nginx після кожного деплою.

    **Приклад конфігурації Nginx:**
    ```nginx
    server {
        listen 80;
        server_name example.com;
        
        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

## Налаштування СУБД (MongoDB)

1. Встановіть MongoDB на сервері або використовуйте віддалену базу даних (наприклад, MongoDB Atlas).
2. Підключіть FastAPI додаток до MongoDB, вказавши правильні креденціали та URL в конфігураційних файлах.

## Розгортання коду

1. Клонуйте репозиторій на сервер:
    ```bash
    git clone https://github.com/dimact22/TaskManagerBE.git /path/to/your/project
    ```

2. Створіть та активуйте віртуальне середовище:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Встановіть залежності:
    ```bash
    pip install -r requirements.txt
    ```

4. Запустіть Gunicorn для запуску додатку:
    ```bash
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
    ```

5. Переконайтесь, що Gunicorn працює на порту 8000.

## Перевірка працездатності

1. Перевірте, чи доступний API через браузер або curl:
    ```bash
    curl http://your-server-ip:8000
    ```

2. Якщо все працює, налаштуйте Nginx для проксирування запитів до Gunicorn.