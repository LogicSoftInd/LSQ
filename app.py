from flask import Flask, render_template, request, redirect, url_for, flash

import db
import config
from aes import AESCipher

app = Flask(__name__)
app.secret_key = config.flask_secret_key

@app.route("/")
def index():
        searchword = request.args.get('search', '')
        if (searchword):
            queries = db.get_queries_for_search(searchword)
            if len(queries) == 0:
                flash("No record found", "error")
                queries = db.get_queries()
        else:
            queries = db.get_queries()

        databases = db.get_databases()
        
        return render_template("index.html", databases=databases, queries=queries, issearchword=searchword)

@app.route("/queries.json/")
def query_list():
    queries = db.get_queries()
    databases = db.get_databases()
    qlist = [
                {
                    "id":str(query["_id"]), 
                    "title":query['title'], 
                    "created_by":query['who'], 
                    "tags":query['tags']
                } 
            for query in queries]
    return jsonify({ "queries": qlist });

@app.route("/query/", methods=["POST"])
def query_add():
    try:
        title = request.form.get("title").strip()
        sql = request.form.get("sql").strip()
        tags = request.form.get("tags").strip()
        desc = request.form.get("desc").strip()
        who = request.form.get("who").strip()

        if not title or not sql:
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
    databases = db.get_databases()
    query = db.get_query_details(id)
    return render_template("view_query.html", databases=databases, query=query)

@app.route("/query/<id>/json/", methods=["GET"])
def query_json_view(id):
    query = db.get_query_details(id)
    json_val = {
        "title":query['title'],
        "query":query['sql'],
        "tags":query['tags'],
        "description":query['desc'],
        "created_by":query['who']
    }
    return jsonify(json_val)

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

@app.route("/query/<id>/run/<database_id>", methods=["GET", "POST"])
def query_run(id, database_id):
    """ Run a query against a specific database instance """
    if config.enable_run_query:
        database = db.get_database_details(database_id)
        query = db.get_query_details(id)
        query_results = None
        query_results_cols = []
        error = None

        # try and import the DB engine
        try: 
            dbapi2 = __import__(config.database_engine)
        except ImportError as e:
            app.logger.error("Fatal error. Could not import DB engine.", exc_info=True)
            flash("Fatal error. Contact Administrator", "error")
            return redirect(url_for("index"))
        
        # try and make the connection and run the query
        try:
            if database.get("password"):
                crypt = AESCipher(config.flask_secret_key)
                password = crypt.decrypt(database.get("password"))
            else:
                password = None
            
            connect = dbapi2.connect(database=database.get("name"), 
                host=database.get("hostname"), 
                port=database.get("port"), 
                user=database.get("user"), 
                password=password)
            
            curse = connect.cursor()
            curse.execute(query["sql"])
            query_results = curse.fetchall()

            # Assemble column names so the table makes sense
            for col in curse.description:
                query_results_cols.append(col.name)

        except dbapi2.ProgrammingError, e:
            # TODO: Exceptions don't seem to be standard in DB-API2, 
            # so this will likely have to be checked against other
            # engines.  The following works with psycopg2.
            if hasattr(e, "pgerror"):
                error = e.pgerror
            else:
                error = "There was an error with your query."
        except dbapi2.Error as e:
            if hasattr(e, "pgerror"):
                error = e.pgerror or e.message
                app.logger.error(error)
            else:
                error = e.msg
                app.logger.error(error)

    else: 
        database = None
        query = None
        query_results = None
        query_results_cols = None
        error = None
    return render_template("run_query.html", run_enabled=config.enable_run_query, query=query, database=database, query_results=query_results, query_results_cols=query_results_cols, error=error)

@app.route("/database/", methods=["POST"])
def database_add():
    try:
        name = request.form.get("name").strip()
        hostname = request.form.get("hostname").strip()
        port = request.form.get("port", "").strip()
        user = request.form.get("user", "").strip()
        password = request.form.get("password", "").strip()
        desc = request.form.get("desc", "").strip()

        if not name or not hostname:
            flash("Name and Host/File Name are required fields", "error")
            return redirect(url_for("index"))

        db.insert_database(name, hostname, port, user, password, desc)
        flash("Database Added!", "success")
        return redirect(url_for("index"))

    except Exception as e:
        app.logger.error("Fatal error", exc_info=True)
        flash("Fatal error. Contact Administrator", "error")
        return redirect(url_for("index"))

@app.route("/database/<id>/edit/", methods=["GET", "POST"])
def database_edit(id):
    if request.method == "GET":
        database = db.get_database_details(id)
        if database['password']:
            database['password'] = 'placeholder'
        return render_template("edit_database.html", database=database)
    elif request.method == "POST":
        try:
            id = request.form["id"].strip()
            name = request.form.get("name").strip()
            hostname = request.form.get("hostname").strip()
            port = request.form.get("port", "").strip()
            user = request.form.get("user", "").strip()
            password = request.form.get("password", "").strip()
            if password == 'placeholder':
                password = None
            desc = request.form.get("desc", "").strip()

            if not name or not hostname:
                flash("Name and Host/File Name are required fields", "error")
                return redirect(url_for("database_edit", id=id))

            db.update_database(id, name, hostname, port, user, password, desc)
            flash("Database Modified!", "success")
            return redirect(url_for("database_view", id=id))

        except Exception as e:
            app.logger.error("Fatal error", exc_info=True)
            flash("Fatal error. Contact Administrator", "error")
            return redirect(url_for("index"))

@app.route("/database/<id>/", methods=["GET", "DELETE"])
def database_view(id):
    database = db.get_database_details(id)
    return render_template("view_database.html", database=database)

@app.route("/database/<id>/delete/", methods=["GET", "POST"])
def database_delete(id):
    if request.method == "GET":
        database = db.get_database_details(id)
        return render_template("delete_database.html", database=database)
    elif request.method == "POST":
        db.delete_database(id)
        flash("Delete Successful", "success")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=config.flask_debug, port=config.flask_port, host=config.flask_bind_address)
