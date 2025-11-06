from flask import Flask,render_template
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("pineapple.html")

@app.route("/another")
def another():
    return render_template("pineappleTwo.html")

@app.route("/three")
def three():
    someNewVar = "bananas" 
    someNewList = ["one", "two", "three"]
    someNewDict= {"color":"yellow", "feature":"spiky", "taste":"sweet"}
    return render_template("pineappleThree.html", 
                           someHTMLVar = someNewVar,
                           someHTMLList = someNewList,
                           someHTMLDict = someNewDict)

@app.route("/four")
def four():
    userLoggedIn =False
    aNewList = [1,2,3,4,5]
    bNewList = ["yellow","orange","fuscia","navy","green"]
    return render_template("pineappleFour.html", 
                           #aHTMLList = aNewList is a standard key value pairs
                           aHTMLList = aNewList,
                           bHTMLList = bNewList,
                           userLoggedInHTML = userLoggedIn) 
app.run(debug=True)