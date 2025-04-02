# Import the googlemaps library and dotenv to load environment variables
from pydantic import BaseModel, EmailStr, Field, validator
from fastapi import HTTPException, status
import re
from typing import Optional
from typing import List, Optional

# Model to represent a user's registration data
class UserLogin(BaseModel):
    """
    Модель для авторизації користувача: Використовується для перевірки даних користувача при авторизації.

    **Атрибути:**
    - phone: Номер телефону користувача (мінімум 13 символів).
    - password: Пароль користувача (від 6 до 20 символів).

    **Приклад:**
    ```json
    {
        "phone": "+380987654321",
        "password": "securepassword"
    }
    ```
    """
    phone: str = Field(..., min_length=13)
    password: str = Field(..., min_length=6, max_length=20)

class UserRegister(BaseModel):
    """
    Модель для реєстрації користувача: Використовується для створення нового користувача в системі.

    **Атрибути:**
    - name: Ім'я користувача (строка).
    - phone: Номер телефону користувача (мінімум 13 символів).
    - password: Пароль користувача (від 6 до 20 символів).
    - status: Статус користувача (строка, наприклад "user", "admin").

    **Приклад:**
    ```json
    {
        "name": "Ivan Ivanov",
        "phone": "+380987654321",
        "password": "securepassword",
        "status": "user"
    }
    ```
    """

    name: str
    phone: str = Field(..., min_length=13)
    password: str = Field(..., min_length=6, max_length=20)
    status: str

class UserEdit(BaseModel):
    """
    Модель для редагування користувача: Використовується для оновлення даних користувача в системі.

    **Атрибути:**
    - id: Унікальний ідентифікатор користувача (строка).
    - name: Нове ім'я користувача (строка, необов'язково).
    - password: Новий пароль користувача (строка, необов'язково).
    - status: Новий статус користувача (строка, необов'язково).

    **Приклад:**
    ```json
    {
        "id": "607d1f77bcf86cd799439011",
        "name": "Ivan Ivanov",
        "password": "new_secure_password",
        "status": "admin"
    }
    ```
    """

    id: str
    name: str
    status: str
    password: str

class DeleteUserRequest(BaseModel):
    """
    Модель для видалення користувача: Використовується для видалення користувача за його ідентифікатором.

    **Атрибути:**
    - id: Унікальний ідентифікатор користувача (строка).
    - phone: Номер телефону користувача (строка).

    **Приклад:**
    ```json
    {
        "id": "607d1f77bcf86cd799439011",
        "phone": "+380987654321"
    }
    ```
    """

    id: str
    phone: str

class DeleteGroupRequest(BaseModel):
    group_name: str

class GroupCreateRequest(BaseModel):
    """
    Модель для створення групи: Використовується для створення нової групи в системі.

    **Атрибути:**
    - group_name: Назва групи (строка).
    - manager_phone: Номер телефону менеджера групи (строка).
    - user_phones: Список телефонів користувачів у групі (список строк).

    **Приклад:**
    ```json
    {
        "group_name": "Team A",
        "manager_phone": "+380987654321",
        "user_phones": ["+380987654322", "+380987654323"]
    }
    ```
    """

    group_name: str  # Название группы
    manager_phone: str  # ID менеджера
    user_phones: List[str]  # Список пользователей
    
class GroupEdit(BaseModel):
    """
    Модель для редагування групи: Використовується для оновлення даних групи в системі.

    **Атрибути:**
    - group_name: Назва групи (строка).
    - manager_phone: Номер телефону менеджера групи (строка).
    - user_phones: Список телефонів користувачів у групі (список строк).
    - active: Статус активності групи (ціле число, 1 - активна, 0 - неактивна).

    **Приклад:**
    ```json
    {
        "group_name": "Team A",
        "manager_phone": "+380987654321",
        "user_phones": ["+380987654322", "+380987654323"],
        "active": 1
    }
    ```
    """

    group_name: str  # Название группы
    manager_phone: str  # ID менеджера
    user_phones: List[str]  # Список пользователей
    active: int

class Task(BaseModel):
    """
    Модель для задачі: Використовується для створення або оновлення задачі.

    **Атрибути:**
    - title: Заголовок задачі (строка).
    - description: Опис задачі (строка).
    - startDate: Дата початку задачі (строка).
    - endDate: Дата закінчення задачі (строка).
    - startTime: Час початку задачі (строка).
    - endTime: Час закінчення задачі (строка).
    - repeatDays: Дні тижня, на які повторюється задача (список строк).
    - group: Назва групи, до якої належить задача (строка).
    - taskType: Тип задачі (строка).
    - importance: Важливість задачі (ціле число).
    - needphoto: Потрібен фото-звіт (ціле число, 1 - так, 0 - ні).
    - needcomment: Потрібен коментар (ціле число, 1 - так, 0 - ні).

    **Приклад:**
    ```json
    {
        "title": "Task 1",
        "description": "Task description",
        "startDate": "2025-04-01",
        "endDate": "2025-04-02",
        "startTime": "08:00",
        "endTime": "09:00",
        "repeatDays": ["Monday", "Wednesday"],
        "group": "Team A",
        "taskType": "Urgent",
        "importance": 1,
        "needphoto": 1,
        "needcomment": 1
    }
    ```
    """

    title: str
    description: str
    startDate: str
    endDate: str
    startTime: str
    endTime: str
    repeatDays: List[str] = []
    group: str
    taskType: str
    importance: int
    needphoto: int
    needcomment: int
 
class TaskEdit(BaseModel):
    """
    Модель для редагування задачі: Використовується для оновлення задачі.

    **Атрибути:**
    - title: Заголовок задачі (строка).
    - description: Опис задачі (строка).
    - start_date: Дата початку задачі (строка).
    - end_date: Дата закінчення задачі (строка).
    - start_time: Час початку задачі (строка).
    - end_time: Час закінчення задачі (строка).
    - repeat_days: Дні тижня, на які повторюється задача (список строк).
    - group: Назва групи, до якої належить задача (строка).
    - task_type: Тип задачі (строка).
    - importance: Важливість задачі (ціле число).
    - created_by: Номер телефону користувача, який створив задачу (строка).
    - taskid: Унікальний ідентифікатор задачі (строка).
    - needphoto: Потрібен фото-звіт (ціле число, 1 - так, 0 - ні).
    - needcomment: Потрібен коментар (ціле число, 1 - так, 0 - ні).

    **Приклад:**
    ```json
    {
        "title": "Updated Task 1",
        "description": "Updated description",
        "start_date": "2025-04-01",
        "end_date": "2025-04-02",
        "start_time": "09:00",
        "end_time": "10:00",
        "repeat_days": ["Tuesday"],
        "group": "Team A",
        "task_type": "Urgent",
        "importance": 2,
        "created_by": "+380987654321",
        "taskid": "607d1f77bcf86cd799439012",
        "needphoto": 1,
        "needcomment": 1
    }
    ```
    """

    title: str
    description: str
    start_date: str
    end_date: str
    start_time: str
    end_time: str
    repeat_days: List[str] = []
    group: str
    task_type: str
    importance: int
    created_by: str
    taskid: str
    needphoto: int
    needcomment: int

class TaskTime(BaseModel):
    """
    Модель для часу задачі: Використовується для відправки часу виконання задачі.

    **Атрибути:**
    - start_time: Час початку задачі (строка).
    - finish_time: Час завершення задачі (строка).
    - pause_start: Час початку паузи (список строк).
    - pause_end: Час закінчення паузи (список строк).
    - id_task: Ідентифікатор задачі (строка).
    - keyTime: Унікальний ключ часу (строка).
    - comment: Коментар до задачі (необов'язково).

    **Приклад:**
    ```json
    {
        "start_time": "09:00",
        "finish_time": "10:00",
        "pause_start": ["09:30"],
        "pause_end": ["09:40"],
        "id_task": "607d1f77bcf86cd799439012",
        "keyTime": "2025-04-01T09:00",
        "comment": "Paused for a break"
    }
    ```
    """

    start_time: str
    finish_time: str
    pause_start: List[str]
    pause_end: List[str]
    id_task: str
    keyTime: str
    comment: Optional[str] # type: ignore

class TaskTimeCancel(BaseModel):
    """
    Модель для скасування часу задачі: Використовується для скасування часу задачі.

    **Атрибути:**
    - cancel_time: Час скасування задачі (строка).
    - id_task: Ідентифікатор задачі (строка).
    - keyTime: Унікальний ключ часу (строка).
    - comment: Коментар до скасування (строка).

    **Приклад:**
    ```json
    {
        "cancel_time": "2025-04-01T10:00",
        "id_task": "607d1f77bcf86cd799439012",
        "keyTime": "2025-04-01T09:00",
        "comment": "Task cancelled due to unforeseen circumstances"
    }
    ```
    """
    cancel_time: str
    id_task: str
    keyTime: str
    comment: str

