import logging
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from models import Recipe
from app import db, socketio

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('home.html')

@main.route('/upload')
@login_required
def upload():
    try:
        return render_template('index.html', 
                          tinymce_api_key="cic11ch0565sd3xwncfbpuleqz0vw4cdxr3823ok37gddt53")
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return "Internal Server Error", 500

@main.route('/api/recipes/<int:page>')
def get_recipes(page):
    per_page = 10
    recipes = Recipe.query.order_by(Recipe.id.desc()).offset(page * per_page).limit(per_page).all()
    return jsonify([{
        'id': recipe.id,
        'name': recipe.name,
        'ingredients': recipe.get_ingredients(),
        'content': recipe.content
    } for recipe in recipes])

@main.route('/add', methods=['POST'])
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

@main.route('/recipe/<int:recipe_id>')
@login_required
def view_recipe(recipe_id):
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        return render_template('recipe.html', recipe=recipe)
    except Exception as e:
        logger.error(f"Error viewing recipe {recipe_id}: {str(e)}")
        return "Hiba történt a recept betöltése során", 500

@socketio.on('search')
def handle_search(data):
    try:
        query = data['query'].lower()
        
        # If user is authenticated, filter by their recipes
        if current_user.is_authenticated:
            results = Recipe.query.filter(
                Recipe.name.ilike(f'%{query}%')
            ).filter_by(user_id=current_user.id).all()
        else:
            # If not authenticated, return empty results
            results = []
            
        results_json = [{'id': r.id, 'name': r.name} for r in results]
        socketio.emit('search_results', results_json)
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        socketio.emit('error', {'message': 'Hiba történt a keresés során'})
