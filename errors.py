from flask import flash, redirect

def authentication_error():
    flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
    return redirect("/error")