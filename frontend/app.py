from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create():
    name = request.form['name']
    email = request.form['email']
    response = requests.post('http://localhost:8000/users/', json={'name': name, 'email': email})
    return redirect(url_for('index'))

@app.route('/update', methods=['POST'])
def update():
    user_id = request.form['id']
    name = request.form['name']
    email = request.form['email']
    requests.put(f'http://localhost:8000/users/{user_id}', json={'id': user_id, 'name': name, 'email': email})
    return redirect(url_for('index'))

@app.route('/delete/<int:user_id>')
def delete(user_id):
    requests.delete(f'http://localhost:8000/users/{user_id}')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)