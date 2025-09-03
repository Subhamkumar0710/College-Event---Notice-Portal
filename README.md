# College Event & Notice Portal

A web application for managing and sharing college events and notices. Built with **Flask** and **SQLite**, this portal allows administrators to post and manage events/notices, while students can view and search for relevant information.

---

### Reach Out
If you have questions, suggestions, or just want to connect, feel free to reach out to me on [LinkedIn](https://www.linkedin.com/in/subham-kumar-056466275/).

---


## Features

- **User Authentication:** Registration and login for students and admin.
- **Admin Dashboard:** Add, edit, and delete events and notices.
- **Event & Notice Management:** Create, update, and remove events/notices.
- **Search Functionality:** Search events and notices by title, department, or date.
- **Role-Based Access:** Admins have special privileges; students have limited access.
- **Profile Management:** Users can update their profile details.
- **Flash Messages:** User feedback for actions and errors.

---

## Technology Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Database:** SQLite
- **Frontend:** HTML (Jinja2 templates), CSS (custom or framework), JavaScript (optional)
- **Authentication:** Flask session

---

## Getting Started

### 1. Clone the repository

```sh
git clone https://github.com/yourusername/College-Event---Notice-Portal.git
cd College-Event---Notice-Portal
```

### 2. Create a virtual environment and activate it

```sh
python -m venv env
env\Scripts\activate   # On Windows
# or
source env/bin/activate  # On Linux/Mac
```

### 3. Install dependencies

```sh
pip install -r requirements.txt
```

### 4. Run the application

```sh
python app.py
```

### 5. Access the portal

Open your browser and go to: [http://127.0.0.1:5000](http://127.0.0.1:5000)


---

## Project Structure

```
app.py
requirements.txt
templates/
    *.html
static/
    (optional CSS/JS files)
instance/
    groceri.db
```

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for suggestions or bug reports.

---

## License

This project is for educational