# Description

This program implements the program in that people could track their tasks, employers could give tasks to their employees and monitor their performance, and also conduct an analysis of completed tasks and individual employees.

In the application, employers can create groups with employees and issue tasks to all of them, or employers can create a separate group with one employee and issue tasks to him.

The program will have convenient filter functionality and a very informative analysis of completed tasks and individual users.

This program is implemented for small local stores that need certain functionality and for each chain of stores a separate approach will be shown.

At the moment, the application is under development, but is already being developed with potential buyers and taking into account their wishes.

# Setting up Virtual Environment
To set up a virtual environment for this application, follow these steps:

1. Open a command prompt at the root of the application's folder (TaskManagment).
2. Create a directory named venv:

    `mkdir venv`

3. Navigate into 'venv

    `cd venv`

4. create a virtual enviroment named 'Taskmanagment' using Python's 'venv' module: 

    ` python -m venv Taskmanagment`

5. activate the virtual enviroment 

on Windows:

`venv/Scripts/activate`

on macOS/Linux

`venv/bin/activate`

# Managing the Stack(Backend)
## Install Dependencies

1. Install the backend dependencies

    `pip install -r requirements.txt`

## Run the Application

1. Start the FastAPI server:

  `uvicorn main:app --reload`

2. Access Swagger UI:

Open your browser and navigate to http://localhost:8000/docs to access the Swagger UI documentation.

## Tools and Technologies
### MongoDB

This application uses MongoDB as the database. Follow these steps to set up MongoDB:

Install MongoDB:

Visit the MongoDB Download Center and follow the instructions to install MongoDB on your system.

Install MongoDB Compass:

Download and install MongoDB Compass, a GUI for MongoDB, to visualize and manage your MongoDB data.

Get your personall link to mongoDB container and write it in .env file
 
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