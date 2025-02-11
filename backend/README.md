# Game Leaderboard


## Overview
The Game Leaderboard is a plstform that allows game creation, start and end different games and allows different users to participate in different games. Once a user joins a game, a random score is assigned to the user. There are two main Leaderboards which are Global Leaderboard that shows global ranking for users having played different games and the other is the Game Leaderboard that displays the user rankings for a specific game. Additionally these scores are added to many more global and game leaderboards having a second parameter as date(YYYY-MM-DD). This allows to fetch the rankings of the specific leaderboard on that particular day. Another thing is the Game Popularity Index which calculates the popularity indexs core of each game.

The backend is built using FastAPI and integrates with Amazon RDS Postgres to manage and store data. Redis is used for implementing Sorted Sets for Leaderboard Rankings. 


## Features
- ✅ Fast & Scalable – Uses FastAPI, PostgreSQL, and Redis for high performance.
- ✅ Real-time Leaderboards – Efficient ranking system powered by Redis sorted sets.
- ✅ Automated Popularity Index Updates – Scheduler updates rankings every 5 minutes.
- ✅ Seamless Database Integration – PostgreSQL for persistent storage, Redis for quick lookups.


## Table of Contents
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Running Instructions](#running-instructions)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Technologies Used](#technologies-used)
- [Future Scopes](#future-scopes)
---

## System Requirements
Before you begin, ensure you have the following installed:
- **Python 3.8+**
- **PostgreSQL (pgAdmin)**


## Installation

## Setting BACKEND
### 1. Clone the Repository and create a virtual environment
```bash
git clone https://github.com/your-username/Game-Leaderboard.git
cd backend
python -m venv venv
venv\Scripts\activate

```
### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running Instructions

### 1. Create a .env file in the backend/app directory with the following content

#### Add the Postgres PgAdmin variables for local deployment.
Note: I have two variables in my code, one is POSTGRES_URL (which is for local pgAdmin) and the other one USED in MY CODE is POSTGRES_URL_RDS (which is cloud Postgres. Ensure you pass the right variable as per your need to the Postgres engine in app/configs/database/postgres_config)
```bash
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_URL
```

#### Run Database Migrations in backend directory
```bash
alembic init alembic
alembic revision --autogenerate -m "New configuration"
alembic upgrade head
```

### 2. Start a Redis local Server
```bash
redis-server --port 6379
```

- Additonally update the host in backend/app/configs/redis/redis.py
- - For local redis server:
```bash
host = 'redis://localhost:6379'
```
- - For Docker Image of Redis
```bash
host = 'redis://redis:6379'
```

### 3. Start the Backend Server
```bash
cd backend
uvicorn app.main:app --reload
```

## OR
- Start Docker in Background
- Clone the repository.
- Run the following commands.
```bash
cd backend
python -m venv venv
venv\Scripts\activate

docker-compose up --build
```
### This will run a Docker container having the FastAPI Backend as well as a Redis image server from Docker.

### The Swagger UI docs will be accessible at http://127.0.0.1:8000/docs for testing.


## API Endpoints

### User Operations
- Register a new User: `POST /api/v1/users`
- Update a User: `PUT /api/v1/users/{user_id}`
- Delete a User: `DELETE /api/v1/users/{user_id}`

### Game Operations
- Create a new Game: `POST /api/v1/games`
- Start a new Game `POST /api/v1/games/{game_id}/start`
- Stop an active Game: `POST /api/v1/games/{game_id}/end`
- Upvote a Game: `POST /api/v1/games/{game_id}/upvote`
- Get the Game Popularity Index: `GET /api/v1/games/popularity-index`
- Join a Game as a User: `POST /api/v1/games/{game_id}/join`
- Exit a Game as a User: `PUT /api/v1/games/{game_id}/exit`

### Leaderboard Operations
- Get Global Leaderboard: `GET /api/v1/leaderboard/global`
or
- Get Global Leaderboard for a specific date: `GET /api/v1/leaderboard/global?date=YYYY-MM-DD`
- Get a specific Game's Leaderboard: `GET /api/v1/leaderboard/{game_id}`
or
- Get s specific Game's Leaderboard for a specific date: `GET /api/v1/leaderboard/{game_id}?date=YYYY-MM-DD`


## Steps to Follow
- Go to http://127.0.0.1:8000/docs
- There are more than 5 games already created. (Game IDs: 3, 4, 5, 6, 7, 8, 9)
- There are multiple users already created or can create more. (User IDs: 2, 4, 5, 7, 8, 9)
- Start any game/multiple games using the above Game IDs.
- Join different games using the given Game IDs and User IDs.
- Once the Contestant joins a game, a random score is assigned to the User ID.
- Fetch the Leaderboard at Global and Game Level.
- Can pass an optional date parameter to fetch leaderboard of that specific date.
- Fetch the Game Popularity Index which is actually refreshed every 5 mins.

## Technologies Used
- **FastAPI**: Python web framework for building APIs.
- **PostgreSQL**: PostgreSQL database for storing and querying structured data(users, calls, point of contacs, leads).
- **Pydantic**: Input Data validation.
- **Redis**: Sorted Sets
- **Swagger UI**: Interactive API documentation.
