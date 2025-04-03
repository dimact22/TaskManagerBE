# Резервне копіювання FastAPI у Production

## Резервне копіювання бази даних MongoDB

1. Для резервного копіювання MongoDB можна використовувати стандартну утиліту `mongodump`:
    ```bash
    mongodump --uri="mongodb://your-db-url" --out=/path/to/backup/directory
    ```

2. Щоб створювати резервні копії регулярно, налаштуйте cron job:
    - Відкрийте crontab:
        ```bash
        crontab -e
        ```
    - Додайте запис для регулярного резервного копіювання:
        ```bash
        0 2 * * * mongodump --uri="mongodb://your-db-url" --out=/path/to/backup/directory
        ```

## Резервне копіювання коду

1. Регулярно створюйте резервні копії коду за допомогою git:
    ```bash
    git clone https://github.com/dimact22/TaskManagerBE.git /path/to/backup/directory
    ```

2. Переконайтесь, що всі зміни в коді зберігаються в репозиторії для подальшого відновлення.

## Відновлення з резервної копії

1. Для відновлення бази даних використовуйте команду `mongorestore`:
    ```bash
    mongorestore --uri="mongodb://your-db-url" /path/to/backup/directory
    ```

2. Відновіть код з резервної копії:
    ```bash
    cp -r /path/to/backup/directory/* /path/to/your/project/
    ```

3. Перезапустіть додаток:
    ```bash
    sudo systemctl restart gunicorn
    sudo systemctl restart nginx
    ```
