import sqlite3 as sql
import pandas as pd
from get_recommendations import get_recommendations, get_friends
import os
from app import app
from flask import render_template, request, jsonify
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import SelectField

con = sql.connect('rest_database.db')
con.execute('CREATE TABLE IF NOT EXISTS tbl_RS (Restaurant TEXT, rate TEXT,'
            + ' datetime timestamp, usubject TEXT, PRIMARY KEY (usubject, Restaurant));')
con.close()

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
class Form(FlaskForm):
    city = SelectField('city', choices=pd.read_csv("out.csv").sort_values('Name').Name.unique().tolist())
    rate = SelectField('rate', choices=[(0, ""),(1, '1'),(2, '2'),(3, '3'),(4, '4'),(5, '5')])


# home page
@app.route('/', methods=['GET', 'POST'])  # root : main page
def index():

    if request.method == 'GET':
        form = Form()
        df = pd.read_csv("out.csv")
        df["Name"] = df['Name'] + " on " + df["Street Address"]
        country = df.sort_values('Name').Name.unique().tolist()

        return render_template('index.html', form=form, country=country)
    else:
        restaurant = request.form['Restaurant']
        rate = request.form['Rate']
        name = request.form['myname'].capitalize()
        try:
            con1 = sql.connect('rest_database.db')
            c = con1.cursor()  # cursor
            timepoint = datetime.now()
            # insert data
            c.execute("INSERT OR REPLACE INTO tbl_RS (Restaurant, rate, datetime, usubject) VALUES (?,?,?,?);",
                      (restaurant, rate, timepoint, name))
            con1.commit()  # apply changes
            # go to thanks page

            return render_template('createthanks.html')
        except con1.Error as err: # if error
                # then display the error in 'database_error.html' page
                return render_template('database_error.html', error=err)
        finally:
                con1.close() # close the connection

# Create rating for special customer
@app.route('/rate', methods=['GET', 'POST'])
def rate():
    if request.method == 'GET':
        form = Form()
        country = pd.read_csv("out.csv").sort_values('Name').Name.unique().tolist()
        return render_template('rate.html', form=form, country=country)
    else:
        restaurant = request.form['Restaurant']
        rate =  request.form['Rate']
        name = request.form['myname'].capitalize()

        try:
            con1 = sql.connect('rest_database.db')
            c = con1.cursor()  # cursor
            timepoint = datetime.now()
            # insert data
            c.execute("INSERT OR REPLACE INTO tbl_RS (Restaurant, rate, datetime, usubject) VALUES (?,?,?,?);",
                      (restaurant, rate, timepoint, name))
            con1.commit()  # apply changes
            # go to thanks page

            return render_template('createthanks.html')
        except con1.Error as err: # if error
                # then display the error in 'database_error.html' page
                return render_template('database_error.html', error=err)
        finally:
                con1.close() # close the connection


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
        name = request.form['myname'].capitalize()
        if title and post and titledisc:
            # store in database
            try:
                con1 = sql.connect('qa_database.db')
                c = con1.cursor()  # cursor
                timepoint = datetime.now()
                # insert data
                c.execute("INSERT OR REPLACE INTO tbl_QA (title, titledisc, post, datetime, aname) VALUES (?,?,?,?,?);",
                    (title, titledisc, post, timepoint, name))
                con1.commit() # apply changes
                # go to thanks page
                return render_template('createthanks.html')
            except con1.Error as err: # if error
                # then display the error in 'database_error.html' page
                return render_template('database_error.html', error=err)
            finally:
                con1.close() # close the connection
        else:
            return render_template('sorry.html')


# Display rates
@app.route('/rates', methods=['GET', 'POST'])
def rates():
    #if request.method == 'GET':
        # send the form
        # code to read the question from database
        try:
            con = sql.connect('rest_database.db')
            c = con.cursor()  # cursor
            # read question : SQLite index start from 1 (see index.html)
            query = "Select Restaurant, rate, datetime, usubject FROM tbl_RS;"
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


@app.route('/rates/<name>', methods=['GET', 'POST'])
def ratesbyname(name):
    #if request.method == 'GET':
        # send the form
        # code to read the question from database
        try:
            con = sql.connect('rest_database.db')
            c = con.cursor()  # cursor
            # read question : SQLite index start from 1 (see index.html)
            query = f"Select Restaurant, rate, datetime, usubject FROM tbl_RS where usubject like '{name.capitalize()}';"
            c.execute(query)
            info = c.fetchall()  # fetch the data from cursor
            con.commit()  # apply changess]
            #d = {'rate':[], 'restaurant': []}

            all_rec = pd.concat([get_recommendations(rates[0], int(rates[1])) for rates in info], ignore_index=True)
            all_rec = all_rec.groupby('restaurant', as_index=False).sum().sort_values('rate', ascending=False)
            #for rates in info:

            all_rec['rate'] = all_rec['rate'] / all_rec['rate'].abs().max()
            #    all_rec = pd.concat([all_rec, get_recommendations(rates[0], rates[1])])

            all_rec = pd.concat([all_rec, get_friends(name)], ignore_index=True)
            all_rec = all_rec.groupby('restaurant', as_index=False).sum().sort_values('rate', ascending=False)
            print(all_rec)

            return render_template('ratingid.html', posts=info, uniqname=name, recomendations=all_rec.restaurant)
        except con.Error as err: # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=err)
        finally:
            con.close() # close the connection

        #return render_template('question.html', posts=info)
