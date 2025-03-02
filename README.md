# Description

Ця програма реалізує програму у тому що люди могли відстежувати свої завдання, роботодавці могли давати завдання своїм працівникам і контролювати їх виконання і також вести аналіз виконаних завдань та окремих співробітників.

У додатку роботодавці можуть створювати групи зі співробітниками та видавати завдання їм усім або роботодавці можуть створювати окрему групу з одним працівником та видавати завдання йому.

Програма буде мати зручний функціонал фільтри та дуже інформативний аналіз виконаних завдань та окремих користувачів.

Ця програма реалізується для маленьких локальних магазинів, яким потрібен певний функціонал і для кожної мережі магізинів буде проявлятися окремий підхід.

На даний момент додаток знаходиться в розробці, але розробляється вже з потенційними покупцями та з урахуванням їх побажань.

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