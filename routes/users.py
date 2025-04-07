from fastapi import APIRouter, HTTPException, status, Depends, Request
from db.dbconn import users_collections, groups, tasks, completedtasks  # Assuming this is your database collection or function
from db.hash import Hash
from jose import jwt
from logger import logger
from fastapi.encoders import jsonable_encoder
import os
from shemas.users import UserLogin, UserRegister, DeleteUserRequest, GroupCreateRequest, DeleteGroupRequest, UserEdit, GroupEdit, Task, TaskTime,TaskTimeCancel, TaskEdit
from middelware.auth import auth_middleware_status_return, verify_admin_token, auth_middleware_phone_return
from bson import ObjectId
from datetime import datetime
import uuid
from urllib.parse import unquote
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
user_app = APIRouter()  # Correct instantiation of APIRouter

@user_app.post("/login")
async def login_user(user: UserLogin):
    """
    Авторизація користувача: аутентифікує користувача та повертає JWT токен.

    **Запит:**
    - phone: Телефон користувача (строка)
    - password: Пароль користувача (строка)

    **Відповідь:**
    - token: JWT токен у форматі {"token": <jwt_token>} (строка)

    **Помилки:**
    - 400 BAD REQUEST: Якщо користувач не знайдений або пароль невірний

    **Приклад запиту:**
    ```json
    {
        "phone": "+380123456789",
        "password": "mysecretpassword"    }
    ```

    **Приклад відповіді:**
    ```json
    {
        "token": "your_jwt_token_here"
    }
    ```
    """
    
    found_user = users_collections.find_one({"phone": user.phone})
    
    if not found_user:
        error_id = str(uuid.uuid4())  # Генеруємо унікальний ID для помилки
        logger.warning(f"[{error_id}] Login failed for {user.phone}: not found", extra={'user': user.phone})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Користувача не знайдено", "error_id": error_id}
        )

    # Перевірка пароля
    if not pwd_context.verify(user.password, found_user["password"]):
        error_id = str(uuid.uuid4())  # Генеруємо новий унікальний ID для помилки
        logger.warning(f"[{error_id}] Wrong password for {user.phone}", extra={'user': user.phone})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Невірний пароль", "error_id": error_id}
        )

    # Генерація токену
    token = jwt.encode({
        "sub": user.phone,  # Зазначаємо суб'єкта (phone)
        "exp": 3600  # Термін дії токену (1 година)
    }, "your_secret_key", algorithm="HS256")

    # Логування успішного входу
    logger.info(f"User {user.phone} logged in successfully", extra={'user': user.phone})
    
    return {"token": token}

@user_app.get("/get_status/{token}")
async def login_user(token:str):
    payload = jwt.decode(token, os.getenv("SecretJwt"), algorithms=["HS256"])
    return str(payload.get("status"))

@user_app.post("/register", dependencies=[Depends(verify_admin_token)])
async def login_user(request: Request, user: UserRegister):
    """
    Реєстрація користувача: Створює нового користувача в системі.

    **Запит:**
    - phone: Телефон користувача (строка)
    - name: Ім'я користувача (строка)
    - password: Пароль користувача (строка)

    **Відповідь:**
    - message: Статус запиту, повідомлення про успішну реєстрацію.

    **Помилки:**
    - 400 BAD REQUEST: Якщо користувач вже існує в базі.

    **Приклад запиту:**
    ```json
    {
        "phone": "+380987654321",
        "name": "Ivan Ivanov",
        "password": "securepassword"
    }
    ```

    **Приклад відповіді:**
    ```json
    {
        "message": "User successfully registered"
    }
    """
    existing_user = users_collections .find_one({"phone": user.phone}) # Check if the email already exists in the database
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists") # Return error if user exists
    hashed_password = Hash.bcrypt(user.password) # Hash the password for security
    user.password = hashed_password   
    try:
        users_collections.insert_one(dict(user)) # Insert new user into database
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="There is some problem with the database, please try again later")
    return {"status": "Ok"} # Return success message and token

@user_app.get("/get_users", dependencies=[Depends(verify_admin_token)])
async def get_users(request: Request):
    """
    Отримати список користувачів: Отримує список усіх користувачів, які не є адміністраторами.

    **Запит:**
    - Немає.

    **Відповідь:**
    - users: Список користувачів (масив об'єктів).
      - _id: Унікальний ідентифікатор користувача (строка)
      - name: Ім'я користувача (строка)
      - phone: Телефон користувача (строка)
      - status: Статус користувача (строка)

    **Приклад відповіді:**
    ```json
    [
        {
            "_id": "607d1f77bcf86cd799439011",
            "name": "Ivan Ivanov",
            "phone": "+380987654321",
            "status": "user"
        },
        {
            "_id": "607d1f77bcf86cd799439012",
            "name": "Petro Petrov",
            "phone": "+380987654322",
            "status": "user"
        }
    ]
    """

    users = users_collections.find({"status": {"$ne": "admin"}})
    # Преобразуем _id в строку для каждого документа
    users_list = []
    for user in users:
        user["_id"] = str(user["_id"])  # Преобразуем _id в строку
        users_list.append(user)
    return users_list

@user_app.post("/delete_user", dependencies=[Depends(verify_admin_token)])
async def delete_user(request: Request, user: DeleteUserRequest):
    """
    Видалення користувача: Видаляє користувача з бази даних.

    **Запит:**
    - id: ID користувача для видалення (строка)

    **Відповідь:**
    - message: Повідомлення про успішне видалення.

    **Помилки:**
    - 400 BAD REQUEST: Якщо ID користувача некоректне.
    - 404 NOT FOUND: Якщо користувача не знайдено.

    **Приклад запиту:**
    ```json
    {
        "id": "63a5fe9d80c774c1a7e586fe"
    }
    ```

    **Приклад відповіді:**
    ```json
    {
        "message": "User successfully deleted"
    }
    """
    # Проверяем валидность ObjectId
    if not ObjectId.is_valid(user.id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    result = users_collections.delete_one({"_id": ObjectId(user.id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    tasks_for_delete = [i['group_name'] for i in groups.find({"manager_phone": user.phone}, {'_id':0, 'group_name':1})]
    
    
    print(tasks_for_delete)
    groups.delete_many({"manager_phone": user.phone})
    groups.update_many(
    {"user_phones": {"$in": [user.phone]}},  # Условие для поиска документов
    {"$pull": {"user_phones": user.phone}}   # Удаление телефона из массива   
)
    tasks.delete_many({'group':{"$in": [tasks_for_delete]}})
    
    return {"message": "User successfully deleted"}

@user_app.post("/delete_group", dependencies=[Depends(verify_admin_token)])
async def delete_group(request: Request, group: DeleteGroupRequest):
    """
    Видалення групи: Видаляє групу з бази даних та всі завдання, пов'язані з цією групою.

    **Запит:**
    - group_name: Назва групи для видалення (строка)

    **Відповідь:**
    - message: Повідомлення про успішне видалення групи.

    **Помилки:**
    - 404 NOT FOUND: Якщо групу не знайдено.

    **Приклад запиту:**
    ```json
    {
        "group_name": "GroupName"
    }
    ```

    **Приклад відповіді:**
    ```json
    {
        "message": "Group successfully deleted"
    }
    ```
"""
    
    result = groups.delete_one({"group_name": group.group_name})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Group not found")

    tasks.delete_many({'group': group.group_name})
    
    return {"message": "Group successfully deleted"}

@user_app.get("/get_users_add", dependencies=[Depends(verify_admin_token)])
async def get_users_add(request: Request):
    """
    Отримання користувачів для додавання: Повертає список користувачів, які не мають статусу "admin" або "receive".

    **Запит:** 
    - немає

    **Відповідь:**
    - users: Список користувачів з їх іменами та телефонами.

    **Приклад відповіді:**
    ```json
    [
        {"name": "John Doe", "phone": "+380987654321"},
        {"name": "Jane Doe", "phone": "+380987654322"}
    ]
    ```
"""
    users = users_collections.find(
        {
        "status": { "$nin": ["admin", "receive"] } 
        },
        {
            "name": 1,    
            "phone": 1,  
            "_id": 0     
        }
        );   
    users = list(users)
    return users 

@user_app.get("/get_users_receive", dependencies=[Depends(verify_admin_token)])
async def get_users_receive(request: Request):
    """
    Отримання користувачів для отримання: Повертає список користувачів, які не мають статусу "admin" або "add".

    **Запит:** 
    - немає

    **Відповідь:**
    - users: Список користувачів з їх іменами та телефонами.

    **Приклад відповіді:**
    ```json
    [
        {"name": "John Doe", "phone": "+380987654321"},
        {"name": "Jane Doe", "phone": "+380987654322"}
    ]
    ```
"""
    users = users_collections.find(
        {
        "status": { "$nin": ["admin", "add"] } 
        },
        {
            "name": 1,    
            "phone": 1,  
            "_id": 0     
        }
        );   
    users = list(users)
    return users 

@user_app.post("/create_group/", dependencies=[Depends(verify_admin_token)])
async def create_group(group: GroupCreateRequest):
    """
    Створення групи: Створює нову групу в базі даних.

    **Запит:**
    - group_name: Назва групи (строка)
    - manager_phone: Телефон менеджера групи (строка)
    - user_phones: Список телефонів користувачів (список рядків)

    **Відповідь:**
    - message: Повідомлення про успішне створення групи.

    **Помилки:**
    - 400 BAD REQUEST: Якщо група з такою назвою вже існує.

    **Приклад запиту:**
    ```json
    {
        "group_name": "Developers",
        "manager_phone": "+380987654321",
        "user_phones": ["+380987654322", "+380987654323"]
    }
    ```

    **Приклад відповіді:**
    ```json
    {
        "message": "Group successfully created"
    }
    ```
"""
    existing_group = groups.find_one({"group_name": group.group_name}) # Check if the email already exists in the database
    if existing_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="The group with this name already exists") # Return error if user exists
    group_data = {
        "group_name": group.group_name,
        "manager_phone": group.manager_phone,
        "user_phones": group.user_phones,
        "active": 1
    }
    groups.insert_one(group_data)
    return {"message": "Group successfully created"}

@user_app.get("/get_groups/", dependencies=[Depends(verify_admin_token)])
async def get_groups(request: Request):
    """
    Отримання всіх груп: Повертає список всіх груп з бази даних.

    **Запит:** 
    - немає

    **Відповідь:**
    - groups: Список груп з їх назвами, телефонами менеджерів, телефонами користувачів та активністю.

    **Приклад відповіді:**
    ```json
    [
        {
            "group_name": "Developers",
            "manager_phone": "+380987654321",
            "user_phones": ["+380987654322", "+380987654323"],
            "active": 1
        }
    ]
    ```
"""

    groups_all = groups.find({}, {
            "group_name": 1,    
            "manager_phone": 1,  
            "user_phones": 1,
            "active": 1,
            "_id": 0     
        })
    return list(groups_all)

@user_app.post("/edit_user/", dependencies=[Depends(verify_admin_token)])
async def edit_user(request: Request, user: UserEdit):
    """
    Оновлення користувача: Оновлює дані користувача в системі.

    **Запит:**
    - id: Унікальний ідентифікатор користувача (строка)
    - name: Нове ім'я користувача (строка, необов'язково)
    - password: Новий пароль користувача (строка, необов'язково)
    - status: Новий статус користувача (строка, необов'язково)

    **Відповідь:**
    - message: Статус запиту, повідомлення про успішне оновлення користувача.

    **Помилки:**
    - 400 BAD REQUEST: Якщо не було надано жодного дійсного поля для оновлення.
    - 404 NOT FOUND: Якщо користувач не знайдений.

    **Приклад запиту:**
    ```json
    {
        "id": "607d1f77bcf86cd799439011",
        "name": "Ivan Ivanov",
        "password": "new_secure_password",
        "status": "user"
    }
    ```

    **Приклад відповіді:**
    ```json
    {
        "message": "User updated successfully"
    }
    """

    user_id = ObjectId(user.id)  # Если у вас поле '_id' в MongoDB, то используйте ObjectId
    update_data = {}

    if user.name:
        update_data["name"] = user.name
    if user.password:
        update_data["password"] = Hash.bcrypt(user.password)
    if user.status is not None: 
        update_data["status"] = user.status

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    result = users_collections.update_one(
        {"_id": user_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User updated successfully"}    

@user_app.post("/edit_group/", dependencies=[Depends(verify_admin_token)])
async def edit_group(request: Request, user: GroupEdit):
    """
    Оновлення групи: Оновлює дані групи в базі даних.

    **Запит:**
    - group_name: Назва групи (строка)
    - manager_phone: Телефон менеджера групи (необов'язково, рядок)
    - user_phones: Список телефонів користувачів (необов'язково, список рядків)
    - active: Активність групи (необов'язково, ціле число)

    **Відповідь:**
    - message: Повідомлення про успішне оновлення групи.

    **Помилки:**
    - 404 NOT FOUND: Якщо групу не знайдено.

    **Приклад запиту:**
    ```json
    {
        "group_name": "Developers",
        "manager_phone": "+380987654321",
        "user_phones": ["+380987654322", "+380987654323"],
        "active": 1
    }
    ```

    **Приклад відповіді:**
    ```json
    {
        "message": "Group updated successfully"
    }
    ```
"""

    update_data = {}

    if user.manager_phone:
        update_data["manager_phone"] = user.manager_phone
    if user.user_phones:
        update_data["user_phones"] = user.user_phones
    update_data["active"] = user.active
   
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    result = groups.update_one(
        {"group_name": user.group_name},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Group not found")

    return {"message": "Group updated successfully"}    

@user_app.get("/get_my_groups")
async def login_user(request: Request, phone = Depends(auth_middleware_phone_return)):
    """
    Отримання моїх груп: Повертає список груп, якими управляє користувач за номером телефону.

    **Запит:** 
    - phone: Телефон користувача (строка)

    **Відповідь:**
    - groups: Список назв груп.

    **Приклад відповіді:**
    ```json
    ["Developers", "Managers"]
    ```
"""

    results = groups.find({"manager_phone": phone}, {"group_name": 1, "_id": 0}) 
    results2 = list()
    for i in results:
        results2.append(i["group_name"])    
    return results2  

@user_app.get("/get_my_info")
async def get_info(request: Request, phone = Depends(auth_middleware_phone_return)):
    """
    Отримання моєї інформації: Повертає інформацію про користувача за номером телефону.

    **Запит:** 
    - phone: Телефон користувача (строка)

    **Відповідь:**
    - users: Інформація про користувача, без пароля.

    **Приклад відповіді:**
    ```json
    [
        {
            "name": "John Doe",
            "phone": "+380987654321",
            "status": "active"
        }
    ]
    ```
"""

    results = users_collections.find({"phone": phone},{"password": 0, "_id": 0}) 
    re2 = list()
    for i in results:
        re2.append(i)
    print(re2)
    return jsonable_encoder(re2)

@user_app.post("/tasks")
async def create_task(request: Request, task: Task, phone=Depends(auth_middleware_phone_return)):
    """
    Створення задачі: Створює нову задачу в базі даних.

    **Запит:**
    - title: Назва задачі (строка)
    - description: Опис задачі (строка)
    - start_date: Дата початку задачі (строка)
    - end_date: Дата завершення задачі (строка)
    - start_time: Час початку задачі (строка)
    - end_time: Час завершення задачі (строка)
    - repeat_days: Дні повторення задачі (список цілих чисел)
    - group: Назва групи (строка)
    - task_type: Тип задачі (строка)
    - importance: Важливість задачі (ціле число)
    - needphoto: Чи потрібно фото (ціле число)
    - needcomment: Чи потрібно коментар (ціле число)

    **Відповідь:**
    - message: Повідомлення про успішне збереження задачі.

    **Помилки:**
    - 404 NOT FOUND: Якщо група не існує або користувач не має прав на створення задачі.

    **Приклад запиту:**
    ```json
    {
        "title": "Complete report",
        "description": "Finish the monthly report",
        "start_date": "2025-04-01",
        "end_date": "2025-04-02",
        "start_time": "10:00",
        "end_time": "18:00",
        "repeat_days": [1, 3, 5],
        "group": "Developers",
        "task_type": "Work",
        "importance": 1,
        "needphoto": 1,
        "needcomment": 0
    }
    ```

    **Приклад відповіді:**
    ```json
    {
        "message": "Task successfully saved to database"
    }
    ```
"""

    result = groups.find_one({"group_name": task.group}, {"manager_phone": 1, "_id": 0})
    name = users_collections.find({'phone': phone},{'name': 1})
    if not result or result["manager_phone"] != phone:
        raise HTTPException(status_code=404, detail="У вас немає прав для виконання цієї задачі")
    task_data = {
        "title": task.title,
        "description": task.description,
        "start_date": task.startDate,
        "end_date": task.endDate,
        "start_time": task.startTime,
        "end_time": task.endTime,
        "repeat_days": task.repeatDays,
        "group": task.group,
        "task_type": task.taskType,
        "importance": int(task.importance),
        "created_by": phone,
        'needphoto': task.needphoto,
        'needcomment': task.needcomment,
        "created_name": name[0]['name']
    }
    try:
        tasks.insert_one(task_data)
        return {"message": "Task successfully saved to database"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Failed to save task to database")

@user_app.get("/get_my_task")
async def get_tasks(request: Request, phone=Depends(auth_middleware_phone_return)):
    """
    Отримання моїх завдань: Повертає список завдань, пов'язаних з групами, в яких користувач бере участь.

    **Запит:** 
    - phone: Телефон користувача (строка)

    **Відповідь:**
    - tasks: Список завдань для користувача.

    **Приклад відповіді:**
    ```json
    [
        {
            "title": "Complete report",
            "description": "Finish the monthly report",
            "start_date": "2025-04-01",
            "end_date": "2025-04-02",
            "importance": 1
        }
    ]
    ```
"""

    r = groups.find({'user_phones': f"{phone}", 'active': 1},{"group_name": 1, "_id": 0})
    compltasks = completedtasks.find({"phone": f"{phone}"}, {"key_time": 1, "_id": 0})
    tasksCompleteIDs = []
    for i in compltasks:
        tasksCompleteIDs.append(i['key_time'])
    
    groups_name = []
    for i in r:
        groups_name.append(i["group_name"])
    tasks_cursor = tasks.find(
    {'group': {'$in': groups_name}}).sort([('importance', -1)])
    user_tasks = list(tasks_cursor)
    for i in range(0,len(user_tasks)):
        user_tasks[i]["_id"] = str(user_tasks[i]["_id"])    
    user_tasks.append(tasksCompleteIDs)
    return user_tasks

@user_app.post("/push_task")
async def login_user(request: Request, task: TaskTime, phone = Depends(auth_middleware_phone_return)):
    """
    Отримання моїх завдань: Повертає список завдань, пов'язаних з групами, в яких користувач бере участь.

    **Запит:** 
    - phone: Телефон користувача (строка)

    **Відповідь:**
    - tasks: Список завдань для користувача.

    **Приклад відповіді:**
    ```json
    [
        {
            "title": "Complete report",
            "description": "Finish the monthly report",
            "start_date": "2025-04-01",
            "end_date": "2025-04-02",
            "importance": 1
        }
    ]
    ```
"""

    task_data = {
        "start_time": task.start_time,
        "finish_time": task.finish_time,
        "pause_start": task.pause_start,
        "pause_end": task.pause_end,
        "id_task": task.id_task,
        "key_time": task.keyTime,
        "phone": phone,
        "comment": task.comment,
        'status': 1
    }   
    completedtasks.insert_one(task_data)
    return {"message": "Informations about task successfully saved to database"}

@user_app.post("/cancel_task")
async def login_user(request: Request, task_cancel: TaskTimeCancel, phone = Depends(auth_middleware_phone_return)):
    """
    Скасування задачі: Зберігає інформацію про скасовану задачу в базі даних.

    **Запит:**
    - task_cancel: Дані про скасування задачі (об'єкт TaskTimeCancel)

    **Відповідь:**
    - message: Повідомлення про успішне збереження інформації про скасовану задачу.

    **Приклад відповіді:**
    ```json
    {
        "message": "Informations about task successfully saved to database"
    }
    ```
"""

    task_data = {
        "cancel_time": task_cancel.cancel_time,
        "id_task": task_cancel.id_task,
        "key_time": task_cancel.keyTime,
        "phone": phone,
        "comment": task_cancel.comment,
        'status': 0
    }   
    completedtasks.insert_one(task_data)
    return {"message": "Informations about task successfully saved to database"}

@user_app.get("/get_my_created_task/")
async def get_tasks(request: Request, phone=Depends(auth_middleware_phone_return)):
    """
    Отримати інформацію про завдання: Отримує завдання, створені поточним користувачем.

    **Запит:**
    - phone: Телефон поточного користувача (строка).

    **Відповідь:**
    - tasks: Список завдань, створених користувачем (масив об'єктів).
      - _id: Унікальний ідентифікатор завдання (строка)
      - title: Назва завдання (строка)
      - description: Опис завдання (строка)
      - start_date: Дата початку завдання (строка)
      - end_date: Дата закінчення завдання (строка)
      - start_time: Час початку завдання (строка)
      - end_time: Час закінчення завдання (строка)
      - importance: Важливість завдання (число)
      - status: Статус завдання (число)

    **Приклад відповіді:**
    ```json
    [
        {
            "_id": "607d1f77bcf86cd799439013",
            "title": "Task 1",
            "description": "Description of task 1",
            "start_date": "2025-04-01",
            "end_date": "2025-04-02",
            "start_time": "08:00",
            "end_time": "12:00",
            "importance": 1,
            "status": 0
        },
        {
            "_id": "607d1f77bcf86cd799439014",
            "title": "Task 2",
            "description": "Description of task 2",
            "start_date": "2025-04-03",
            "end_date": "2025-04-04",
            "start_time": "10:00",
            "end_time": "14:00",
            "importance": 2,
            "status": 1
        }
    ]
    """

    tasks_cursor = tasks.find(
    {'created_by': phone}).sort([('importance', -1)])
    user_tasks = list(tasks_cursor)
    for i in range(0,len(user_tasks)):
        user_tasks[i]["_id"] = str(user_tasks[i]["_id"])    
    return user_tasks

@user_app.get("/get_infoprocent_about_task/{group}/{task_id}")
async def get_tasks(request: Request, group: str, task_id: str):
    task_id = unquote(task_id)
    print(task_id)
    count = groups.find_one(
    {'group_name': group}) 
    count2 = list(completedtasks.find({'key_time': task_id}))
    print(len(count2))
    return (len(count2)/len(count['user_phones'])) * 100
    
@user_app.delete("/delete_task/{task_id}")
async def delete_group(request: Request, task_id: str, phone=Depends(auth_middleware_phone_return)):
    """
    Видалення задачі: Видаляє задачу з бази даних.

    **Запит:**
    - task_id: Ідентифікатор задачі (строка)

    **Відповідь:**
    - message: Повідомлення про успішне видалення задачі.

    **Помилки:**
    - 404 NOT FOUND: Якщо задача не знайдена або у вас немає прав на її видалення.

    **Приклад запиту:**
    ```json
    {
        "task_id": "60d5c7b4e92c6c5e1f4d5c9b"
    }
    ```

    **Приклад відповіді:**
    ```json
    {
        "message": "Group successfully deleted"
    }
    ```
"""

    result = tasks.delete_one({"_id": ObjectId(task_id), 'created_by':phone})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="The task was not found or you do not have sufficient rights")
    
    return {"message": "Group successfully deleted"}

@user_app.put("/update_task/")
async def change_task(request: Request, task: TaskEdit, phone = Depends(auth_middleware_phone_return)):
    """
    Оновлення задачі: Оновлює дані задачі в базі даних.

    **Запит:**
    - taskid: Ідентифікатор задачі (строка)
    - title: Назва задачі (необов'язково, рядок)
    - description: Опис задачі (необов'язково, рядок)
    - start_date: Дата початку задачі (необов'язково, рядок)
    - end_date: Дата завершення задачі (необов'язково, рядок)
    - start_time: Час початку задачі (необов'язково, рядок)
    - end_time: Час завершення задачі (необов'язково, рядок)
    - repeat_days: Дні повторення задачі (необов'язково, список цілих чисел)
    - group: Назва групи (необов'язково, рядок)
    - task_type: Тип задачі (необов'язково, рядок)
    - importance: Важливість задачі (необов'язково, ціле число)
    - needphoto: Чи потрібно фото (необов'язково, ціле число)
    - needcomment: Чи потрібно коментар (необов'язково, ціле число)

    **Відповідь:**
    - message: Повідомлення про успішне оновлення задачі.

    **Помилки:**
    - 404 NOT FOUND: Якщо задача не знайдена або у вас немає прав на її оновлення.

    **Приклад запиту:**
    ```json
    {
        "taskid": "60d5c7b4e92c6c5e1f4d5c9b",
        "title": "Updated report",
        "description": "Updated the monthly report",
        "importance": 2
    }
    ```

    **Приклад відповіді:**
    ```json
    {
        "message": "Group successfully updated"
    }
    ```
"""

    task_data = {
        "title": task.title,
        "description": task.description,
        "start_date": task.start_date,
        "end_date": task.end_date,
        "start_time": task.start_time,
        "end_time": task.end_time,
        "repeat_days": task.repeat_days,
        "group": task.group,
        "task_type": task.task_type,
        "importance": task.importance,
        'needcomment': task.needcomment,
        'needphoto': task.needphoto
    }
    try:
        result = tasks.update_one(
            {"_id": ObjectId(task.taskid), 'created_by':phone},  
            {"$set": task_data}  
        )
        
        if result:
            return {"message": "Group successfully updated"}
        else:
            raise HTTPException(status_code=404, detail=f"Failed to update task to database: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to update task to database: {str(e)}")
    
    




