# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fyyur is a musical venue and artist booking platform (Udacity Full Stack Nanodegree project). The UI and route controllers exist but currently use mock data. The core task is implementing database models and replacing mock data with real PostgreSQL queries.

## Development Commands

```bash
# Setup virtual environment
python -m virtualenv env
source env/bin/activate  # Windows: env/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Run development server (localhost:5000)
python3 app.py

# Database migrations (after configuring PostgreSQL)
flask db migrate
flask db upgrade
```

**Note:** Use Python 3.9 or lower to avoid dependency issues.

## Architecture

### Tech Stack
- **Backend:** Flask, SQLAlchemy ORM, PostgreSQL, Flask-Migrate, Flask-WTF
- **Frontend:** Jinja2 templates, Bootstrap 3

### Key Files
- `app.py` - Main application: models (incomplete), routes/controllers, filters
- `config.py` - Database URL configuration (TODO: set PostgreSQL connection)
- `forms.py` - WTForms for Venue, Artist, Show creation
- `templates/` - Jinja2 templates (complete, do not modify)

### Data Model Relationships
The app requires three models with a many-to-many relationship:
- `Venue` - venues where shows occur
- `Artist` - performers
- `Show` - junction table linking artists to venues with start_time (NOT YET IMPLEMENTED)

### Route Structure
- `/venues`, `/venues/<id>`, `/venues/search`, `/venues/create`
- `/artists`, `/artists/<id>`, `/artists/search`, `/artists/create`
- `/shows`, `/shows/create`
- Edit routes: `/venues/<id>/edit`, `/artists/<id>/edit`

## Implementation Requirements

### Missing Model Fields (based on mock data)
**Venue:** genres, website, seeking_talent (bool), seeking_description
**Artist:** website, seeking_venue (bool), seeking_description
**Show:** venue_id, artist_id, start_time (datetime)

### Critical Constraints
- Maintain exact mock data structure when returning real data
- Search must be case-insensitive and support partial string matching
- Venues must be grouped by city/state in `/venues` endpoint
- Past vs upcoming shows distinguished by comparing start_time to current datetime
- Use `form.field.data` to access WTForms values (not `request.form`)

### Forms Pattern
```python
form = VenueForm()
venue = Venue(name=form.name.data, city=form.city.data, ...)
```
