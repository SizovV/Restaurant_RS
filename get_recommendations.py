import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from flask import render_template, request, jsonify
from sklearn.metrics.pairwise import linear_kernel
import sqlite3 as sql


### Function that gives us the most similar restaurants
def get_recommendations(name, rate=0):
    df = pd.read_csv("out.csv")
    df.Comments = df.Comments.fillna('')
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df.Comments)
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    indices = pd.Series(df.index, index=df.Name).drop_duplicates()
    ### Index of the restaurant which matches the name
    idx = indices[name]

    ### Get the pairwise similarity
    sim_scores = list(enumerate(cosine_sim[idx]))

    ### Sort the restaurants based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    ### Get the similarity scores of the 10 Most similar restuarants
    sim_scores = sim_scores[1:11]

    ### Get the restauarant inidices
    restaurant_indices = [i[0] for i in sim_scores]

    ### Resturn the Top 10 most similar restaurants
    df["Name"] = df["Name"] + " on " + df["Street Address"]

    rait_matr = [rate * i + 1 for i in range(len(df['Name'].iloc[restaurant_indices].tolist()))]

    d = {'rate': rait_matr[::-1], 'restaurant': df['Name'].iloc[restaurant_indices].tolist()}
    return pd.DataFrame(data=d, columns=['rate', 'restaurant'])


def get_friends(name):
    try:
        con = sql.connect('rest_database.db')
        c = con.cursor()  # cursor
        # insert data
        query = "SELECT COUNT(DISTINCT usubject) from tbl_RS"
        params = ()
        c.execute(query, params)
        number_of_subj = c.fetchall()
        # print(number_of_subj[0][0])
    except con.Error as err:  # if error
        # then display the error in 'database_error.html' page
        return render_template('database_error.html', error=err)
    finally:
        con.close()  # close the connection
    print(number_of_subj[0][0])

    if number_of_subj[0][0] >= 5:
        try:
            con = sql.connect('rest_database.db')
            c = con.cursor()  # cursor
            # insert data
            query = "with a_data as (SELECT sum(rate) as sum_rate, Restaurant  from tbl_RS WHERE rate>=4 " \
                    "AND Restaurant not in (SELECT Restaurant from tbl_RS WHERE usubject = ?) AND usubject in " \
                    "(SELECT distinct usubject from " \
                    "(SELECT b.usubject, b.Restaurant, b.rate from (SELECT * FROM tbl_RS WHERE usubject = ?) a " \
                    "inner join (SELECT * FROM tbl_RS WHERE usubject != ?) b " \
                    "on a.Restaurant=b.Restaurant and abs(a.rate-b.rate)<=1) group by usubject) group by Restaurant)" \
                    "SELECT sum_rate/(SELECT max(sum_rate) from a_data), Restaurant from a_data"
            params = (name, name, name)
            c.execute(query, params)
            info = c.fetchall()

            return pd.DataFrame(data=info, columns=['rate', 'restaurant'])
        except con.Error as err:  # if error
            # then display the error in 'database_error.html' page
            return render_template('database_error.html', error=err)
        finally:
            con.close()  # close the connection
    else:
        return pd.DataFrame(data=[[],[]], columns=['rate', 'restaurant'])

# get_friends('Seva')
# df = pd.concat([get_recommendations(name='Coach House Diner', rate=3), get_recommendations(name='Coach House Diner', rate=3), get_recommendations(name='Coach House Diner', rate=3)], ignore_index=True)
# print(get_recommendations(name='15 Church Restaurant', rate=3))
# print(df.groupby('restaurant', as_index=False).sum())
