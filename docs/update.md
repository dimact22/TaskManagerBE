# Оновлення FastAPI у Production

## Кроки для оновлення коду

1. Підключіться до сервера через SSH:
    ```bash
    ssh user@your-server-ip
    ```

2. Перейдіть до директорії з проектом:
    ```bash
    cd /path/to/your/project
    ```

3. Витягніть останні зміни з репозиторію:
    ```bash
    git pull origin main
    ```

4. Якщо були додані нові залежності, оновіть їх:
    ```bash
    pip install -r requirements.txt
    ```

5. Якщо потрібно, зробіть міграції бази даних:
    ```bash
    alembic upgrade head
    ```

6. Перезапустіть Gunicorn:
    ```bash
    sudo systemctl restart gunicorn
    ```

7. Перезавантажте Nginx, якщо змінили конфігурацію:
    ```bash
    sudo systemctl restart nginx
    ```

## Перевірка працездатності

1. Перевірте, чи працює нова версія додатку:
    ```bash
    curl http://your-server-ip:8000
    ```

2. Переконайтесь, що всі кінцеві точки API працюють коректно.
    ```bash
    curl http://your-server-ip:8000/docs
    ```
