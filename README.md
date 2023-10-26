# MLSA LEADERBOARD API

A leaderboard to track MLSA's hacktoberfest participants contributions.

#### Frontend - https://hacktoberfest.onrender.com
#### Backend - https://leaderboard.acel.dev/api/schema/swagger-ui

## Running this project locally

### Prerequisites

Before running the project, ensure you have the following software installed on your system:

- Python 3.8: You can download and install Python 3.8 from the official Python website (https://www.python.org/downloads/)
- PostgreSQL: The main DB for the project. You can install it from their official website (https://www.postgresql.org/download/)
- Redis: You can install it by following the instructions on their official website (https://redis.io/docs/getting-started/installation/)
- Pipenv: Pipenv is a package manager and virtual environment tool for Python. Install it by running the following command:

### On Windows:


      pip install --user pipenv

### On macOS and Linux:


      pip3 install --user pipenv

## Setup

Follow these steps to set up and run the Django project:


**1. Clone the project repository:**

    git clone https://github.com/Acel-01/MLSA-LEADERBOARD-API.git


**2. Move into the project directory:**

    cd MLSA-LEADERBOARD-API/


**3. Install project dependencies using Pipenv:**

    pipenv install

**4. Create a .env file and Populate it using the .env.example file:**

    touch .env


**5. Create a SECRET_KEY value for your app by running the following command at a terminal prompt:**

    python -c 'import secrets; print(secrets.token_hex())'

Set the returned value as the value of SECRET_KEY in the .env file

**6. Activate the virtual environment:**

    pipenv shell


**7. Apply database migrations:**

    python manage.py migrate


**8. Start the PostgreSQL server**


**9. Start the development server:**

    python manage.py runserver

**10. Start Redis server:**

    sudo service redis-server start

**Link to Documentation:**

- Local - http://127.0.0.1:8000/api/schema/swagger-ui/#/
- Swagger - https://app.swaggerhub.com/apis-docs/Acel/mlsa-leaderboard_api/1.0.0#

## Running this project using Docker

### Prerequisites

- Install Docker: https://docs.docker.com/engine/install/
- Install Docker Compose: https://docs.docker.com/compose/install/

### Setup


**1. Clone the project repository:**

    git clone https://github.com/Acel-01/MLSA-LEADERBOARD-API.git


**2. Move into the project directory:**

    cd MLSA-LEADERBOARD-API/


**3. Create a .env.dev file and Populate it using the .env.dev.example file:**

    touch .env.dev


**4. Create a SECRET_KEY value for your app by running the following command at a terminal prompt:**

    python -c 'import secrets; print(secrets.token_hex())'

Set the returned value as the value of SECRET_KEY in the .env.dev file

**5. Build the images:**

    docker-compose -f docker-compose.yml build


**6. Apply database migrations:**

    docker-compose -f local.yml run --rm django python manage.py migrate


**7. Start the development server:**

    docker-compose -f local.yml
