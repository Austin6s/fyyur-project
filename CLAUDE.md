# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fyyur is a Python Flask web application for booking musical artists at venues. It connects artists with venues and manages show listings.

**Tech Stack**: Python 3.12, Flask, PostgreSQL, SQLAlchemy, Flask-Migrate, Flask-WTF, Jinja2 templates, Bootstrap 3

## Common Commands

```bash
# Run the application (starts on http://localhost:5000)
python3 app.py

# Run tests
pytest test_app.py -v

# Run a single test
pytest test_app.py::test_function_name -v

# Format code
black app.py forms.py test_app.py config.py

# Lint code
flake8 app.py forms.py test_app.py config.py

# Database migrations
flask db migrate    # Create migration from model changes
flask db upgrade    # Apply migrations to database
```

## Architecture

### Main Files
- **app.py** - Flask app with models, routes, and controllers (all in one file)
- **forms.py** - WTForms form definitions (VenueForm, ArtistForm, ShowForm)
- **config.py** - Database configuration, uses `TEST_DATABASE` env var to switch between test/prod databases
- **test_app.py** - pytest test suite

### Database Models (defined in app.py)
- **Venue** - Music venues with location, contact info, genres
- **Artist** - Performers with contact info, genres, seeking status
- **Show** - Links Artist to Venue with start_time (foreign keys to both)
- **Availability** - Artist booking windows (belongs to Artist)
- **Album** - Artist discography (belongs to Artist)
- **Song** - Tracks within albums (belongs to Album)

All relationships use cascade delete - deleting an Artist removes their Shows, Availability, and Albums.

### URL Structure
- `/venues`, `/venues/<id>`, `/venues/create`, `/venues/<id>/edit`
- `/artists`, `/artists/<id>`, `/artists/create`, `/artists/<id>/edit`
- `/artists/<id>/availability` - POST to add availability windows
- `/artists/<id>/albums`, `/albums/<id>/songs` - Discography management
- `/shows`, `/shows/create`
- Search: POST to `/venues/search` or `/artists/search`

### Templates
- `templates/layouts/` - Base templates (main.html, form.html)
- `templates/pages/` - Page content templates
- `templates/forms/` - Form templates for create/edit
- `templates/errors/` - 404 and 500 error pages

## Testing Notes

Tests use a separate `fyyur_test` database. The test suite sets `TEST_DATABASE=true` environment variable which config.py uses to switch database connections.
