# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fyyur is a musical venue and artist booking platform (Udacity Full Stack Nanodegree project). This is a fully functioning Flask application connected to a PostgreSQL database.

## Development Commands

```bash
# Setup virtual environment
python -m virtualenv env
source env/bin/activate  # Windows: env/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Run development server (localhost:5000)
python3 app.py

# Database migrations
flask db migrate
flask db upgrade
```

**Note:** Use Python 3.9 or lower to avoid dependency issues.

## Architecture

### Tech Stack
- **Backend:** Flask, SQLAlchemy ORM, PostgreSQL, Flask-Migrate, Flask-WTF
- **Frontend:** Jinja2 templates, Bootstrap 3

### Key Files
- `app.py` - Main application: models, routes/controllers, filters
- `config.py` - Database URL configuration
- `forms.py` - WTForms for Venue, Artist, Show creation
- `templates/` - Jinja2 templates

### Data Models
- `Venue` - venues where shows occur
- `Artist` - performers
- `Show` - junction table linking artists to venues with start_time
- `Availability` - artist availability windows (bonus feature)
- `Album` - artist albums (bonus feature)
- `Song` - songs belonging to albums (bonus feature)

### Route Structure
- `/venues`, `/venues/<id>`, `/venues/search`, `/venues/create`
- `/artists`, `/artists/<id>`, `/artists/search`, `/artists/create`
- `/shows`, `/shows/create`
- Edit routes: `/venues/<id>/edit`, `/artists/<id>/edit`
- Delete routes: `/venues/<id>` (DELETE method)
- Bonus routes: `/artists/<id>/availability`, `/artists/<id>/albums`, `/albums/<id>/songs`

## Key Implementation Details

### Critical Constraints
- Search is case-insensitive and supports partial string matching
- Venues are grouped by city/state in `/venues` endpoint
- Past vs upcoming shows distinguished by comparing start_time to current datetime

### Forms Pattern
```python
form = VenueForm()
venue = Venue(name=form.name.data, city=form.city.data, ...)
```
