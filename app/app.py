from typing import List, Dict
import simplejson as json
import os
from flask import Flask, request, Response, redirect, url_for, session, flash
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
from flask_mail import Mail, Message


app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)
app.secret_key = "123456"

app.config['SECRET_KEY'] = 'top-secret!'
app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = "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"
app.config['MAIL_DEFAULT_SENDER'] = 'vinayb004@gmail.com'
mail = Mail(app)

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'homesData'

mysql.init_app(app)

db = MySQL(app)

@app.route('/send', methods=['GET', 'POST'])
def send_grid():
    return render_template('sendgrid.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/team')
def team_page():
    return render_template('team.html')

@app.route('/login', methods=['GET', 'POST'])
def login_check():
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            cursor = mysql.get_db().cursor()
            cursor.execute("SELECT * FROM tblloginImport WHERE email=%s AND password=%s", (username, password))
            info = cursor.fetchone()
            if info is not None:
                if info['email'] == username and info['password'] == password:
                    session['loginsuccess'] = True
                    return redirect(url_for("home_page"))
            else:
                return redirect(url_for("login_check"))

    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def new_user():
    if request.method == "POST":
        recipient = request.form['two']
        msg = Message('Thanks for signing up to Homes!', recipients=[recipient])
        msg.body = ('To login, please click here: '
                    'localhost:5000')
        msg.html = ('<h1>Thanks for signing up to Homes!</h1>'
                    '<p>To login, please click here: '
                    '<a clicktracking="off" href="http://localhost:5000/login">http://localhost:5000/login</a></p>')
        mail.send(msg)
        flash(f'An email was sent to {recipient}. Please verify your email to login.')
        if "one" in request.form and "two" in request.form and "three" in request.form:
            username = request.form['one']
            email = request.form['two']
            password = request.form['three']
            cursor = mysql.get_db().cursor()
            cursor.execute('INSERT INTO tblloginImport(name, email, password)VALUES(%s,%s,%s)', (username, email, password))
            mysql.get_db().commit()
            return redirect(url_for('send_grid'))
    return render_template("register.html")

@app.route('/homepage', methods=['GET'])
def home_page():
    if session['loginsuccess'] == True:
        user = {'username': 'Your'}
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT * FROM tblhomesImport')
        result = cursor.fetchall()
        return render_template('dblist.html', title='Home', user=user, homes=result)

@app.route('/logout')
def logout():
    session.pop('loginsuccess',None)
    return redirect(url_for('index'))

@app.route('/view/<int:home_id>', methods=['GET'])
def record_view(home_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblhomesImport WHERE id=%s', home_id)
    result = cursor.fetchall()
    return render_template('view.html', title='View Form', home=result[0])


@app.route('/edit/<int:home_id>', methods=['GET'])
def form_edit_get(home_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblhomesImport WHERE id=%s', home_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Edit Form', home=result[0])


@app.route('/edit/<int:home_id>', methods=['POST'])
def form_update_post(home_id):
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Sell'), request.form.get('List'), request.form.get('Living'),
                 request.form.get('Rooms'), request.form.get('Beds'),
                 request.form.get('Baths'), request.form.get('Age'), request.form.get('Acres'),
                 request.form.get('Taxes'), home_id)
    sql_update_query = """UPDATE tblhomesImport t SET t.Sell = %s, t.List = %s, t.Living = %s, t.Rooms = 
    %s, t.Beds = %s, t.Baths = %s, t.Age = %s, t.Acres = %s, t.Taxes = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/homes/new', methods=['GET'])
def form_insert_get():
    return render_template('new.html', title='New Homes Form')


@app.route('/homes/new', methods=['POST'])
def form_insert_post():
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Sell'), request.form.get('List'), request.form.get('Living'),
                 request.form.get('Rooms'), request.form.get('Beds'),
                 request.form.get('Baths'), request.form.get('Age'), request.form.get('Acres'),
                 request.form.get('Taxes'))
    sql_insert_query = """INSERT INTO tblhomesImport (Sell, List, Living, Rooms, Beds, Baths, Age, Acres, Taxes) VALUES (%s, %s,%s, %s,%s, %s,%s, %s, %s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/delete/<int:home_id>', methods=['POST'])
def form_delete_post(home_id):
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblhomesImport WHERE id = %s """
    cursor.execute(sql_delete_query, home_id)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/api/v1/homes', methods=['GET'])
def api_browse() -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblhomesImport')
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/homes/<int:home_id>', methods=['GET'])
def api_retrieve(home_id) -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblhomesImport WHERE id=%s', home_id)
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/homes/<int:home_id>', methods=['PUT'])
def api_edit(home_id) -> str:
    cursor = mysql.get_db().cursor()
    content = request.json
    inputData = (content['Sell'], content['List'], content['Living'],
                 content['Rooms'], content['Beds'],
                 content['Baths'], content['Age'], content['Acres'], content['Taxes'], home_id)
    sql_update_query = """UPDATE tblhomesImport t SET t.Sell = %s, t.List = %s, t.Living = %s, t.Rooms = 
    %s, t.Beds = %s, t.Baths = %s, t.Age = %s, t.Acres = %s, t.Taxes = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/homes', methods=['POST'])
def api_add() -> str:
    content = request.json
    cursor = mysql.get_db().cursor()
    inputData = (content['Sell'], content['List'], content['Living'],
                 content['Rooms'], content['Beds'],
                 content['Baths'], content['Age'], content['Acres'], request.form.get('Taxes'))
    sql_insert_query = """INSERT INTO tblhomesImport (Sell,List,Living,Rooms,Beds,Baths,Age,Acres,Taxes) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=201, mimetype='application/json')
    return resp


@app.route('/api/v1/homes/<int:home_id>', methods=['DELETE'])
def api_delete(home_id) -> str:
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblhomesImport WHERE id = %s """
    cursor.execute(sql_delete_query, home_id)
    mysql.get_db().commit()
    resp = Response(status=210, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
