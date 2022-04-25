from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from interweb.auth import login_required
from interweb.db import get_db

bp= Blueprint("serv",__name__)
@bp.route("/")
def index():
    db = get_db()
    serv = db.execute(
        "SELECT s.id, adresse, port, size, created, username, author_id"
        " FROM serv s JOIN user u ON s.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("serv/index.html", serv=serv)

@bp.route("/create",methods=("GET","POST"))
@login_required

def create():
    if request.method == "POST":
        adress = request.form["adress"]
        port = request.form["port"]
        size = request.form["size"]
        error = None
        
        db = get_db()
        serv = db.execute("SELECT adresse FROM serv").fetchall()
        
        try:
            for i in adress.split("."):
                if int(i) > 255:
                    raise ValueError("Adresse ip invalide")
            for s in serv:
                if s["adresse"]==adress:
                    raise ValueError("Adresse ip invalide")
        except: 
            error = "Adresse ip invalide"
        
        if not port:
            error = "Port non defini"
        
        if not size:
            error = "Taille non definie"
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute( "INSERT INTO serv (author_id, adresse, port, size) VALUES (?, ?, ?, ?)",(g.user["id"],adress,port,size))
            db.commit()
            return redirect(url_for("serv.index"))
    return render_template("serv/create.html")

def get_post(id, check_author=True):
    serv = get_db().execute(
        'SELECT s.id, adresse, port, size, created, author_id, username'
        ' FROM serv s JOIN user u ON s.author_id = u.id'
        ' WHERE s.id = ?',
        (id,)
    ).fetchone()

    if serv is None:
        abort(404, f"server id {id} doesn't exist.")

    if check_author and serv['author_id'] != g.user['id']:
        abort(403)

    return serv
    
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required

def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM serv WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('serv.index'))