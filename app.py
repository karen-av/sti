from flask import Flask, json, request 
import logging 
import datetime
from cs50 import SQL
import sqlite3
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__) 



@app.route('/') 
def index(): 

    return "<p>Hello, World!</p>"