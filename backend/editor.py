#backend.py=
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str

# Membuat koneksi ke database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Membuat tabel user jika belum ada
@app.on_event("startup")
def startup():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

# Root
@app.get("/")
def read_root():
    return {"message": "Welcome to the User Management API"}

# Create User
@app.post("/users/")
def create_user(user: User):
    conn = get_db_connection()
    conn.execute('INSERT INTO users (name, email) VALUES (?, ?)', (user.name, user.email))
    conn.commit()
    conn.close()
    return {"message": "User created successfully"}

# Read User
@app.get("/users/{user_id}")
def read_user(user_id: int):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return {"id": user["id"], "name": user["name"], "email": user["email"]}
    raise HTTPException(status_code=404, detail="User not found")

# Update User
@app.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    conn = get_db_connection()
    conn.execute('UPDATE users SET name = ?, email = ? WHERE id = ?', (user.name, user.email, user_id))
    conn.commit()
    conn.close()
    return {"message": "User updated successfully"}

# Delete User
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return {"message": "User deleted successfully"}

#frontend/app.py=
from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

@app.route('/')
def index():
    response = requests.get('http://localhost:8000/users/')
    users = response.json()  # Pastikan ini mengembalikan data yang diharapkan
    print(users) # debug
    return render_template('index.html', users=users)

@app.route('/create', methods=['POST'])
def create():
    name = request.form['name']
    email = request.form['email']
    requests.post('http://localhost:8000/users/', json={'name': name, 'email': email})
    return redirect(url_for('index'))

@app.route('/update', methods=['POST'])
def update():
    user_id = request.form['id']
    name = request.form['name']
    email = request.form['email']
    requests.put(f'http://localhost:8000/users/{user_id}', json={'name': name, 'email': email})
    return redirect(url_for('index'))

@app.route('/delete/<int:user_id>')
def delete(user_id):
    requests.delete(f'http://localhost:8000/users/{user_id}')
    return redirect(url_for('index'))

#frontend/templates/index.html = 
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User CRUD</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="mb-4">User CRUD Operations</h1>
        <div class="mb-3">
            <form action="/create" method="post" class="row g-3">
                <div class="col-auto">
                    <input type="text" name="name" placeholder="Name" class="form-control">
                </div>
                <div class="col-auto">
                    <input type="email" name="email" placeholder="Email" class="form-control">
                </div>
                <div class="col-auto">
                    <button type="submit" class="btn btn-primary mb-3">Create User</button>
                </div>
            </form>
        </div>
        <ul class="list-group">
            {% for user in users %}
            <li class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        {{ user.name }} - {{ user.email }}
                    </div>
                    <div>
                        <form action="/update" method="post" class="d-inline">
                            <input type="hidden" name="id" value="{{ user.id }}">
                            <input type="text" name="name" value="{{ user.name }}" class="form-control d-inline-block" style="width: auto;">
                            <input type="email" name="email" value="{{ user.email }}" class="form-control d-inline-block" style="width: auto;">
                            <button type="submit" class="btn btn-sm btn-warning">Update</button>
                        </form>
                        <a href="/delete/{{ user.id }}" class="btn btn-sm btn-danger">Delete</a>
                    </div>
                </div>
            </li>
            {% endfor %}
        </ul>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>