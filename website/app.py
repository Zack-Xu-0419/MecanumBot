import sqlite3
import os
import datetime
import time
from datetime import datetime, timedelta
from pathlib import Path
from wtforms import DateField, Form, validators
from flask import Flask, request, url_for, render_template, redirect, session

currentDirectory = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

app.secret_key = "Hspt"

color = datetime.now().hour


@app.route('/init', methods=["GET", "POST"])
def init():
    if request.method == "GET":
        return render_template("init.html")
    else:
        if request.form["password"] == "SHIELD":
            print("true")
            dbConnection = sqlite3.connect(currentDirectory + "/Home.db")
            initCursor = dbConnection.cursor()
            initCursor.execute(
                "CREATE TABLE IF NOT EXISTS bibleGuidelines(description TEXT, verse TEXT, category TEXT, toward TEXT, needWorkingOn BOOL, notes TEXT, provenUseful TEXT)")
            initCursor.execute(
                "CREATE TABLE IF NOT EXISTS countdown(description TEXT, initialDate DATE, targetDate DATE, person TEXT, priority INTEGER, displayUnit TEXT)")
            dbConnection.commit()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")


@app.route("/api/getRobotInfo", methods=["GET"])
def getRobotInfo():
    return {"time": time.time()}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
