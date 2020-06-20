from flask import Flask, render_template
from flask_pymongo import PyMongo
import scrape_mars


app = Flask(__name__)

# Use flask_pymongo to set up mongoDB connection.
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

@app.route("/")
def index():
    mars = mongo.db.mars.find_one()
    # return render_template("index.html")
    return render_template("index.html", mars=mars)

@app.route("/scrape")
def scrape():
    mars = mongo.db.mars
    mars_data = scrape_mars.scrape_all()
    # print(mars_data)
    mars.replace_one({}, mars_data, upsert=True)
    return "Scrape Successful!!!"

if __name__ == "__main__":
    app.run(debug=True)