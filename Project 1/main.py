# flask is the library, Flask is an object from flask library
from flask import Flask 

# __name__ is a python key term
app = Flask(__name__)

#run route after /, when a cient type in the path, the function index() will run
@app.route("/") #this is a decorator function= a concept in python, it is called this name because it adds more onto the index() function that does more than just reutrn texts.
def index():
    return '<h1> Hello world from CART 351 </h1>'

@app.route("/about")
def about():
    return '<h1 style = "color:purple"> About CART 351'

# <name> is a varible so it needs the brackets
@app.route("/users/<name>")
def user_profile(name):
    return f"<h2> This is <span style = 'color: orange'>{name}'s</span> profile page </h2>"

# Testing error debugging
# @app.route("/another/<dynamicVar>")
# def another_Route(dynamicVar):
#     return f"<h2> the 100th letter of {dynamicVar} is {dynamicVar[99]}</h2>"

# routing exercise
# @app.route("/cats/<catsname>") 
# def latincats(catsname):
#     if {catsname[-1]} ="y"
#     return f"<h2> The new cat name of {catsname} is {catsname[-1]}</h2>"


#turn on debugging on the browser in python
app.run(debug=True)