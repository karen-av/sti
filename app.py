from flask import Flask, json, request 


app = Flask(__name__) 

@app.route('/') 
def index(): 

    return "<p>Hello, World!</p>"