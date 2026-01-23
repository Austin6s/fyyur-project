#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True, cascade='all, delete-orphan')

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True, cascade='all, delete-orphan')

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

class Availability(db.Model):
    __tablename__ = 'Availability'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)  # Available from
    end_time = db.Column(db.DateTime, nullable=False)    # Available until
    artist = db.relationship('Artist', backref=db.backref('availability', lazy=True, cascade='all, delete-orphan'))

class Album(db.Model):
    __tablename__ = 'Album'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Integer)
    artist = db.relationship('Artist', backref=db.backref('albums', lazy=True, cascade='all, delete-orphan'))
    songs = db.relationship('Song', backref='album', lazy=True, cascade='all, delete-orphan')

class Song(db.Model):
    __tablename__ = 'Song'

    id = db.Column(db.Integer, primary_key=True)
    album_id = db.Column(db.Integer, db.ForeignKey('Album.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  # Bonus: Show 10 most recently listed venues and artists
  recent_venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
  recent_artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
  return render_template('pages/home.html', recent_venues=recent_venues, recent_artists=recent_artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Get all venues
  venues = Venue.query.all()

  # Group venues by (city, state)
  areas = {}  # Dictionary: {(city, state): [venue1, venue2, ...]}
  now = datetime.now()

  for venue in venues:
    key = (venue.city, venue.state)

    # Count upcoming shows for this venue
    num_upcoming = len([show for show in venue.shows if show.start_time > now])

    venue_data = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming
    }

    if key not in areas:
      areas[key] = []
    areas[key].append(venue_data)

  # Convert to list format expected by template
  data = [
    {"city": city, "state": state, "venues": venues}
    for (city, state), venues in areas.items()
  ]

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  # ilike = case-insensitive LIKE
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  now = datetime.now()

  response = {
    "count": len(venues),
    "data": [{
      "id": v.id,
      "name": v.name,
      "num_upcoming_shows": len([s for s in v.shows if s.start_time > now])
    } for v in venues]
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # Query venue by id
  venue = Venue.query.get(venue_id)
  now = datetime.now()

  # Split shows into past and upcoming
  past_shows = []
  upcoming_shows = []

  for show in venue.shows:
    show_data = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    }
    if show.start_time < now:
      past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)

  # Build data dict for template
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(',') if venue.genres else [],  # Convert string back to list
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()

  # Validate form (checks DataRequired, URL validators, etc.)
  if not form.validate():
    flash('Invalid form submission. Please check required fields.')
    return render_template('forms/new_venue.html', form=form)

  try:
    venue = Venue(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      address=request.form.get('address'),
      phone=request.form.get('phone'),
      image_link=request.form.get('image_link'),
      facebook_link=request.form.get('facebook_link'),
      website=request.form.get('website_link'),
      genres=','.join(request.form.getlist('genres')),
      seeking_talent=request.form.get('seeking_talent') == 'y',
      seeking_description=request.form.get('seeking_description')
    )
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully listed!')
  except Exception as e:
    db.session.rollback()
    print(f'ERROR: {e}')
    flash('An error occurred. Venue could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)  # Cascade automatically deletes related shows
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # Query all artists from database
  artists = Artist.query.all()
  # Convert to list of dicts for template
  data = [{"id": artist.id, "name": artist.name} for artist in artists]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  now = datetime.now()

  response = {
    "count": len(artists),
    "data": [{
      "id": a.id,
      "name": a.name,
      "num_upcoming_shows": len([s for s in a.shows if s.start_time > now])
    } for a in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # Query artist by id
  artist = Artist.query.get(artist_id)
  now = datetime.now()

  # Split shows into past and upcoming
  past_shows = []
  upcoming_shows = []

  for show in artist.shows:
    show_data = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
    }
    if show.start_time < now:
      past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)

  # Get availability windows
  availability = [{
    "id": a.id,
    "start_time": str(a.start_time),
    "end_time": str(a.end_time)
  } for a in artist.availability]

  # Get albums with songs
  albums = [{
    "id": album.id,
    "name": album.name,
    "year": album.year,
    "songs": [{"id": s.id, "name": s.name} for s in album.songs]
  } for album in artist.albums]

  # Build data dict for template
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(',') if artist.genres else [],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
    "availability": availability,
    "albums": albums
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm()
  # Pass artist data to template (form fields populated via template)
  return render_template('forms/edit_artist.html', form=form, artist={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(',') if artist.genres else [],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  })

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist = Artist.query.get(artist_id)
    # Update attributes directly on the queried object
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = ','.join(request.form.getlist('genres'))
    artist.facebook_link = request.form.get('facebook_link')
    artist.image_link = request.form.get('image_link')
    artist.website = request.form.get('website_link')
    artist.seeking_venue = request.form.get('seeking_venue') == 'y'
    artist.seeking_description = request.form.get('seeking_description')
    # No add() needed - object already tracked by session
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

#  Artist Availability
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/availability', methods=['POST'])
def add_availability(artist_id):
  try:
    start = datetime.strptime(request.form.get('start_time'), '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(request.form.get('end_time'), '%Y-%m-%d %H:%M:%S')
    availability = Availability(artist_id=artist_id, start_time=start, end_time=end)
    db.session.add(availability)
    db.session.commit()
    flash('Availability added!')
  except Exception as e:
    db.session.rollback()
    print(f'ERROR: {e}')
    flash('Error adding availability.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/<int:artist_id>/availability/<int:avail_id>/delete', methods=['POST'])
def delete_availability(artist_id, avail_id):
  try:
    avail = Availability.query.get(avail_id)
    db.session.delete(avail)
    db.session.commit()
    flash('Availability removed.')
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

#  Albums & Songs
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/albums', methods=['POST'])
def add_album(artist_id):
  try:
    album = Album(
      artist_id=artist_id,
      name=request.form.get('album_name'),
      year=request.form.get('album_year') or None
    )
    db.session.add(album)
    db.session.commit()
    flash('Album added!')
  except Exception as e:
    db.session.rollback()
    print(f'ERROR: {e}')
    flash('Error adding album.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/albums/<int:album_id>/songs', methods=['POST'])
def add_song(album_id):
  try:
    album = Album.query.get(album_id)
    song = Song(album_id=album_id, name=request.form.get('song_name'))
    db.session.add(song)
    db.session.commit()
    flash('Song added!')
  except Exception as e:
    db.session.rollback()
    print(f'ERROR: {e}')
    flash('Error adding song.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=album.artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm()
  return render_template('forms/edit_venue.html', form=form, venue={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(',') if venue.genres else [],
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  })

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = ','.join(request.form.getlist('genres'))
    venue.facebook_link = request.form.get('facebook_link')
    venue.image_link = request.form.get('image_link')
    venue.website = request.form.get('website_link')
    venue.seeking_talent = request.form.get('seeking_talent') == 'y'
    venue.seeking_description = request.form.get('seeking_description')
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()

  if not form.validate():
    flash('Invalid form submission. Please check required fields.')
    return render_template('forms/new_artist.html', form=form)

  try:
    artist = Artist(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      phone=request.form.get('phone'),
      image_link=request.form.get('image_link'),
      facebook_link=request.form.get('facebook_link'),
      website=request.form.get('website_link'),
      genres=','.join(request.form.getlist('genres')),
      seeking_venue=request.form.get('seeking_venue') == 'y',
      seeking_description=request.form.get('seeking_description')
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully listed!')
  except Exception as e:
    db.session.rollback()
    print(f'ERROR: {e}')
    flash('An error occurred. Artist could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # Query all shows with related venue and artist data
  shows = Show.query.all()
  data = []

  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,  # Using relationship
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,  # Using relationship
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)  # Convert datetime to string
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()

  if not form.validate():
    flash('Invalid form submission. Please check required fields.')
    return render_template('forms/new_show.html', form=form)

  try:
    artist_id = request.form.get('artist_id')
    start_time_str = request.form.get('start_time')
    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')

    # Check artist availability
    artist = Artist.query.get(artist_id)
    if artist.availability:  # If artist has set availability windows
      is_available = any(
        avail.start_time <= start_time <= avail.end_time
        for avail in artist.availability
      )
      if not is_available:
        flash(f'Artist {artist.name} is not available at that time.')
        return render_template('forms/new_show.html', form=form)

    show = Show(
      venue_id=request.form.get('venue_id'),
      artist_id=artist_id,
      start_time=start_time
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception as e:
    db.session.rollback()
    print(f'ERROR: {e}')
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
