import logging
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models import User, Recipe, UserRole
from app import db

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@login_required
@admin_required
def dashboard():
    users = User.query.filter_by(role=UserRole.USER.value).all()
    recipes = Recipe.query.all()
    return render_template('admin/dashboard.html', users=users, recipes=recipes)

@admin.route('/users')
@login_required
@admin_required
def users():
    users = User.query.filter_by(role=UserRole.USER.value).all()
    return render_template('admin/users.html', users=users)

@admin.route('/recipes')
@login_required
@admin_required
def recipes():
    recipes = Recipe.query.all()
    return render_template('admin/recipes.html', recipes=recipes)

@admin.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin():
        flash('Admin felhasználót nem lehet törölni!', 'error')
        return redirect(url_for('admin.users'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash('Felhasználó sikeresen törölve!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Hiba történt a felhasználó törlése során!', 'error')
        logger.error(f"Error deleting user {user_id}: {str(e)}")

    return redirect(url_for('admin.users'))

@admin.route('/recipe/<int:recipe_id>/delete', methods=['POST'])
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

    return redirect(url_for('admin.recipes'))
