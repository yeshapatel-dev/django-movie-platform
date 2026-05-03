# 🎬 Movie Management System

A Django-based web application designed to manage and explore movie data with role-based access control. The system allows users to browse movies, view detailed information, and interact through reviews, while administrators manage platform content.

---

## 🚀 Features

### 👤 User Side

* Browse all movies from homepage
* View detailed movie information (description, cast, director, reviews)
* Explore people (actors, directors, writers) and their related work
* Filter movies by year and genre
* Search functionality
* Add reviews to movies

### 🛠️ Admin Side

* Add and manage movies
* Add and manage people (actors, directors, writers)
* Control platform content via role-based access

---

## 🧠 Tech Stack

* **Backend:** Django
* **Database:** SQLite
* **Frontend:** HTML, CSS (Django Templates)

---

## 🎯 Project Focus

This project focuses mainly on:

* Backend development using Django
* Database relationships and data modeling
* Role-based authentication and authorization

---

## 🔮 Future Improvements

* Add movie streaming links (OTT-style integration)
* Build REST APIs using Django REST Framework
* Improve UI/UX
* Deploy as a production-ready system

---

## ⚙️ Setup Instructions

```bash
# Clone repository
git clone https://github.com/yeshapatel-dev/django-movie-platform.git

# Navigate to project
cd movie_management_system

# Create virtual environment
python -m venv venv

# Activate venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

---

## 📌 Note

This project was built as a practice project to strengthen Django backend concepts and can be extended into a production-level application.
