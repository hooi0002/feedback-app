from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from send_mail import send_mail

# Initialize our app
app = Flask(__name__)

ENV = 'prod'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:901029@localhost/EICodeCasting1' # Development Database
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://uvnhcocezwrkma:5c2457495dab6ad37307a6309e043f245cb651c3873218b7ff6d1a8ee3e8759e@ec2-44-205-41-76.compute-1.amazonaws.com:5432/d19b0b0ipsp9rq' # Deployment Database

#add this to avoid getting warning in the console
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create a database object so that we can use this object to query our database
db = SQLAlchemy(app)

# The way that SQLAlchemy works is that we create a model
# similar to what we would do in Mongol or Sequalize
# Create the model in the form of a class
# This class extends db Model
class Feedback(db.Model):
    __tablename__ = 'feedback'

    #Define fields here
    id = db.Column(db.Integer, primary_key=True)
    student = db.Column(db.String(200), unique=True)
    trainer = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())

    def __init__(self, student, trainer, rating, comments):
        self.student = student
        self.trainer = trainer
        self.rating = rating
        self.comments = comments


# Using a decorator to declare the route
# route for the home page, just put a /
# it will then render the index.html template
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        student = request.form['student']
        trainer = request.form['trainer']
        rating = request.form['rating']
        comments = request.form['comments']
        print(student, trainer, rating, comments)
        if student == '' or trainer == '':
            return render_template('index.html', message='Please enter required fields')
        
        #query the database here, to add an entry, we first have to
        #make sure that the student doesn't already exist
        #we don't want the same student the submit the feedback form twice
        if db.session.query(Feedback).filter(Feedback.student == student).count() == 0:
            data = Feedback(student, trainer, rating, comments)
            db.session.add(data)
            db.session.commit()
            send_mail(student, trainer, rating, comments)
            return render_template('success.html')
        return render_template('index.html', message='You have already submitted feedback')


# This should allow us to run our server
if __name__ == '__main__':
    app.run()
