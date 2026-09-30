from flask import Flask, jsonify, request
import json
import os
import mysql.connector
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'db')
DB_USER = os.getenv('DB_USER', 'appuser')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME', 'appdb')
METEOSOURCE_API_KEY = os.getenv('METEOSOURCE_API_KEY')

def get_connection():
	return mysql.connector.connect(
		host=DB_HOST,
		user=DB_USER,
		password=DB_PASSWORD,
		database=DB_NAME,
	)

@app.get('/api/healthz')
def healthz():
	return {'status': 'ok'}, 200

@app.get('/api/readyz')
def readyz():
	return {'status': 'ok'}, 200

@app.get('/api')
def index():
    return jsonify(message='Todo API version 1.0.1')

@app.get('/api/weather')
def get_weather():
	if not METEOSOURCE_API_KEY:
		return jsonify(error='weather service is not configured'), 503

	params = urlencode({
		'place_id': 'oulu',
		'sections': 'current',
		'units': 'metric',
		'key': METEOSOURCE_API_KEY,
	})

	try:
		with urlopen(
			f'https://www.meteosource.com/api/v1/free/point?{params}',
			timeout=10,
		) as response:
			return jsonify(json.loads(response.read()))
	except (HTTPError, URLError, TimeoutError, ValueError):
		return jsonify(error='weather service request failed'), 502

@app.get('/api/todos')
def get_todos():
	conn = get_connection()
	cur = conn.cursor(dictionary=True)
	cur.execute('SELECT id, title, completed FROM todos ORDER BY id DESC')
	todos = cur.fetchall()
	cur.close()
	conn.close()
	return jsonify(todos)

@app.post('/api/todos')
def create_todo():
	data = request.get_json(silent=True) or {}
	title = str(data.get('title', '')).strip()

	if not title:
		return jsonify(error='title is required'), 400
	if len(title) > 255:
		return jsonify(error='title is too long'), 400

	conn = get_connection()
	cur = conn.cursor()
	cur.execute('INSERT INTO todos (title) VALUES (%s)', (title,))
	conn.commit()
	todo_id = cur.lastrowid
	cur.close()
	conn.close()
	return jsonify(id=todo_id, title=title, completed=False), 201

@app.patch('/api/todos/<int:todo_id>')
def toggle_todo(todo_id):
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		'UPDATE todos SET completed = NOT completed WHERE id = %s',
		(todo_id,),
	)
	conn.commit()
	updated = cur.rowcount
	cur.close()
	conn.close()

	if not updated:
		return jsonify(error='todo not found'), 404
	return jsonify(message='todo updated')

@app.delete('/api/todos/<int:todo_id>')
def delete_todo(todo_id):
	conn = get_connection()
	cur = conn.cursor()
	cur.execute('DELETE FROM todos WHERE id = %s', (todo_id,))
	conn.commit()
	deleted = cur.rowcount
	cur.close()
	conn.close()

	if not deleted:
		return jsonify(error='todo not found'), 404
	return '', 204


if __name__ == '__main__':
	# Dev-only fallback
	app.run(host='0.0.0.0', port=8000, debug=True)
