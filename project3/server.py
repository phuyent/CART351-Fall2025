
# PROJECT III: ARTISAN NETWORK - Explorable Networked Craft Workshop
# =====================================================================
# A collaborative craft workshop platform where users create paintings,
# flower arrangements, and charm bracelets in a shared community space.


from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime
from datetime import timedelta
from functools import wraps
from config import Config
import os
import base64
import json
from bson.objectid import ObjectId
from config import config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])

# Load configuration
app.config.from_object(Config)
# DEBUG: Print to see if MONGO_URI is loaded
print(f"DEBUG: MONGO_URI = {app.config.get('MONGO_URI')}")
# Initialize MongoDB
mongo = PyMongo(app)

# Test connection
try:
    mongo.db.command('ping')
    print("✅ MongoDB connected successfully!")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")


# Enable CORS
CORS(app)

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'flowers'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'charms'), exist_ok=True)

# ============================================
# HELPER FUNCTIONS
# ============================================

def allowed_file(filename):
    # Check if file extension is allowed
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def serialize_document(doc):
    # Convert MongoDB document to JSON-serializable format
    if doc:
        doc['_id'] = str(doc['_id'])
        if 'creator_id' in doc:
            doc['creator_id'] = str(doc['creator_id'])
    return doc

def serialize_documents(docs):
    # Convert list of MongoDB documents
    return [serialize_document(doc) for doc in docs]

def login_required(f):
    # Decorator to require user login
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    # Get current logged-in user
    if 'user_id' in session:
        return mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    return None

def compress_image(filepath, max_width=800):
    # Compress image for storage
    try:
        img = Image.open(filepath)
        img.thumbnail((max_width, max_width), Image.Resampling.LANCZOS)
        img.save(filepath, quality=85, optimize=True)
    except Exception as e:
        print(f"Error compressing image: {e}")

# ============================================
# ROUTES: Authentication
# ============================================

@app.route('/')
def index():
    # Home page
    user = get_current_user()
    return render_template('index.html', user=user)

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    # User registration
    if request.method == 'POST':
        data = request.get_json()
        
        # Validate input
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        # Check if user exists
        if mongo.db.users.find_one({'email': data['email']}):
            return jsonify({'status': 'error', 'message': 'Email already registered'}), 400
        
        # Create new user
        new_user = {
            'username': data['username'],
            'email': data['email'],
            'password': data['password'], 
            'created_at': datetime.utcnow(),
            'profile_image': None,
            'bio': '',
            'total_creations': 0,
            'total_uploads': 0,
            'last_active': datetime.utcnow()
        }
        
        result = mongo.db.users.insert_one(new_user)
        session['user_id'] = str(result.inserted_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Account created successfully',
            'user_id': str(result.inserted_id)
        }), 201
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Simple name-based login
    if request.method == 'POST':
        # Get username from FORM data (not JSON)
        username = request.form.get('username')
        
        if not username or len(username.strip()) < 2:
            return render_template('auth/login.html', error='Name must be at least 2 characters')
        
        username = username.strip()
        
        # Find or create user
        user = mongo.db.users.find_one({'username': username})
        
        if not user:
            # Create new user
            user = {
                'username': username,
                'created_at': datetime.utcnow(),
                'last_login': datetime.utcnow()
            }
            result = mongo.db.users.insert_one(user)
            user['_id'] = result.inserted_id
        else:
            # Update last login
            mongo.db.users.update_one(
                {'_id': user['_id']}, 
                {'$set': {'last_login': datetime.utcnow()}}
            )
        
        # Store in session
        session['user_id'] = str(user['_id'])
        session['username'] = username
        
        return redirect(url_for('index'))
    
    return render_template('auth/login.html')

@app.context_processor
def inject_user():
    if 'user_id' in session:
        user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
        return {'user': user}
    return {'user': None}

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ============================================================
# API ENDPOINTS - Workshop Save Routes
# ============================================================

@app.route('/api/paintings/save', methods=['POST'])
def save_painting():
    # Save a product painting to database
    try:
        data = request.get_json()
        
        # Get user from session
        if 'username' not in session:
            return jsonify({'status': 'error', 'message': 'Not logged in'}), 401
        
        # Create painting document
        painting = {
            'workshop_type': 'product_painting',
            'username': session['username'],
            'title': data.get('title'),
            'product_type': data.get('product_type'),
            'image_data': data.get('image_data'),
            'colors_used': data.get('colors_used', []),
            'strokes': data.get('strokes', 0),
            'creation_time': data.get('creation_time', 0),
            'created_at': datetime.utcnow(),
            'likes': 0
        }
        
        # Insert into database
        result = mongo.db.paintings.insert_one(painting)
        
        return jsonify({
            'status': 'success',
            'message': 'Painting saved successfully',
            'id': str(result.inserted_id)
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/arrangements/save', methods=['POST'])
def save_arrangement():
    # Save a flower arrangement to database
    try:
        data = request.get_json()
        
        if 'username' not in session:
            return jsonify({'status': 'error', 'message': 'Not logged in'}), 401
        
        arrangement = {
            'workshop_type': 'flower_arranging',
            'username': session['username'],
            'title': data.get('title'),
            'vessel_type': data.get('vessel_type'),
            'image_data': data.get('image_data'),
            'flower_count': data.get('flower_count', 0),
            'creation_time': data.get('creation_time', 0),
            'created_at': datetime.utcnow(),
            'likes': 0
        }
        
        result = mongo.db.arrangements.insert_one(arrangement)
        
        return jsonify({
            'status': 'success',
            'message': 'Arrangement saved successfully',
            'id': str(result.inserted_id)
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/bracelets/save', methods=['POST'])
def save_bracelet():
    # Save a charm bracelet to database
    try:
        data = request.get_json()
        
        if 'username' not in session:
            return jsonify({'status': 'error', 'message': 'Not logged in'}), 401
        
        bracelet = {
            'workshop_type': 'charm_bracelet',
            'username': session['username'],
            'title': data.get('title'),
            'band_type': data.get('band_type'),
            'image_data': data.get('image_data'),
            'charm_count': data.get('charm_count', 0),
            'creation_time': data.get('creation_time', 0),
            'created_at': datetime.utcnow(),
            'likes': 0
        }
        
        result = mongo.db.bracelets.insert_one(bracelet)
        
        return jsonify({
            'status': 'success',
            'message': 'Bracelet saved successfully',
            'id': str(result.inserted_id)
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/creations/all', methods=['GET'])
def get_all_creations():
    # Get all creations from all workshops
    try:
        # Get all paintings
        paintings = list(mongo.db.paintings.find())
        
        # Get all arrangements
        arrangements = list(mongo.db.arrangements.find())
        
        # Get all bracelets
        bracelets = list(mongo.db.bracelets.find())
        
        # Combine all creations
        all_creations = paintings + arrangements + bracelets
        
        # Convert ObjectId to string
        for creation in all_creations:
            creation['_id'] = str(creation['_id'])
        
        # Sort by created_at (newest first)
        all_creations.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
        
        return jsonify({
            'status': 'success',
            'creations': all_creations
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



# ============================================
# ROUTES: Workshops
# ============================================

@app.route('/workshop/product-painting')
@login_required
def product_painting_workshop():
    # Product painting workshop interface
    return render_template('workshops/product-painting.html')

@app.route('/workshop/flower-arranging')
@login_required
def flower_arranging_workshop():
    # Flower arranging workshop interface
    flowers = serialize_documents(mongo.db.flowers.find())
    return render_template('workshops/flower-arrange.html', flowers=flowers)

@app.route('/workshop/charm-bracelet')
@login_required
def charm_bracelet_workshop():
    # Charm bracelet workshop interface
    charms = serialize_documents(mongo.db.charms.find())
    return render_template('workshops/charm-bracelet.html', charms=charms)

# ============================================
# ROUTES: Gallery
# ============================================

@app.route('/gallery')
def gallery():
    # Main gallery page
    return render_template('gallery/index.html')

@app.route('/gallery/<workshop_type>')
def gallery_by_type(workshop_type):
    # Gallery filtered by workshop type
    valid_types = ['product_painting', 'flower_arranging', 'charm_bracelet']
    if workshop_type not in valid_types:
        return redirect(url_for('gallery'))
    return render_template('gallery/by-workshop.html', workshop_type=workshop_type)

@app.route('/profile/<user_id>')
def user_profile(user_id):
    # User profile page
    try:
        user = serialize_document(mongo.db.users.find_one({'_id': ObjectId(user_id)}))
        if not user:
            return redirect(url_for('gallery'))
        
        # Get user's creations
        creations = {
            'paintings': serialize_documents(mongo.db.paintings.find({'creator_id': ObjectId(user_id)})),
            'arrangements': serialize_documents(mongo.db.arrangements.find({'creator_id': ObjectId(user_id)})),
            'bracelets': serialize_documents(mongo.db.bracelets.find({'creator_id': ObjectId(user_id)}))
        }
        
        return render_template('gallery/user-profile.html', user=user, creations=creations)
    except:
        return redirect(url_for('gallery'))

# ============================================
# API: Paintings
# ============================================

@app.route('/api/paintings', methods=['POST'])
@login_required
def create_painting():
    # Create and save a new painting
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['title', 'product_type', 'image_data', 'canvas_size']
        if not all(field in data for field in required):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        # Create painting document
        painting = {
            'creator_id': ObjectId(session['user_id']),
            'workshop_type': 'product_painting',
            'product_type': data['product_type'],
            'canvas_size': data['canvas_size'],
            'image_data': data['image_data'],
            'title': data['title'],
            'description': data.get('description', ''),
            'colors_used': data.get('colors_used', []),
            'brush_sizes': data.get('brush_sizes', []),
            'creation_time': data.get('creation_time', 0),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'likes': 0,
            'views': 0,
            'comments': []
        }
        
        result = mongo.db.paintings.insert_one(painting)
        
        # Update user creation count
        mongo.db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$inc': {'total_creations': 1}}
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Painting saved successfully',
            'painting_id': str(result.inserted_id)
        }), 201
    
    except Exception as e:
        app.logger.error(f"Error creating painting: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/paintings', methods=['GET'])
def get_paintings():
    #Retrieve paintings with optional filters
    try:
        # Get query parameters
        product_type = request.args.get('product_type')
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)
        sort_by = request.args.get('sort_by', default='-created_at')
        
        # Build filter
        filter_query = {'workshop_type': 'product_painting'}
        if product_type:
            filter_query['product_type'] = product_type
        
        # Get total count
        total = mongo.db.paintings.count_documents(filter_query)
        
        # Parse sort
        sort_field = sort_by.lstrip('-')
        sort_direction = -1 if sort_by.startswith('-') else 1
        
        # Query paintings
        paintings = serialize_documents(
            mongo.db.paintings
            .find(filter_query)
            .sort(sort_field, sort_direction)
            .skip(offset)
            .limit(limit)
        )
        
        return jsonify({
            'status': 'success',
            'paintings': paintings,
            'total': total,
            'returned': len(paintings)
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/paintings/<painting_id>', methods=['GET'])
def get_painting(painting_id):
    #Get specific painting
    try:
        painting = serialize_document(mongo.db.paintings.find_one({'_id': ObjectId(painting_id)}))
        
        if not painting:
            return jsonify({'status': 'error', 'message': 'Painting not found'}), 404
        
        # Increment views
        mongo.db.paintings.update_one(
            {'_id': ObjectId(painting_id)},
            {'$inc': {'views': 1}}
        )
        
        return jsonify({
            'status': 'success',
            'painting': painting
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/paintings/<painting_id>', methods=['DELETE'])
@login_required
def delete_painting(painting_id):
    #Delete a painting (only by creator)
    try:
        painting = mongo.db.paintings.find_one({'_id': ObjectId(painting_id)})
        
        if not painting:
            return jsonify({'status': 'error', 'message': 'Painting not found'}), 404
        
        # Check if user is creator
        if str(painting['creator_id']) != session['user_id']:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
        
        mongo.db.paintings.delete_one({'_id': ObjectId(painting_id)})
        
        # Decrement user creation count
        mongo.db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$inc': {'total_creations': -1}}
        )
        
        return jsonify({'status': 'success', 'message': 'Painting deleted'}), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================
# API: Flower Upload & Management
# ============================================

@app.route('/api/flowers', methods=['POST'])
@login_required
def upload_flower():
    # Upload custom flower design
    try:
        if 'flower_image' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400
        
        file = request.files['flower_image']
        
        if not file or not allowed_file(file.filename):
            return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400
        
        # Save file
        filename = secure_filename(f"{datetime.utcnow().timestamp()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'flowers', filename)
        file.save(filepath)
        
        # Compress if image
        if filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}:
            compress_image(filepath)
        
        # Read file as base64
        with open(filepath, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Create flower document
        flower = {
            'name': request.form.get('name', 'Custom Flower'),
            'image_data': image_data,
            'uploader_id': ObjectId(session['user_id']),
            'is_preset': False,
            'created_at': datetime.utcnow(),
            'usage_count': 0,
            'thumbnail': image_data  # Same as full image for now
        }
        
        result = mongo.db.flowers.insert_one(flower)
        
        # Update user upload count
        mongo.db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$inc': {'total_uploads': 1}}
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Flower uploaded successfully',
            'flower_id': str(result.inserted_id)
        }), 201
    
    except Exception as e:
        app.logger.error(f"Error uploading flower: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/flowers', methods=['GET'])
def get_flowers():
    # Get all available flowers
    try:
        limit = request.args.get('limit', default=50, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        flowers = serialize_documents(
            mongo.db.flowers
            .find()
            .sort('usage_count', -1)
            .skip(offset)
            .limit(limit)
        )
        
        return jsonify({
            'status': 'success',
            'flowers': flowers
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================
# API: Charm Upload & Management
# ============================================

@app.route('/api/charms', methods=['POST'])
@login_required
def upload_charm():
    # Upload custom charm design
    try:
        if 'charm_image' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400
        
        file = request.files['charm_image']
        
        if not file or not allowed_file(file.filename):
            return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400
        
        # Save file
        filename = secure_filename(f"{datetime.utcnow().timestamp()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'charms', filename)
        file.save(filepath)
        
        # Compress if image
        if filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}:
            compress_image(filepath)
        
        # Read file as base64
        with open(filepath, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Create charm document
        charm = {
            'name': request.form.get('name', 'Custom Charm'),
            'image_data': image_data,
            'uploader_id': ObjectId(session['user_id']),
            'is_preset': False,
            'created_at': datetime.utcnow(),
            'usage_count': 0,
            'thumbnail': image_data,
            'shape': request.form.get('shape', 'circle')
        }
        
        result = mongo.db.charms.insert_one(charm)
        
        # Update user upload count
        mongo.db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$inc': {'total_uploads': 1}}
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Charm uploaded successfully',
            'charm_id': str(result.inserted_id)
        }), 201
    
    except Exception as e:
        app.logger.error(f"Error uploading charm: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/charms', methods=['GET'])
def get_charms():
    # Get all available charms
    try:
        limit = request.args.get('limit', default=50, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        charms = serialize_documents(
            mongo.db.charms
            .find()
            .sort('usage_count', -1)
            .skip(offset)
            .limit(limit)
        )
        
        return jsonify({
            'status': 'success',
            'charms': charms
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================
# API: Arrangements
# ============================================

@app.route('/api/arrangements', methods=['POST'])
@login_required
def create_arrangement():
    # Create and save flower arrangement
    try:
        data = request.get_json()
        
        required = ['title', 'arrangement_data', 'image_snapshot']
        if not all(field in data for field in required):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        arrangement = {
            'creator_id': ObjectId(session['user_id']),
            'workshop_type': 'flower_arranging',
            'arrangement_data': data['arrangement_data'],
            'title': data['title'],
            'description': data.get('description', ''),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'likes': 0,
            'views': 0,
            'image_snapshot': data['image_snapshot'],
            'comments': []
        }
        
        result = mongo.db.arrangements.insert_one(arrangement)
        
        mongo.db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$inc': {'total_creations': 1}}
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Arrangement saved successfully',
            'arrangement_id': str(result.inserted_id)
        }), 201
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/arrangements', methods=['GET'])
def get_arrangements():
    # Get all arrangements
    try:
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        arrangements = serialize_documents(
            mongo.db.arrangements
            .find()
            .sort('created_at', -1)
            .skip(offset)
            .limit(limit)
        )
        
        return jsonify({
            'status': 'success',
            'arrangements': arrangements
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================
# API: Bracelets
# ============================================

@app.route('/api/bracelets', methods=['POST'])
@login_required
def create_bracelet():
    # Create and save charm bracelet
    try:
        data = request.get_json()
        
        required = ['title', 'bracelet_data', 'image_snapshot']
        if not all(field in data for field in required):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        bracelet = {
            'creator_id': ObjectId(session['user_id']),
            'workshop_type': 'charm_bracelet',
            'bracelet_data': data['bracelet_data'],
            'title': data['title'],
            'description': data.get('description', ''),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'likes': 0,
            'views': 0,
            'image_snapshot': data['image_snapshot'],
            'comments': []
        }
        
        result = mongo.db.bracelets.insert_one(bracelet)
        
        mongo.db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$inc': {'total_creations': 1}}
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Bracelet saved successfully',
            'bracelet_id': str(result.inserted_id)
        }), 201
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/bracelets', methods=['GET'])
def get_bracelets():
    # Get all bracelets
    try:
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        bracelets = serialize_documents(
            mongo.db.bracelets
            .find()
            .sort('created_at', -1)
            .skip(offset)
            .limit(limit)
        )
        
        return jsonify({
            'status': 'success',
            'bracelets': bracelets
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================
# API: Community & Social
# ============================================

@app.route('/api/users/trending', methods=['GET'])
def get_trending():
    #Get trending creations
    try:
        limit = request.args.get('limit', default=12, type=int)
        
        # Get trending creations from all types
        paintings = list(mongo.db.paintings.find().sort('likes', -1).limit(limit // 3))
        arrangements = list(mongo.db.arrangements.find().sort('likes', -1).limit(limit // 3))
        bracelets = list(mongo.db.bracelets.find().sort('likes', -1).limit(limit // 3))
        
        trending = paintings + arrangements + bracelets
        trending = serialize_documents(trending)
        
        return jsonify({
            'status': 'success',
            'creations': trending
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/users/stats', methods=['GET'])
def get_community_stats():
    # Get community statistics
    try:
        stats = {
            'total_paintings': mongo.db.paintings.count_documents({}),
            'total_arrangements': mongo.db.arrangements.count_documents({}),
            'total_bracelets': mongo.db.bracelets.count_documents({}),
            'total_users': mongo.db.users.count_documents({}),
            'total_uploads': mongo.db.flowers.count_documents({}) + mongo.db.charms.count_documents({}),
            'total_likes': (
                sum(p['likes'] for p in mongo.db.paintings.find()) +
                sum(a['likes'] for a in mongo.db.arrangements.find()) +
                sum(b['likes'] for b in mongo.db.bracelets.find())
            )
        }
        
        return jsonify({
            'status': 'success',
            'stats': stats
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/users/<creation_id>/like', methods=['POST'])
@login_required
def like_creation(creation_id):
    #Like a creation#
    try:
        data = request.get_json()
        creation_type = data.get('creation_type')
        
        # Determine collection
        collection_map = {
            'painting': mongo.db.paintings,
            'arrangement': mongo.db.arrangements,
            'bracelet': mongo.db.bracelets
        }
        
        collection = collection_map.get(creation_type)
        if not collection:
            return jsonify({'status': 'error', 'message': 'Invalid creation type'}), 400
        
        result = collection.update_one(
            {'_id': ObjectId(creation_id)},
            {'$inc': {'likes': 1}}
        )
        
        if result.matched_count:
            return jsonify({'status': 'success', 'message': 'Liked successfully'}), 200
        
        return jsonify({'status': 'error', 'message': 'Creation not found'}), 404
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    return "Internal server error", 500

# ============================================
# RUN APPLICATION
# ============================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)