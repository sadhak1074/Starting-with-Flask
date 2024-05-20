from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Set your MySQL root password here
app.config['MYSQL_DB'] = 'managementapp'

mysql = MySQL(app)

# Create a table if it does not exist
try:
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS tasks (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        completed BOOLEAN DEFAULT FALSE
                    )""")
        cur.close()
        mysql.connection.commit()
except MySQLdb.Error as e:
    print(f"Error creating tasks table: {e}")

# Route to display form, add a new task, and list existing tasks
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tasks (title, description) VALUES (%s, %s)", (title, description))
        mysql.connection.commit()
        cur.close()
        flash('Task added successfully!')
        return redirect(url_for('index'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, description, completed FROM tasks")
    tasks = cur.fetchall()
    cur.close()
    return render_template('index.html', tasks=tasks)

# Route to render a form for updating a task
@app.route('/update_task/<int:task_id>', methods=['GET'])
def update_task_form(task_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title, description, completed FROM tasks WHERE id = %s", (task_id,))
    task = cur.fetchone()
    cur.close()
    return render_template('update_task.html', task=task)

# Route to update a task
@app.route('/update_task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    title = request.form['title']
    description = request.form['description']
    completed = request.form.get('completed') == 'on'

    cur = mysql.connection.cursor()
    cur.execute("UPDATE tasks SET title=%s, description=%s, completed=%s WHERE id=%s",
                (title, description, completed, task_id))
    mysql.connection.commit()
    cur.close()
    flash('Task updated successfully!')
    return redirect(url_for('index'))

# Route to delete a task
@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    mysql.connection.commit()
    cur.close()
    flash('Task deleted successfully!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
