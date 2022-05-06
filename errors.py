from flask import flash, redirect

def authentication_error():
    flash("Sinulla ei ole oikeutta nähdä sivua", category="error")
    return redirect("/error")

def page_not_found():
    flash("Sivua ei löytynyt", category="error")
    return redirect("/error")
