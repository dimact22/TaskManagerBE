from fastapi import APIRouter, HTTPException, status, Depends, Request
from db.dbconn import users_collections, groups, tasks, completedtasks  # Assuming this is your database collection or function
from db.hash import Hash
from jose import jwt
from fastapi.encoders import jsonable_encoder
import os
from shemas.users import UserLogin, UserRegister, DeleteUserRequest, GroupCreateRequest, DeleteGroupRequest, UserEdit, GroupEdit, Task, TaskTime,TaskTimeCancel, TaskEdit
from middelware.auth import auth_middleware_status_return, verify_admin_token, auth_middleware_phone_return
from bson import ObjectId
from datetime import datetime
from urllib.parse import unquote

user_app = APIRouter()  # Correct instantiation of APIRouter

@user_app.post("/login")
async def login_user(user: UserLogin):
    """
    Авторизація користувача: аутентифікує користувача та повертає JWT токен.

    Args:
        user (UserLogin): Об'єкт з телефоном та паролем користувача.

    Returns:
        dict: JWT-токен у форматі {"token": <jwt_token>}.

    Raises:
        HTTPException: Якщо користувач не знайдений (400 BAD REQUEST).
        HTTPException: Якщо пароль невірний (400 BAD REQUEST).
    """
    
    found_user = users_collections.find_one({"phone": user.phone})  # Access your DB here
    
    if not found_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")
    
    if Hash.verify(user.password, found_user["password"]):
        token = jwt.encode({'sub': found_user["phone"], 'status': found_user['status']}, os.getenv("SecretJwt"), algorithm='HS256')
        return {"token": token}
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")

@user_app.get("/get_status/{token}")
async def login_user(token:str):
    payload = jwt.decode(token, os.getenv("SecretJwt"), algorithms=["HS256"])
    return str(payload.get("status"))

@user_app.post("/register", dependencies=[Depends(verify_admin_token)])
async def login_user(request: Request, user: UserRegister):
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
    users = users_collections.find({"status": {"$ne": "admin"}})
    # Преобразуем _id в строку для каждого документа
    users_list = []
    for user in users:
        user["_id"] = str(user["_id"])  # Преобразуем _id в строку
        users_list.append(user)
    return users_list

@user_app.post("/delete_user", dependencies=[Depends(verify_admin_token)])
async def delete_user(request: Request, user: DeleteUserRequest):
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
    
    result = groups.delete_one({"group_name": group.group_name})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Group not found")

    tasks.delete_many({'group': group.group_name})
    
    return {"message": "Group successfully deleted"}

@user_app.get("/get_users_add", dependencies=[Depends(verify_admin_token)])
async def get_users_add(request: Request):
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
    results = groups.find({"manager_phone": phone}, {"group_name": 1, "_id": 0}) 
    results2 = list()
    for i in results:
        results2.append(i["group_name"])    
    return results2  

@user_app.get("/get_my_info")
async def get_info(request: Request, phone = Depends(auth_middleware_phone_return)):
    results = users_collections.find({"phone": phone},{"password": 0, "_id": 0}) 
    re2 = list()
    for i in results:
        re2.append(i)
    print(re2)
    return jsonable_encoder(re2)

@user_app.post("/tasks")
async def create_task(request: Request, task: Task, phone=Depends(auth_middleware_phone_return)):
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
    result = tasks.delete_one({"_id": ObjectId(task_id), 'created_by':phone})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="The task was not found or you do not have sufficient rights")
    
    return {"message": "Group successfully deleted"}

@user_app.put("/update_task/")
async def change_task(request: Request, task: TaskEdit, phone = Depends(auth_middleware_phone_return)):
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
    
    




