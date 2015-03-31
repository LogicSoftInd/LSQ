from flask import Flask, render_template, request, redirect, url_for, flash

import db

app = Flask(__name__)
app.secret_key = "IAmTheMasterOfMyFateIAmTheCaptainOfMySoul"

@app.route("/")
def index():
    queries = db.get_queries()
    return render_template("index.html", queries=queries)

@app.route("/query/", methods=["POST"])
def query_add():

    try:
        title = request.form["title"].strip()
        sql = request.form["sql"].strip()
        tags = request.form["tags"].strip()

        if len(title) == 0 or len(sql) == 0:
            flash("title and sql are required fields", "error")
            return redirect(url_for("index"))

        db.insert_query(title, sql, tags)
        return redirect(url_for("index"))

    except Exception as e:
        print e
        return redirect(url_for("index"))

@app.route("/query/<id>/")
def query_view(id):
    query = db.get_query_details(id)
    return render_template("view_query.html", query=query)

@app.route("/query/<id>/edit/", methods=["GET", "POST"])
def query_edit(id):
    if request.method == "GET":
        query = db.get_query_details(id)
        return render_template("edit_query.html", query=query)
    elif request.method == "POST":
        try:
            id = request.form["id"].strip()
            title = request.form["title"].strip()
            sql = request.form["sql"].strip()
            tags = request.form["tags"].strip()

            if len(title) == 0 or len(sql) == 0:
                flash("title and sql are required fields", "error")
                return redirect(url_for("query_edit", id=id))

            db.update_query(id, title, sql, tags)
            return redirect(url_for("index"))

        except Exception as e:
            print e
            return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
