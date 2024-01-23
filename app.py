import os
from datetime import date
from flask import Flask, render_template, request, url_for, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
import random

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
    
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(2000), nullable=False)
    pub_date = db.Column(db.Date, nullable=False)
    link = db.Column(db.String, nullable=False)
    source = db.Column(db.String(200), nullable=False)
    tag = db.Column(db.String(20))

    def __str__(self) -> str:
        return f"{self.source}: {self.title}"

@app.route('/')
def signin():
    return render_template('sign-in.html')

@app.route('/topics')
def topics():
    return render_template('topics.html')

@app.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.order_by(Article.pub_date.desc()).paginate(page=page, per_page=10)
    return render_template('index.html', pagination=pagination)

@app.route('/<article_tag>/')
def filter(article_tag):
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.filter_by(tag = article_tag).order_by(Article.pub_date.desc()).paginate(page=page, per_page=10)
    return render_template('filter.html', tag = article_tag, pagination=pagination)

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=5000, debug=True)