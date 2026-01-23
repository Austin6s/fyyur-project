Fyyur
-----

## Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.

## Overview

This is a fully functioning venue and artist booking site powered by a PostgreSQL database. The application supports:

* Creating, reading, updating, and deleting venues and artists
* Creating shows that link artists to venues
* Searching for venues and artists (case-insensitive, partial string matching)
* Viewing detailed information about specific artists or venues
* Distinguishing between past and upcoming shows

### Bonus Features Implemented

* **Artist Availability**: Artists can set available time windows for bookings
* **Recent Listings**: Homepage displays the 10 most recently listed venues and artists
* **Discography Management**: Artists can add albums and songs to their profile

## Tech Stack (Dependencies)

### 1. Backend Dependencies
Our tech stack will include the following:
 * **virtualenv** as a tool to create isolated Python environments
 * **SQLAlchemy ORM** to be our ORM library of choice
 * **PostgreSQL** as our database of choice
 * **Python3** and **Flask** as our server language and server framework
 * **Flask-Migrate** for creating and running schema migrations
You can download and install the dependencies mentioned above using `pip` as:
```
pip install virtualenv
pip install SQLAlchemy
pip install postgres
pip install Flask
pip install Flask-Migrate
```
> **Note** - If we do not mention the specific version of a package, then the default latest stable package will be installed. 

### 2. Frontend Dependencies
You must have the **HTML**, **CSS**, and **Javascript** with [Bootstrap 3](https://getbootstrap.com/docs/3.4/customize/) for our website's frontend. Bootstrap can only be installed by Node Package Manager (NPM). Therefore, if not already, download and install the [Node.js](https://nodejs.org/en/download/). Windows users must run the executable as an Administrator, and restart the computer after installation. After successfully installing the Node, verify the installation as shown below.
```
node -v
npm -v
```
Install [Bootstrap 3](https://getbootstrap.com/docs/3.3/getting-started/) for the website's frontend:
```
npm init -y
npm install bootstrap@3
```


## Main Files: Project Structure

  ```sh
  ├── README.md
  ├── app.py *** the main driver of the app. Includes your SQLAlchemy models.
                    "python app.py" to run after installing dependencies
  ├── config.py *** Database URLs, CSRF generation, etc
  ├── error.log
  ├── forms.py *** Your forms
  ├── requirements.txt *** The dependencies we need to install with "pip3 install -r requirements.txt"
  ├── static
  │   ├── css 
  │   ├── font
  │   ├── ico
  │   ├── img
  │   └── js
  └── templates
      ├── errors
      ├── forms
      ├── layouts
      └── pages
  ```

Overall:
* Models are located in the `MODELS` section of `app.py`.
* Controllers are also located in `app.py`.
* The web frontend is located in `templates/`, which builds static assets deployed to the web server at `static/`.
* Web forms for creating data are located in `form.py`


Highlight folders:
* `templates/pages` -- Defines the pages that are rendered to the site. These templates render views based on data passed into the template's view, in the controllers defined in `app.py`.
* `templates/layouts` -- Defines the layout that a page can be contained in to define footer and header code for a given page.
* `templates/forms` -- Defines the forms used to create new artists, shows, and venues.
* `app.py` -- Defines routes that match the user's URL, and controllers which handle data and renders views to the user. Contains all models and database interactions.
* Models in `app.py` -- Defines the data models (Venue, Artist, Show, Availability, Album, Song) that set up the database tables.
* `config.py` -- Stores configuration variables including the PostgreSQL database connection string.


Implementation Complete
-----

All functionality has been implemented:

1. **Database Connection** - PostgreSQL database configured in `config.py`
2. **Models** - Venue, Artist, Show, Availability, Album, and Song models with proper relationships
3. **Create Operations** - Form submissions for creating venues, artists, and shows with validation
4. **Read Operations** - Listing venues (grouped by city/state), artists, and shows with real data
5. **Search** - Case-insensitive partial string matching for venues and artists
6. **Detail Pages** - Venue and artist pages showing past vs upcoming shows
7. **Edit/Delete** - Update and delete functionality for venues and artists (with cascade delete)

#### Data Handling with `Flask-WTF` Forms
The starter codes use an interactive form builder library called [Flask-WTF](https://flask-wtf.readthedocs.io/). This library provides useful functionality, such as form validation and error handling. You can peruse the Show, Venue, and Artist form builders in `forms.py` file. The WTForms are instantiated in the `app.py` file. For example, in the `create_shows()` function, the Show form is instantiated from the command: `form = ShowForm()`. To manage the request from Flask-WTF form, each field from the form has a `data` attribute containing the value from user input. For example, to handle the `venue_id` data from the Venue form, you can use: `show = Show(venue_id=form.venue_id.data)`, instead of using `request.form['venue_id']`.

Acceptance Criteria
-----

1. The web app should be successfully connected to a PostgreSQL database. A local connection to a database on your local computer is fine.
2. There should be no use of mock data throughout the app. The data structure of the mock data per controller should be kept unmodified when satisfied by real data.
3. The application should behave just as before with mock data, but now uses real data from a real backend server, with real search functionality. For example:
  * when a user submits a new artist record, the user should be able to see it populate in /artists, as well as search for the artist by name and have the search return results.
  * I should be able to go to the URL `/artist/<artist-id>` to visit a particular artist’s page using a unique ID per artist, and see real data about that particular artist.
  * Venues should continue to be displayed in groups by city and state.
  * Search should be allowed to be partial string matching and case-insensitive.
  * Past shows versus Upcoming shows should be distinguished in Venue and Artist pages.
  * A user should be able to click on the venue for an upcoming show in the Artist's page, and on that Venue's page, see the same show in the Venue Page's upcoming shows section.
4. As a fellow developer on this application, I should be able to run `flask db migrate`, and have my local database (once set up and created) be populated with the right tables to run this application and have it interact with my local postgres server, serving the application's needs completely with real data I can seed my local database with.
  * The models are complete in the `Models` section of `app.py` and model all objects used throughout Fyyur.
  * Define the models in a different file to follow [Separation of Concerns](https://en.wikipedia.org/wiki/Separation_of_concerns) design principles. You can refactor the models to a new file, such as `models.py`.
  * The right _type_ of relationship and parent-child dynamics between models should be accurately identified and fit the needs of this particular application.
  * The relationship between the models should be accurately configured, and referential integrity amongst the models should be preserved.
  * `flask db migrate` should work, and populate my local postgres database with properly configured tables for this application's objects, including proper columns, column data types, constraints, defaults, and relationships that completely satisfy the needs of this application. The proper type of relationship between venues, artists, and shows should be configured.

##### Stand Out Features (Implemented)

The following bonus features have been implemented:

* **Artist Availability** - Artists can add availability windows specifying when they can be booked. Managed via the artist detail page.
* **Recent Listings** - Homepage displays the 10 most recently created venues and artists.
* **Discography** - Artists can add albums (with optional year) and songs to their profile.


## Development Setup
1. **Download the project starter code locally**
```
git clone https://github.com/udacity/FSND.git
cd FSND/projects/01_fyyur/starter_code 
```

2. **Create an empty repository in your Github account online. To change the remote repository path in your local repository, use the commands below:**
```
git remote -v 
git remote remove origin 
git remote add origin <https://github.com/<USERNAME>/<REPO_NAME>.git>
git branch -M master
```
Once you have finished editing your code, you can push the local repository to your Github account using the following commands.
```
git add . --all   
git commit -m "your comment"
git push -u origin master
```

3. **Initialize and activate a virtualenv using:**
```
python -m virtualenv env
source env/bin/activate
```
>**Note** - In Windows, the `env` does not have a `bin` directory. Therefore, you'd use the analogous command shown below:
```
source env/Scripts/activate
```

4. **Install the dependencies:**
```
pip install -r requirements.txt
```

5. **Run the development server:**
```
export FLASK_APP=myapp
export FLASK_ENV=development # enables debug mode
python3 app.py
```

6. **Verify on the Browser**<br>
Navigate to project homepage [http://127.0.0.1:5000/](http://127.0.0.1:5000/) or [http://localhost:5000](http://localhost:5000) 

## Troubleshooting:
- If you encounter any dependency errors, please ensure that you are using Python 3.9 or lower.
- If you are still facing the dependency errors, follow the given commands:
  - `using pip install --upgrade flask-moment`
  - `Using pip install Werkzeug==2.0.0`
  - `Using pip uninstall Flask and then pip install flask==2.0.3`
