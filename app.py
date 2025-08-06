from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import csv
import io
from datetime import datetime

app = Flask(__name__)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hockey-stats-secret-key-1994'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///hockey_stats.db'
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'images', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config.from_object(Config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth_login'
login_manager.login_message = 'Please log in to access the admin panel.'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    jersey_number = db.Column(db.Integer, unique=True)
    age = db.Column(db.Integer)
    height = db.Column(db.String(10))
    weight = db.Column(db.Integer)
    hometown = db.Column(db.String(100))
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    penalty_minutes = db.Column(db.Integer, default=0)
    games_played = db.Column(db.Integer, default=0)
    plus_minus = db.Column(db.Integer, default=0)
    image_filename = db.Column(db.String(200))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    @property
    def points(self):
        return self.goals + self.assists
    
    @property
    def image_url(self):
        if self.image_filename:
            return f'/uploads/{self.image_filename}'
        return '/static/images/default_player.png'

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    opponent = db.Column(db.String(100), nullable=False)
    home_game = db.Column(db.Boolean, default=True)
    our_score = db.Column(db.Integer, default=0)
    opponent_score = db.Column(db.Integer, default=0)
    venue = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def result(self):
        if self.our_score > self.opponent_score:
            return 'W'
        elif self.our_score < self.opponent_score:
            return 'L'
        else:
            return 'T'
    
    @property
    def score_display(self):
        return f"{self.our_score}-{self.opponent_score}"

class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(500))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published = db.Column(db.Boolean, default=True)
    featured = db.Column(db.Boolean, default=False)
    author = db.relationship('User', backref=db.backref('news_posts', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    try:
        featured_players = Player.query.filter_by(is_featured=True, is_active=True).all()
        recent_news = News.query.filter_by(published=True).order_by(News.created_at.desc()).limit(5).all()
        recent_matches = Match.query.order_by(Match.date.desc()).limit(5).all()
        
        active_players = Player.query.filter_by(is_active=True).all()
        total_goals = sum(p.goals for p in active_players)
        total_assists = sum(p.assists for p in active_players)
        total_points = total_goals + total_assists
        top_scorer = Player.query.filter_by(is_active=True).order_by(Player.goals.desc()).first()
        
        team_stats = {
            'total_goals': total_goals,
            'total_assists': total_assists,
            'total_points': total_points,
            'top_scorer': top_scorer
        }
    except Exception as e:
        featured_players = []
        recent_news = []
        recent_matches = []
        team_stats = {
            'total_goals': 0,
            'total_assists': 0,
            'total_points': 0,
            'top_scorer': None
        }
    
    return render_template('index.html', 
                         featured_players=featured_players,
                         recent_news=recent_news,
                         recent_matches=recent_matches,
                         team_stats=team_stats)

@app.route('/player/<int:player_id>')
def player_detail(player_id):
    player = Player.query.get_or_404(player_id)
    return render_template('player_detail.html', player=player)

@app.route('/auth/login', methods=['GET', 'POST'])
def auth_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=True)
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@app.route('/auth/logout')
@login_required
def auth_logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/')
@login_required
def admin_dashboard():
    total_players = Player.query.filter_by(is_active=True).count()
    total_matches = Match.query.count()
    total_news = News.query.filter_by(published=True).count()
    recent_matches = Match.query.order_by(Match.date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_players=total_players,
                         total_matches=total_matches,
                         total_news=total_news,
                         recent_matches=recent_matches)

@app.route('/admin/players')
@login_required
def admin_players():
    players = Player.query.all()
    return render_template('admin/players.html', players=players)

@app.route('/admin/players/add', methods=['GET', 'POST'])
@login_required
def admin_add_player():
    if request.method == 'POST':
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
                image_filename = timestamp + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
        player = Player(
            name=request.form['name'],
            position=request.form['position'],
            jersey_number=int(request.form['jersey_number']) if request.form['jersey_number'] else None,
            age=int(request.form['age']) if request.form['age'] else None,
            height=request.form['height'],
            weight=int(request.form['weight']) if request.form['weight'] else None,
            hometown=request.form['hometown'],
            goals=int(request.form['goals']) if request.form['goals'] else 0,
            assists=int(request.form['assists']) if request.form['assists'] else 0,
            penalty_minutes=int(request.form['penalty_minutes']) if request.form['penalty_minutes'] else 0,
            games_played=int(request.form['games_played']) if request.form['games_played'] else 0,
            plus_minus=int(request.form['plus_minus']) if request.form['plus_minus'] else 0,
            bio=request.form['bio'],
            image_filename=image_filename,
            is_featured='is_featured' in request.form
        )
        
        db.session.add(player)
        db.session.commit()
        flash('Player added successfully!', 'success')
        return redirect(url_for('admin_players'))
    
    return render_template('admin/add_player.html')

@app.route('/admin/players/delete/<int:player_id>', methods=['POST'])
@login_required
def admin_delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    
    if player.image_filename:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], player.image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(player)
    db.session.commit()
    flash('Player deleted successfully!', 'success')
    return redirect(url_for('admin_players'))

@app.route('/admin/matches')
@login_required
def admin_matches():
    matches = Match.query.order_by(Match.date.desc()).all()
    return render_template('admin/matches.html', matches=matches)

@app.route('/admin/matches/add', methods=['GET', 'POST'])
@login_required
def admin_add_match():
    if request.method == 'POST':
        match = Match(
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            opponent=request.form['opponent'],
            home_game='home_game' in request.form,
            our_score=int(request.form['our_score']) if request.form['our_score'] else 0,
            opponent_score=int(request.form['opponent_score']) if request.form['opponent_score'] else 0,
            venue=request.form['venue'],
            notes=request.form['notes']
        )
        
        db.session.add(match)
        db.session.commit()
        flash('Match added successfully!', 'success')
        return redirect(url_for('admin_matches'))
    
    return render_template('admin/add_match.html')

@app.route('/admin/news')
@login_required
def admin_news():
    news_posts = News.query.order_by(News.created_at.desc()).all()
    return render_template('admin/news.html', news_posts=news_posts)

@app.route('/admin/news/add', methods=['GET', 'POST'])
@login_required
def admin_add_news():
    if request.method == 'POST':
        news_post = News(
            title=request.form['title'],
            content=request.form['content'],
            excerpt=request.form['excerpt'],
            author_id=current_user.id,
            published='published' in request.form,
            featured='featured' in request.form
        )
        
        db.session.add(news_post)
        db.session.commit()
        flash('News post added successfully!', 'success')
        return redirect(url_for('admin_news'))
    
    return render_template('admin/add_news.html')

@app.route('/admin/export/players')
@login_required
def admin_export_players():
    players = Player.query.filter_by(is_active=True).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'Name', 'Position', 'Jersey #', 'Age', 'Height', 'Weight',
        'Hometown', 'Goals', 'Assists', 'Points', 'PIM', 'Games Played', '+/-'
    ])
    
    for player in players:
        writer.writerow([
            player.name, player.position, player.jersey_number,
            player.age, player.height, player.weight, player.hometown,
            player.goals, player.assists, player.points,
            player.penalty_minutes, player.games_played, player.plus_minus
        ])
    
    output.seek(0)
    output_bytes = io.BytesIO()
    output_bytes.write(output.getvalue().encode('utf-8'))
    output_bytes.seek(0)
    
    return send_file(
        output_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'players_stats_{datetime.now().strftime("%Y%m%d")}.csv'
    )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def create_admin_user():
    try:
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@lesplombiers.com',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: admin/admin123")
    except Exception as e:
        print(f"Could not create admin user: {e}")

def init_database():
    try:
        db.create_all()
        create_admin_user()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database initialization error: {e}")

with app.app_context():
    init_database()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)