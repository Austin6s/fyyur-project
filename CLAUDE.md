# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fyyur is a venue and artist booking application built with Flask and PostgreSQL. Users can create, search, and manage venues, artists, and shows. Includes bonus features: artist availability windows and discography management.

**Course Context**: This is Project 1 from the Udacity "Backend Developer with Python" Nanodegree, part of Course 02 "SQL and Data Modeling for the Web with Python". The project demonstrates:
- SQLAlchemy ORM and Flask-SQLAlchemy
- Database CRUD operations
- Model relationships and data modeling
- Database migrations with Flask-Migrate/Alembic

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Run tests
pytest test_app.py -v

# Linting
flake8

# Code formatting
black .

# Database migrations
flask db migrate
flask db upgrade

# Fabric tasks
fab test      # Run tests
fab prepare   # Test, commit, and push
fab deploy    # Deploy to Heroku
```

## Testing

Tests use a separate database (`fyyur_test`). The test file sets `TEST_DATABASE=true` automatically.

```bash
pytest test_app.py -v
```

## Architecture

**Single-file Flask app** (`app.py`) containing models, routes, and controllers.

### Database Models

- **Venue** - Has many Shows (cascade delete)
- **Artist** - Has many Shows, Availability windows, Albums (all cascade delete)
- **Show** - Links Venue and Artist with start_time
- **Availability** - Artist booking windows (start_time, end_time)
- **Album** - Artist discography, has many Songs
- **Song** - Individual tracks in Albums

### Key Implementation Details

- Genres stored as comma-separated strings in DB; split/join in controllers
- Boolean fields use `"y"` string checks from forms
- DELETE operations use form POST for browser compatibility
- Show creation validates against artist availability windows
- Past/upcoming shows determined by comparing start_time to `datetime.now()`

### Database Configuration

- Production: `fyyur` database
- Testing: `fyyur_test` database (triggered by `TEST_DATABASE` env var)
- PostgreSQL on localhost:5432
- Password from `.env` file (`POSTGRES_PWD`)

## Code Style

- Black formatting (line length 88)
- Flake8 linting (config in `.flake8`)
