# *README: Інструкція для розробника*

*Цей документ містить покрокову інструкцію для розробника, який хоче приєднатися до проекту. Передбачено, що у вас свіже встановлена операційна система і немає необхідного програмного забезпечення.*

## *1. Необхідні залежності та програмне забезпечення*

*Перед початком роботи необхідно встановити:*

- ***Python**** (рекомендована версія 3.10 або новіша)*
- ***Git**** (для клонування репозиторію)*
- ***Virtualenv**** (віртуальне середовище Python)*
- ***MongoDB Atlas**** (онлайн база даних MongoDB)*

## *2. Клонування репозиторію*

```bash
git clone https://github.com/dimact22/TaskManagerBE.git
cd your-repo
```

## *3. Налаштування середовища розробки*

*Створіть та активуйте віртуальне середовище **`venv`**:*

```bash
python -m venv venv
```

### ***Для Windows:***

```bash
venv\Scripts\activate
```

### ***Для macOS/Linux:***

```bash
source venv/bin/activate
```

## 4. Конфігурація підключення до бази даних

Проект використовує **MongoDB Atlas** для зберігання даних. Щоб підключитися, потрібно:
1. Створити обліковий запис у [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Створити новий кластер
3. Отримати рядок підключення у форматі:
   ```sh
   mongodb+srv://<username>:<password>@cluster0.mongodb.net/<dbname>?retryWrites=true&w=majority
   ```
4. Створити файл `.env` у кореневій папці проекту та додати туди змінні середовища:
   ```ini
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/<dbname>?retryWrites=true&w=majority
   ```

---

## *5. Встановлення та конфігурація залежностей*

*Встановіть необхідні пакети з **`requirements.txt`**:*

```bash
pip install -r requirements.txt
```

## 6. Налаштування змінних середовища

Створіть `.env` файл у кореневій директорії та додайте наступні змінні:

```
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/<dbname>?retryWrites=true&w=majority
SECRET_KEY=your_secret_key
```

Замініть `<username>`, `<password>` і `<dbname>` на ваші дані з MongoDB Atlas.

## 7. Запуск проекту у режимі розробки

```sh
poetry run uvicorn main:app --reload
```

Сервер буде доступний за адресою: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 8. Базові команди та операції

### Оновлення залежностей
```sh
pip update
```

### Запуск тестів
```sh
pytest
```

### Форматування коду
```sh
black .
```

## 9. Доступ до Swagger UI

Після запуску API ви можете переглянути документацію за адресою:

```
http://127.0.0.1:8000/docs
```

або у форматі OpenAPI:

```
http://127.0.0.1:8000/openapi.json
```

## 10. Завершення роботи

Щоб вимкнути віртуальне середовище:

```bash
deactivate
```

---

# Документування коду в цьому проєкті

## Загальні правила
1. Використовуйте **Google Style docstrings** для функцій та класів.
2. Для FastAPI-ендпоінтів додавайте **summary** та **description**.
3. Використовуйте **типізацію** (`int`, `str`, `list`, `dict`, тощо).
4. Для опису моделей використовуйте **Pydantic**.

## Приклади

### Документування функції:
```python
def example_function(param: str) -> str:
    """
    Пояснення, що робить ця функція.

    Args:
        param (str): Вхідний параметр.

    Returns:
        str: Результат роботи функції.
    """
    return f"Hello, {param}"
