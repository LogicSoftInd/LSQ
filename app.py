from flask import Flask, render_template, request, redirect, url_for, flash

import db
import config

app = Flask(__name__)
app.secret_key = config.flask_secret_key

@app.route("/")
def index():
        searchword = request.args.get('search', '')
        if (searchword):
            queries = db.get_queries_for_search(searchword)
            if len(queries)== len(db.get_queries()):
                flash("No record found", "error")
        else:
            queries = db.get_queries()
    

        return render_template("index.html", queries=queries, issearchword=searchword)

@app.route("/query/", methods=["POST"])
def query_add():
    try:
        title = request.form["title"].strip()
        sql = request.form["sql"].strip()
        tags = request.form["tags"].strip()
        desc = request.form["desc"].strip()
        who = request.form["who"].strip()

        if len(title) == 0 or len(sql) == 0:
            flash("Title and Sql are required fields", "error")
            return redirect(url_for("index"))

        db.insert_query(title, sql, tags, desc, who)
        flash("Query Added!", "success")
        return redirect(url_for("index"))

    except Exception as e:
        app.logger.error("Fatal error", exc_info=True)
        flash("Fatal error. Contact Administrator", "error")
        return redirect(url_for("index"))

@app.route("/query/<id>/", methods=["GET", "DELETE"])
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
            desc = request.form["desc"].strip()
            who = request.form["who"].strip()

            if len(title) == 0 or len(sql) == 0:
                flash("Title and Sql are required fields", "error")
                return redirect(url_for("query_edit", id=id))

            db.update_query(id, title, sql, tags, desc, who)
            flash("Query Modified!", "success")
            return redirect(url_for("query_view", id=id))

        except Exception as e:
            app.logger.error("Fatal error", exc_info=True)
            flash("Fatal error. Contact Administrator", "error")
            return redirect(url_for("index"))

@app.route("/query/<id>/delete/", methods=["GET", "POST"])
def query_delete(id):
    if request.method == "GET":
        query = db.get_query_details(id)
        return render_template("delete_query.html", query=query)
    elif request.method == "POST":
        db.delete_query(id)
        flash("Delete Successful", "success")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=config.flask_debug, port=config.flask_port, host=config.flask_bind_address)
