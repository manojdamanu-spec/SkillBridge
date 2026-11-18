# SkillBridge

**Tagline:** Connect Your Skills. Discover Opportunities. Build Your Future.

SkillBridge is a student platform that helps students:
- Create a profile and list technical skills.
- Find sample projects that match their skills.
- Discover other students and the skills they have shared.
- Learn about the platform and contact the project team.

## Technology used

- HTML - page structure
- CSS - design and responsive layout
- JavaScript - navigation menu and student search
- Python Flask - backend routes and application logic
- Flask-SQLAlchemy - database connection
- SQLite - default local database
- PostgreSQL / Supabase - optional hosted database

## 1. Install Python

Install Python 3.10 or newer. Check it in a terminal:

```bash
python --version
```

## 2. Open the project folder

Open a terminal inside the `skillbridge` folder.

## 3. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Install the required packages

```bash
pip install -r requirements.txt
```

## 5. Run the website

```bash
python app.py
```

Open this address in your browser:

```text
http://127.0.0.1:5000
```

The app creates a local SQLite database named `skillbridge.db` automatically and inserts sample projects the first time it runs.

## How project matching works

1. A student saves skills in their profile, separated by commas.
2. Each sample project has a list of required skills.
3. Python compares the student's skills with the project's required skills.
4. The match percentage is:

```text
(number of matched skills / total required skills) * 100
```

This is a simple rule-based matching system, not an AI model.

## Use Supabase PostgreSQL later

The app uses SQLite by default because it is easy to run while learning. To switch to Supabase:

1. Create a Supabase project.
2. Open its database connection details and copy the PostgreSQL connection string.
3. Set the `DATABASE_URL` environment variable to that connection string.
4. Make sure the URL starts with `postgresql://`.
5. Restart the Flask app.

Example environment variable:

Windows PowerShell:

```powershell
$env:DATABASE_URL="postgresql://username:password@host:5432/postgres"
python app.py
```

macOS / Linux:

```bash
export DATABASE_URL="postgresql://username:password@host:5432/postgres"
python app.py
```

Do not publish your database password or secret keys in GitHub.

## Important before competition submission

- Replace the sample contact email on the Contact page.
- Add the official RIT, CSE Department and GDG on Campus logos supplied by the organizers.
- Add the organizer logos without stretching or changing them.
- Test registration, login, profile saving, project matching and student search.
- Change the default `SECRET_KEY` before public deployment.
- Use HTTPS and a production hosting setup; do not deploy with Flask debug mode enabled.
- Add your team details and screenshots to this README.

## Folder structure

```text
skillbridge/
│
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── projects.html
│   ├── team_finder.html
│   ├── about.html
│   └── contact.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```


## Sample student accounts

On the first run, SkillBridge automatically adds 8 fictional demo student profiles. They appear in Team Finder. These are sample records, not real students.

All demo accounts use this password: `Student@123`

Example login: `aarav.demo@example.com`

You can also register your own account. Demo students are added only when their email is not already in the database.


## New collaboration features
- Send a partnership request from Find Teammates.
- Open My Requests to accept or reject incoming partnership requests.
- Send a request to join a project from Find Projects.
- Students who own a project can accept or reject requests to join it.
- My Requests also shows the status of requests you have sent.

The included demo projects are owned by the fictional demo account Aarav Sharma (`aarav.demo@example.com`, password `Student@123`) so you can test the project request and acceptance flow.

If you are replacing an older copy of SkillBridge, back up any data you need first. The updated database adds new request tables and a project owner field. For a fresh demo setup, remove the old `instance/skillbridge.db` (if it exists) before starting the updated app; the sample students and projects will be created again.
