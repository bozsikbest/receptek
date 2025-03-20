import os
import logging
from urllib.parse import urlparse
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_socketio import SocketIO
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app import app, db # Importing from app.py
from models import Recipe, User, UserRole # Import UserRole enum from models.py
from forms import LoginForm, RegistrationForm
from functools import wraps
from flask import abort

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = "lsadifhsikdjvbkjsdbv"
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

from flask import Blueprint
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Érvénytelen felhasználónév vagy jelszó')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('upload')
        return redirect(next_page)
    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Sikeres regisztráció!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('upload'))

app.register_blueprint(auth, url_prefix='/auth')

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/api/recipes/<int:page>')
def get_recipes(page):
    per_page = 10
    recipes = Recipe.query.order_by(Recipe.id.desc()).offset(page * per_page).limit(per_page).all()
    return jsonify([{
        'id': recipe.id,
        'name': recipe.name,
        'ingredients': recipe.get_ingredients(),
        'content': recipe.content
    } for recipe in recipes])

@app.route('/upload')
@login_required
def upload():
    try:
        return render_template('index.html', 
                             tinymce_api_key="cic11ch0565sd3xwncfbpuleqz0vw4cdxr3823ok37gddt53")
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return "Internal Server Error", 500

@socketio.on('search')
def handle_search(data):
    try:
        query = data['query'].lower()
        results = Recipe.query.filter(
            Recipe.name.ilike(f'%{query}%')
        ).filter_by(user_id=current_user.id).all()
        results_json = [{'id': r.id, 'name': r.name} for r in results]
        socketio.emit('search_results', results_json)
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        socketio.emit('error', {'message': 'Hiba történt a keresés során'})

@app.route('/add', methods=['POST'])
@login_required
def add_recipe():
    try:
        data = request.json
        name = data.get('name')
        ingredients = data.get('ingredients', [])
        content = data.get('content')

        if not name or not content:
            return jsonify({'error': 'A név és a leírás megadása kötelező!'}), 400

        if not ingredients:
            return jsonify({'error': 'Legalább egy hozzávaló megadása kötelező!'}), 400

        recipe = Recipe(name=name, ingredients=ingredients, content=content, user_id=current_user.id)
        db.session.add(recipe)
        db.session.commit()

        return jsonify({'message': 'Recept sikeresen hozzáadva!'})
    except Exception as e:
        logger.error(f"Error adding recipe: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Hiba történt a recept mentése során'}), 500

@app.route('/recipe/<int:recipe_id>')
@login_required
def view_recipe(recipe_id):
    try:
        recipe = Recipe.query.filter_by(id=recipe_id).first_or_404()
        return render_template('recipe.html', recipe=recipe)
    except Exception as e:
        logger.error(f"Error viewing recipe {recipe_id}: {str(e)}")
        return "Hiba történt a recept betöltése során", 500

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    users = User.query.filter_by(role=UserRole.USER.value).all()
    recipes = Recipe.query.all()
    return render_template('admin/dashboard.html', users=users, recipes=recipes)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.filter_by(role=UserRole.USER.value).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/recipes')
@login_required
@admin_required
def admin_recipes():
    recipes = Recipe.query.all()
    return render_template('admin/recipes.html', recipes=recipes)

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin():
        flash('Admin felhasználót nem lehet törölni!', 'error')
        return redirect(url_for('admin_users'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash('Felhasználó sikeresen törölve!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Hiba történt a felhasználó törlése során!', 'error')
        logger.error(f"Error deleting user {user_id}: {str(e)}")

    return redirect(url_for('admin_users'))

@app.route('/admin/recipe/<int:recipe_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    try:
        db.session.delete(recipe)
        db.session.commit()
        flash('Recept sikeresen törölve!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Hiba történt a recept törlése során!', 'error')
        logger.error(f"Error deleting recipe {recipe_id}: {str(e)}")

    return redirect(url_for('admin_recipes'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)