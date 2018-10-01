from flask import Flask, request, redirect, session, render_template, g, url_for, send_from_directory
from datetime import datetime
from werkzeug import secure_filename
import sqlite3
import hashlib
import os
import shutil
#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')

DATABASE = './db/test.db'
app = Flask(__name__)
app.secret_key = 'Myeongsin Secret Key'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def get_user(name, password):
    sql = 'SELECT * FROM users where name="{}" and password="{}"'.format(name, password)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res

def get_post():
    sql = 'SELECT idx, title, writer, date_time, data, filename FROM board ORDER BY idx DESC'
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res

def get_comment():
    sql = 'SELECT idx, data, writer, date_time, post_num FROM comments'
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res

def create_userdir(userdir):
    dirpath = "./uploads"+"/"+userdir
    if os.path.isdir(dirpath):
        print dirpath
        return dirpath
    else:
        os.mkdir(dirpath)
        return ""

def create_postdir(postdir, userdir):
    frontdir = create_userdir(userdir)
    dirpath = frontdir+"/"+str(postdir)
    if os.path.isdir(dirpath):
        print dirpath
        return dirpath
    else:
        os.mkdir(dirpath)
        return ""

def delete_userdir(userdir):
    dirpath = "./uploads"+"/"+userdir
    shutil.rmtree(dirpath)
    return ""

def delete_postdir(postdir, userdir):
    dirpath = "./uploads"+"/"+userdir+"/"+str(postdir)
    print dirpath
    shutil.rmtree(dirpath)
    return ""

@app.route('/')
def index():
    if 'name' in session:
        return render_template('logged_main.html', ID=session['name'])
    else:
        return render_template('notlogged_main.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        user_id = request.form.get('name')
        user_pw = request.form.get('password')
        hash_pw = hashlib.sha224(user_pw).hexdigest()
        ret = get_user(user_id, hash_pw)
        if len(ret) != 0:
            session['name'] = user_id
            session['password'] = hash_pw
            session['e_mail'] = ret[0][2]
            session['hp'] = ret[0][3]
            return redirect(url_for('index'))
        else:
            return '<a href="/login">Login Failed</a>'

@app.route('/logout')
def logout():
    session.pop('name', None)
    if 'name' not in session:
        return redirect(url_for('logout_page'))

@app.route('/logout_page')
def logout_page():
    return redirect(url_for('index'))

@app.route('/introduce')
def intro():
    return render_template('introduce.html')

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        print(db)
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
        db.commit()

def add_user(name, password, e_mail, hp):
    sql = 'INSERT INTO users (name, password, e_mail, hp) VALUES("{}", "{}", "{}", "{}")'.format(name, password, e_mail, hp)
    db = get_db()
    db.execute(sql)
    db.commit()

def del_user(del_name, del_password):
    ret=get_user(del_name, del_password)
    if del_password == ret[0][1]:
        sql = 'DELETE FROM users where name="{}"'.format(del_name)
        db = get_db()
        db.execute(sql)
        db.commit()
    else:
        return ""

def up_user(update_password, update_email, update_hp):
    user_id = session['name']
    password_sql = 'UPDATE users set password = "{}" where name = "{}"'.format(update_password, user_id)
    email_sql = 'UPDATE users set e_mail = "{}" where name = "{}"'.format(update_email, user_id)
    hp_sql = 'UPDATE users set hp = "{}" where name = "{}"'.format(update_hp, user_id)
    db = get_db()
    db.execute(password_sql)
    db.execute(email_sql)
    db.execute(hp_sql)
    db.commit()

def chk_id(name):
    sql = 'SELECT * FROM users where name="{}"'.format(name)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res

def add_post(title, writer, date_time, data, filename):
    sql = 'INSERT INTO board (title, writer, date_time, data, filename) VALUES("{}", "{}", "{}", "{}", "{}")'.format(title, writer, date_time, data, filename)
    db = get_db()
    db.execute(sql)
    db.commit()

def update_post(idx, title, data, filename):
    title_sql = 'UPDATE board set title = "{}" where idx = "{}"'.format(title, idx)
    data_sql = 'UPDATE board set data = "{}" where idx = "{}"'.format(data, idx)
    fileupload_sql = 'UPDATE board set filename = "{}" where idx = "{}"'.format(filename, idx)
    db = get_db()
    db.execute(title_sql)
    db.execute(data_sql)
    db.execute(fileupload_sql)
    db.commit()

def delete_post(idx):
    sql = 'DELETE FROM board where idx='+str(idx)
    db = get_db()
    db.execute(sql)
    db.commit()

def chk_post(idx):
    sql = 'SELECT * FROM board where idx='+str(idx)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res

def chk_post2(title, writer, date_time, data, filename):
    sql = 'SELECT * FROM board where title = "{}" and writer = "{}" and date_time = "{}" and data = "{}" and filename = "{}"'.format(title, writer, date_time, data, filename)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res

def add_comment(data, writer, date_time, post_num):
    sql = 'INSERT INTO comments (data, writer, date_time, post_num) VALUES ("{}", "{}", "{}", "{}")'.format(data, writer, date_time, post_num)
    db = get_db()
    db.execute(sql)
    db.commit()

def update_comment(data, idx):
    sql = 'UPDATE comments set data = "{}" where idx = "{}"'.format(data, idx)
    db = get_db()
    db.execute(sql)
    db.commit()

def delete_comment(idx):
    sql = 'DELETE FROM comments where idx='+str(idx)
    db = get_db()
    db.execute(sql)
    db.commit()

def deluser_comment(username):
    sql = 'DELETE FROM comments where writer="%s"' %(username)
    db = get_db()
    db.execute(sql)
    db.commit()

def delpost_comment(postnum):
    sql = 'DELETE FROM comments where post_num='+str(postnum)
    db = get_db()
    db.execute(sql)
    db.commit()

@app.route('/join', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('add.html')
    else:
        join_name = request.form.get('name')
        if chk_id(join_name) != []:
            return '<a href="/join">Already Existing Account!</a>'
        join_password = request.form.get('password')
        join_email = request.form.get('e_mail')
        hash_password = hashlib.sha224(join_password).hexdigest()
        join_hp = request.form.get('hp')
        add_user(join_name, hash_password, join_email, join_hp)
        create_userdir(join_name)
        return render_template('welcomejoin.html')

@app.route('/delete', methods=['GET', 'POST'])
def delete_user():
    if 'name' in session:
        if request.method == 'GET':
            return render_template('delete.html', ID=session['name'])
        else:
            del_name = request.form.get('name')
            del_password = request.form.get('password')
            hash_password = hashlib.sha224(del_password).hexdigest()
            if session['name'] == del_name and session['password'] == hash_password:
                ret=get_user(del_name, hash_password)
                if len(ret) != 0:
                    delete_userdir(session['name'])
                    #print type(session['name'])
                    deluser_comment(session['name'])
                    del_user(del_name, hash_password)
                    return '<a href="/logout">Account deleted successfully</a>'
                else:
                    return '<a href="/delete">User does not exist</a>'
            else:
                return '<a href="/delete">Re-insert ID and PASSWORD</a>'
    else:
        return redirect(url_for('index'))

@app.route('/update', methods=['GET', 'POST'])
def update_user():
    if 'name' in session:
        if request.method == 'GET':
            return render_template('update.html')
        else:
            update_password = request.form.get('password')
            hash_password = hashlib.sha224(update_password).hexdigest()
            update_email = request.form.get('e_mail')
            update_hp = request.form.get('hp')
            up_user(hash_password, update_email, update_hp)
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/board', methods=['GET', 'POST'])
def board():
    if 'name' in session:
        if request.method == 'GET':
            ret = get_post()
            return render_template('board.html', posts = ret)
    else:
        return redirect(url_for('index'))

@app.route('/write', methods=['GET', 'POST'])
def write():
    if 'name' in session:
        if request.method == 'GET':
            return render_template('write.html')
        else:
            title = request.form.get('title')
            data = request.form.get('data')
            up_file = request.form.get('filename')
            writer = session['name']
            date_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            if up_file == "":
                add_post(title, writer, date_time, data, "")
                res = chk_post2(title, writer, date_time, data, "")
                create_postdir(res[0][0], session['name'])
                #print res
                return redirect(url_for('board'))
            else:
                f = request.files['filename']
                a = str(f)
                filename = a.split("'")
                #print filename[1]
                add_post(title, writer, date_time, data, filename[1])
                res = chk_post2(title, writer, date_time, data, filename[1])
                #print res
                create_postdir(res[0][0], session['name'])
                f.save('./uploads/' + session['name'] + "/" + str(res[0][0]) + "/" + secure_filename(f.filename))
                return redirect(url_for('board'))
    else:
        return redirect(url_for('index'))

@app.route('/board_view/<idx>', methods=['GET', 'POST'])
def board_view(idx):
    if 'name' in session:
        res = chk_post(idx)
        if request.method == 'GET':
            comment = get_comment()
            #print comment
            return render_template('board_view.html', posts = res, session = session['name'], com_posts = comment)
        else:
            comment = request.form.get('comment')
            date_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            add_comment(comment, session['name'], date_time, idx)
            return redirect(url_for('board_view', idx=res[0][0]))
    else:
        return redirect(url_for('index'))

@app.route('/board_delete/<idx>', methods=['GET', 'POST'])
def board_delete(idx):
    if 'name' in session:
        res = chk_post(idx)
        writer = res[0][2]
        if session['name'] == writer:
            if request.method == 'GET':
                return render_template('board_delete.html', ID=session['name'])
            else:
                user_name = request.form.get('name')
                user_password = request.form.get('password')
                hash_password = hashlib.sha224(user_password).hexdigest()
                if session['name'] == user_name and session['password'] == hash_password:
                    delete_postdir(idx, session['name'])
                    delpost_comment(res[0][0])
                    delete_post(idx)
                    return '<a href="/board">Post deleted successfully</a>'
                else:
                    return '<a href="/board">Re-insert ID and PASSWORD</a>'
        else:
            return redirect(url_for('board'))
    else:
        return redirect(url_for('index'))

@app.route('/board_update/<idx>', methods=['GET', 'POST'])
def board_update(idx):
    if 'name' in session:
        res = chk_post(idx)
        writer = res[0][2]
        if session['name'] == writer:
            if request.method == 'GET':
                sql = 'SELECT * FROM board where idx='+str(idx)
                db = get_db()
                rv = db.execute(sql)
                res = rv.fetchall()
                #print res
                return render_template('board_update.html', posts = res)
            else:
                index = idx
                up_title = request.form.get('title')
                up_data = request.form.get('data')
                up_file = request.form.get('filename')
                if up_file == "":
                    update_post(index, up_title, up_data, "")
                    return redirect(url_for('board'))
                else:
                    f = request.files['filename']
                    f.save('./uploads/' + session['name'] + "/" + str(res[0][0]) + "/" + secure_filename(f.filename))
                    a = str(f)
                    filename = a.split("'")
                    update_post(index, up_title, up_data, filename[1])
                    return redirect(url_for('board'))
        else:
            return redirect(url_for('board'))
    else:
        return redirect(url_for('index'))

@app.route('/file_download/<idx>/<filename>', methods=['GET', 'POST'])
def download(idx, filename):
    if 'name' in session:
        res = chk_post(idx)
        writer = res[0][2]
        f_name = res[0][5]
        location = "./uploads/" + writer + "/" + str(idx) + "/"
        return send_from_directory(directory=location, filename=f_name)
    else:
        return redirect(url_for('board'))

@app.route('/comment_update/<idx>', methods=['GET', 'POST'])
def com_update(idx):
    if 'name' in session:
        sql = 'SELECT * FROM comments where idx='+str(idx)
        db = get_db()
        rv = db.execute(sql)
        res = rv.fetchall()
        if session['name'] == res[0][2]:
            if request.method == 'GET':
                return render_template('comment_update.html')
            else:
                up_comment = request.form.get('comment')
                update_comment(up_comment, idx)
                return redirect(url_for('board_view', idx=res[0][4]))
        else:
            return redirect(url_for('board'))
    else:
        return redirect(url_for('index'))

@app.route('/comment_delete/<idx>', methods=['GET', 'POST'])
def com_delete(idx):
    if 'name' in session:
        sql = 'SELECT * FROM comments where idx='+str(idx)
        db = get_db()
        rv = db.execute(sql)
        res = rv.fetchall()
        if session['name'] == res[0][2]:
            if request.method == 'GET':
                return render_template('comment_delete.html')
            else:
                user_name = request.form.get('name')
                user_password = request.form.get('password')
                hash_password = hashlib.sha224(user_password).hexdigest()
                if session['name'] == user_name and session['password'] == hash_password:
                    delete_comment(idx)
                    return redirect(url_for('board_view', idx=res[0][4]))
                else:
                    return '<a href="/board">Re-insert ID and PASSWORD</a>'
        else:
            return redirect(url_for('board'))
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    #init_db()
    app.run(debug=True, port=8080, host='0.0.0.0')
