"""
Tests for Fyyur application.
Run with: pytest test_app.py -v
"""
import pytest
from datetime import datetime, timedelta
from app import app, db, Venue, Artist, Show, Availability, Album, Song


@pytest.fixture
def client():
    """Configure test client with test database."""
    import os
    from dotenv import load_dotenv
    load_dotenv()

    pwd = os.getenv("POSTGRES_PWD")
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://postgres:{pwd}@localhost:5432/fyyur_test"
    app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for testing

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def sample_venue(client):
    """Create a sample venue for testing."""
    with app.app_context():
        venue = Venue(
            name="Test Venue",
            city="San Francisco",
            state="CA",
            address="123 Test St",
            phone="555-1234",
            genres="Jazz,Rock",
            facebook_link="https://facebook.com/testvenue",
            website="https://testvenue.com",
            seeking_talent=True,
            seeking_description="Looking for artists",
        )
        db.session.add(venue)
        db.session.commit()
        venue_id = venue.id
    return venue_id


@pytest.fixture
def sample_artist(client):
    """Create a sample artist for testing."""
    with app.app_context():
        artist = Artist(
            name="Test Artist",
            city="Los Angeles",
            state="CA",
            phone="555-5678",
            genres="Pop,Electronic",
            facebook_link="https://facebook.com/testartist",
            website="https://testartist.com",
            seeking_venue=True,
            seeking_description="Looking for venues",
        )
        db.session.add(artist)
        db.session.commit()
        artist_id = artist.id
    return artist_id


class TestModels:
    """Test database models."""

    def test_venue_creation(self, client):
        """Test creating a venue."""
        with app.app_context():
            venue = Venue(name="New Venue", city="NYC", state="NY", address="456 Main")
            db.session.add(venue)
            db.session.commit()
            assert venue.id is not None
            assert venue.name == "New Venue"

    def test_artist_creation(self, client):
        """Test creating an artist."""
        with app.app_context():
            artist = Artist(name="New Artist", city="Chicago", state="IL", genres="Blues")
            db.session.add(artist)
            db.session.commit()
            assert artist.id is not None
            assert artist.name == "New Artist"

    def test_show_creation(self, client, sample_venue, sample_artist):
        """Test creating a show with venue and artist relationships."""
        with app.app_context():
            show = Show(
                venue_id=sample_venue,
                artist_id=sample_artist,
                start_time=datetime.now() + timedelta(days=7),
            )
            db.session.add(show)
            db.session.commit()
            assert show.id is not None
            assert show.venue.name == "Test Venue"
            assert show.artist.name == "Test Artist"

    def test_availability_creation(self, client, sample_artist):
        """Test creating availability for an artist."""
        with app.app_context():
            avail = Availability(
                artist_id=sample_artist,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(days=30),
            )
            db.session.add(avail)
            db.session.commit()
            assert avail.id is not None

    def test_album_and_song_creation(self, client, sample_artist):
        """Test creating album and songs."""
        with app.app_context():
            album = Album(artist_id=sample_artist, name="Test Album", year=2024)
            db.session.add(album)
            db.session.commit()

            song = Song(album_id=album.id, name="Test Song")
            db.session.add(song)
            db.session.commit()

            assert album.id is not None
            assert song.id is not None
            assert len(album.songs) == 1

    def test_cascade_delete_venue(self, client, sample_venue, sample_artist):
        """Test that deleting a venue cascades to its shows."""
        with app.app_context():
            show = Show(
                venue_id=sample_venue,
                artist_id=sample_artist,
                start_time=datetime.now(),
            )
            db.session.add(show)
            db.session.commit()
            show_id = show.id

            venue = Venue.query.get(sample_venue)
            db.session.delete(venue)
            db.session.commit()

            assert Show.query.get(show_id) is None

    def test_cascade_delete_artist(self, client, sample_artist):
        """Test that deleting an artist cascades to availability and albums."""
        with app.app_context():
            avail = Availability(
                artist_id=sample_artist,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(days=1),
            )
            album = Album(artist_id=sample_artist, name="Album to Delete")
            db.session.add_all([avail, album])
            db.session.commit()
            avail_id = avail.id
            album_id = album.id

            artist = Artist.query.get(sample_artist)
            db.session.delete(artist)
            db.session.commit()

            assert Availability.query.get(avail_id) is None
            assert Album.query.get(album_id) is None


class TestRoutes:
    """Test application routes."""

    def test_homepage(self, client):
        """Test homepage loads successfully."""
        response = client.get("/")
        assert response.status_code == 200

    def test_venues_page(self, client, sample_venue):
        """Test venues listing page."""
        response = client.get("/venues")
        assert response.status_code == 200
        assert b"Test Venue" in response.data

    def test_venue_detail_page(self, client, sample_venue):
        """Test venue detail page."""
        response = client.get(f"/venues/{sample_venue}")
        assert response.status_code == 200
        assert b"Test Venue" in response.data
        assert b"San Francisco" in response.data

    def test_artists_page(self, client, sample_artist):
        """Test artists listing page."""
        response = client.get("/artists")
        assert response.status_code == 200
        assert b"Test Artist" in response.data

    def test_artist_detail_page(self, client, sample_artist):
        """Test artist detail page."""
        response = client.get(f"/artists/{sample_artist}")
        assert response.status_code == 200
        assert b"Test Artist" in response.data
        assert b"Los Angeles" in response.data

    def test_shows_page(self, client, sample_venue, sample_artist):
        """Test shows listing page."""
        with app.app_context():
            show = Show(
                venue_id=sample_venue,
                artist_id=sample_artist,
                start_time=datetime.now(),
            )
            db.session.add(show)
            db.session.commit()

        response = client.get("/shows")
        assert response.status_code == 200
        assert b"Test Venue" in response.data
        assert b"Test Artist" in response.data

    def test_create_venue_form(self, client):
        """Test venue creation form loads."""
        response = client.get("/venues/create")
        assert response.status_code == 200

    def test_create_artist_form(self, client):
        """Test artist creation form loads."""
        response = client.get("/artists/create")
        assert response.status_code == 200

    def test_create_show_form(self, client):
        """Test show creation form loads."""
        response = client.get("/shows/create")
        assert response.status_code == 200


class TestSearch:
    """Test search functionality."""

    def test_venue_search_exact_match(self, client, sample_venue):
        """Test searching venues with exact name."""
        response = client.post("/venues/search", data={"search_term": "Test Venue"})
        assert response.status_code == 200
        assert b"Test Venue" in response.data

    def test_venue_search_partial_match(self, client, sample_venue):
        """Test searching venues with partial name (case-insensitive)."""
        response = client.post("/venues/search", data={"search_term": "test"})
        assert response.status_code == 200
        assert b"Test Venue" in response.data

    def test_venue_search_case_insensitive(self, client, sample_venue):
        """Test that search is case-insensitive."""
        response = client.post("/venues/search", data={"search_term": "TEST VENUE"})
        assert response.status_code == 200
        assert b"Test Venue" in response.data

    def test_venue_search_no_results(self, client, sample_venue):
        """Test search with no matching results."""
        response = client.post("/venues/search", data={"search_term": "Nonexistent"})
        assert response.status_code == 200
        assert b"Nonexistent" not in response.data or b"0" in response.data

    def test_artist_search_partial_match(self, client, sample_artist):
        """Test searching artists with partial name."""
        response = client.post("/artists/search", data={"search_term": "art"})
        assert response.status_code == 200
        assert b"Test Artist" in response.data


class TestShowsTimeSplit:
    """Test past vs upcoming shows distinction."""

    def test_past_shows(self, client, sample_venue, sample_artist):
        """Test that past shows are correctly identified."""
        with app.app_context():
            past_show = Show(
                venue_id=sample_venue,
                artist_id=sample_artist,
                start_time=datetime.now() - timedelta(days=30),
            )
            db.session.add(past_show)
            db.session.commit()

        response = client.get(f"/venues/{sample_venue}")
        assert response.status_code == 200
        assert b"Past" in response.data or b"past" in response.data

    def test_upcoming_shows(self, client, sample_venue, sample_artist):
        """Test that upcoming shows are correctly identified."""
        with app.app_context():
            upcoming_show = Show(
                venue_id=sample_venue,
                artist_id=sample_artist,
                start_time=datetime.now() + timedelta(days=30),
            )
            db.session.add(upcoming_show)
            db.session.commit()

        response = client.get(f"/venues/{sample_venue}")
        assert response.status_code == 200
        assert b"Upcoming" in response.data or b"upcoming" in response.data


class TestCreateOperations:
    """Test create operations."""

    def test_create_venue_directly(self, client):
        """Test creating a venue directly via model."""
        with app.app_context():
            venue = Venue(
                name="Created Venue",
                city="Austin",
                state="TX",
                address="789 Music Ave",
                phone="555-9999",
                genres="Jazz,Blues",
                facebook_link="https://facebook.com/test",
            )
            db.session.add(venue)
            db.session.commit()

            retrieved = Venue.query.filter_by(name="Created Venue").first()
            assert retrieved is not None
            assert retrieved.city == "Austin"
            assert "Jazz" in retrieved.genres

    def test_create_artist_directly(self, client):
        """Test creating an artist directly via model."""
        with app.app_context():
            artist = Artist(
                name="Created Artist",
                city="Nashville",
                state="TN",
                phone="555-8888",
                genres="Country,Folk",
                facebook_link="https://facebook.com/test",
            )
            db.session.add(artist)
            db.session.commit()

            retrieved = Artist.query.filter_by(name="Created Artist").first()
            assert retrieved is not None
            assert retrieved.city == "Nashville"
            assert "Country" in retrieved.genres

    def test_create_show_submission(self, client, sample_venue, sample_artist):
        """Test creating a show via form submission."""
        future_time = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
        response = client.post(
            "/shows/create",
            data={
                "venue_id": sample_venue,
                "artist_id": sample_artist,
                "start_time": future_time,
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            show = Show.query.filter_by(venue_id=sample_venue, artist_id=sample_artist).first()
            assert show is not None


class TestEditOperations:
    """Test edit operations."""

    def test_edit_venue_form(self, client, sample_venue):
        """Test venue edit form loads with existing data."""
        response = client.get(f"/venues/{sample_venue}/edit")
        assert response.status_code == 200
        assert b"Test Venue" in response.data

    def test_edit_artist_form(self, client, sample_artist):
        """Test artist edit form loads with existing data."""
        response = client.get(f"/artists/{sample_artist}/edit")
        assert response.status_code == 200
        assert b"Test Artist" in response.data

    def test_edit_venue_submission(self, client, sample_venue):
        """Test updating a venue."""
        response = client.post(
            f"/venues/{sample_venue}/edit",
            data={
                "name": "Updated Venue",
                "city": "San Francisco",
                "state": "CA",
                "address": "123 Test St",
                "genres": ["Rock"],
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            venue = Venue.query.get(sample_venue)
            assert venue.name == "Updated Venue"

    def test_edit_artist_submission(self, client, sample_artist):
        """Test updating an artist."""
        response = client.post(
            f"/artists/{sample_artist}/edit",
            data={
                "name": "Updated Artist",
                "city": "Los Angeles",
                "state": "CA",
                "genres": ["Jazz"],
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            artist = Artist.query.get(sample_artist)
            assert artist.name == "Updated Artist"


class TestBonusFeatures:
    """Test bonus features."""

    def test_add_availability(self, client, sample_artist):
        """Test adding availability for an artist."""
        start = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        end = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

        response = client.post(
            f"/artists/{sample_artist}/availability",
            data={"start_time": start, "end_time": end},
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            artist = Artist.query.get(sample_artist)
            assert len(artist.availability) == 1

    def test_add_album(self, client, sample_artist):
        """Test adding an album for an artist."""
        response = client.post(
            f"/artists/{sample_artist}/albums",
            data={"album_name": "New Album", "album_year": "2024"},
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            artist = Artist.query.get(sample_artist)
            assert len(artist.albums) == 1
            assert artist.albums[0].name == "New Album"

    def test_add_song(self, client, sample_artist):
        """Test adding a song to an album."""
        with app.app_context():
            album = Album(artist_id=sample_artist, name="Album for Song")
            db.session.add(album)
            db.session.commit()
            album_id = album.id

        response = client.post(
            f"/albums/{album_id}/songs",
            data={"song_name": "New Song"},
            follow_redirects=True,
        )
        assert response.status_code == 200

        with app.app_context():
            album = db.session.get(Album, album_id)
            assert len(album.songs) == 1
            assert album.songs[0].name == "New Song"

    def test_availability_restricts_show_booking(self, client, sample_venue, sample_artist):
        """Test that shows can only be booked during artist availability."""
        with app.app_context():
            # Set availability for next week only
            avail = Availability(
                artist_id=sample_artist,
                start_time=datetime.now() + timedelta(days=7),
                end_time=datetime.now() + timedelta(days=14),
            )
            db.session.add(avail)
            db.session.commit()

        # Try to book outside availability window
        outside_time = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        response = client.post(
            "/shows/create",
            data={
                "venue_id": sample_venue,
                "artist_id": sample_artist,
                "start_time": outside_time,
            },
            follow_redirects=True,
        )
        assert b"not available" in response.data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
