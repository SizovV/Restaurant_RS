import sqlite3 as sql

from app import app
from flask import render_template, request
from datetime import datetime

# connect to qa_database.sq  (database will be created, if not exist)
con = sql.connect('qa_database2.db')
con.execute('CREATE TABLE IF NOT EXISTS tbl_QA (ID INTEGER PRIMARY KEY AUTOINCREMENT,'
            + 'title TEXT, titledisc TEXT,  post TEXT, datetime timestamp, imagepath TEXT);')
con.close()


# home page
@app.route('/')  # root : main page
def index():
    # by default, 'render_template' looks inside the folder 'template'
    return render_template('index.html')


# Create question
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        # send the form
        return render_template('create.html')
    else: # request.method == 'POST':
        # read data from the form and save in variable
        title = request.form['title']
        post = request.form['post']

        titledisc = request.form['titledesc']
        if title and post and titledisc:
            # store in database
            try:
                con = sql.connect('qa_database2.db')
                c = con.cursor()  # cursor
                timepoint = datetime.now()
                # insert data
                c.execute("INSERT INTO tbl_QA (title, titledisc, post, datetime) VALUES (?,?,?,?);",
                    (title, titledisc, post, timepoint))
                con.commit() # apply changes
                # go to thanks page
                return render_template('createthanks.html')
            except con.Error as err: # if error
                # then display the error in 'database_error.html' page
                return render_template('database_error.html', error=err)
            finally:
                con.close() # close the connection
        else:
            return render_template('sorry.html')

# Display question
@app.route('/question', methods=['GET', 'POST'])
def question():
    #if request.method == 'GET':
        # send the form
        # code to read the question from database
        try:
            con = sql.connect('qa_database2.db')
            c = con.cursor()  # cursor
            # read question : SQLite index start from 1 (see index.html)
            query = "Select title, titledisc, post, datetime, imagepath FROM tbl_QA;"
            c.execute(query)
            info = c.fetchall()  # fetch the data from cursor
            con.commit()  # apply changess]
            return render_template('question.html', posts=info)
        except con.Error as err: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=err)
        finally:
            con.close() # close the connection

        #return render_template('question.html', posts=info)

