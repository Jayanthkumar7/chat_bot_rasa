from flask import Flask ,render_template,redirect,request,url_for,Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, login_required, LoginManager, logout_user, current_user, UserMixin
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookticket.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'the_secret_key'

db = SQLAlchemy(app)

class user(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer , primary_key = True,autoincrement=True)
    username=db.Column(db.String(50),nullable=False)
    name=db.Column(db.String,nullable=False)
    email=db.Column(db.String,nullable=False)
    password=db.Column(db.String,nullable=False)
    
    def get_id(self):
        return str(self.id)
    
class event(db.Model):
    __tablename__= 'events'
    id = db.Column(db.Integer , primary_key = True,autoincrement=True)
    ename=db.Column(db.String,nullable=False)
    t_price=db.Column(db.Float,nullable=False)
    seats=db.Column(db.Integer,nullable=False)
    description=db.Column(db.String,nullable=False)
    image=db.Column(db.LargeBinary,unique=True,nullable=False)
    name=db.Column(db.Text,nullable=False)
    mimetype=db.Column(db.Text,nullable=False)
    
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))  

    
@app.route('/',methods=['POST','GET'])
def home():
    
    events = event.query.all()
    
    
    return render_template('home.html', active_page='home',events=events,current_user=current_user)


@app.route('/event_image/<int:event_id>')
def event_image(event_id):
    event_data = event.query.filter_by(id=event_id).first()

    if not event_data or not event_data.image:
        return 'Image not found', 404

    return Response(event_data.image, mimetype=event_data.mimetype)


@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html', active_page='portfolio',current_user=current_user)

@app.route('/event_details/<int:event_id>',methods=['POST','GET'])
def event_details(event_id):
    event_details=event.query.filter_by(id=event_id).first()
    
    if request.method == 'POST':
        no_of_seats=request.form.get('no_of_tickets')
        
        return redirect(url_for('checkout', seats=no_of_seats, event_id=event_id))

        
    
    return render_template('event_details.html',event_details=event_details,current_user=current_user,active_page='Event Details')

@login_required
@app.route('/checkout/<int:seats>,<int:event_id>',methods=['POST','GET'])
def checkout(seats,event_id):
    event_details=event.query.filter_by(id=event_id).first()
    return render_template('checkout.html',active_page='checkout',seats=seats,event_details=event_details)


@app.route('/events')
def events():
    return render_template('events.html', active_page='events')

@login_required
@app.route('/bookings')
def bookings():
    return render_template('bookings.html',active_page='bookings')
@app.route('/login',methods=['POST','GET'])
def login():
    message=''
    if request.method =='POST':
        email = request.form.get('email')
        password=request.form.get('password')
    
        user_details=user.query.filter_by(email=email).first()
        if not user_details:
            message='User not exist !'
            return redirect('login')
        if user_details:
            if user_details.password == password:
                login_user(user_details)
                return redirect('/')
            else:
                message='incorrect username or password !'
                return redirect('login')    
            
    
    return render_template('login.html', active_page='login',message=message,current_user=current_user)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    message = ''
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        username=request.form.get('username')
        pass1 = request.form.get('password1')
        pass2 = request.form.get('password2')
        
        user_details = user.query.filter_by(email=email).first()
        user_details2 = user.query.filter_by(username=username).first()
        
        if user_details or user_details2:
            message = 'User is already registered, please login or create a new account'
            return redirect(url_for('signup'))
        if pass1 != pass2:
            message = 'Passwords do not match'
            return redirect(url_for('signup'))
        
        new_user = user(name=name, email=email, password=pass1,username=username)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))    
        
    return render_template('signup.html', active_page='signup', message=message,current_user=current_user)  

@app.route('/admin',methods=['POST','GET'])
def admin():
    message=''
    if request.method == 'POST':
        ename=request.form.get('ename')
        t_price=request.form.get('t_price')
        seats=request.form.get('seats')
        description=request.form.get('description')
        pic=request.files['pic']
        filename=secure_filename(pic.filename)
        mimetype=pic.mimetype
        image_data=pic.read()
        
        insertion=event(ename=ename,t_price=t_price,seats=seats,description=description,image=image_data,name=filename,mimetype=mimetype)
        db.session.add(insertion)
        db.session.commit()
        message='insertion is successful'
    
    return render_template ('admin.html' , message=message) 

@login_required
@app.route('/logout',methods=['POST','GET'])
def logout():
    logout_user()
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)