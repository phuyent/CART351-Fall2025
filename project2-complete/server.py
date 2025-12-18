# CART 351 - PROJECT II: COLLABORATIVE PAINTING WORKSHOP
# ======================================================
# A web-based painting application where users can create digital paintings
# and share them in a collective gallery.
# Student: Huyen Tran Pham

# Features:
#  Interactive canvas painting with multiple brush sizes
#  Color palette selection
#  Canvas size customization
#  Save paintings permanently to JSON file (serverside)
#  View gallery of all user paintings
#  Real-time collective art experience

# Technologies:
#  Flask (Backend)
#  p5.js (Canvas drawing)
#  Fetch API (Data transmission)
#  JSON (Data storage)


from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this'

# File path for storing paintings
PAINTINGS_FILE = 'data/paintings.json'


# ============================================
# HELPER FUNCTIONS
# ============================================

def ensure_data_directory():
    # Ensure the data directory exists
    os.makedirs('data', exist_ok=True)


def load_paintings():
    # Load all paintings from JSON file
    ensure_data_directory()
    
    if not os.path.exists(PAINTINGS_FILE):
        return []
    
    try:
        with open(PAINTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []
    except Exception as e:
        print(f"Error loading paintings: {e}")
        return []


def save_paintings(paintings):
    # Save all paintings to JSON file
    ensure_data_directory()
    
    try:
        with open(PAINTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(paintings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving paintings: {e}")
        return False


def generate_painting_id():
    # Generate unique ID for painting
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"painting_{timestamp}"


# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    # Home page - Workshop selection
    return render_template('index.html')


@app.route('/workshop')
def workshop():
    # Main painting workshop page
    return render_template('workshop.html')


@app.route('/gallery')
def gallery():
    # Gallery page showing all paintings
    return render_template('gallery.html')


# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/save-painting', methods=['POST'])
def save_painting():

    # API endpoint to save a painting
    
    # Expected POST data (JSON):
    # {
    #     "artist_name": "User's name",
    #     "painting_title": "Title of painting",
    #     "canvas_size": {"width": 800, "height": 600},
    #     "image_data": "base64 encoded image data",
    #     "colors_used": ["#FF0000", "#00FF00"],
    #     "brush_size": 5,
    #     "creation_time": "timestamp"
    # }

    try:
        # 1. Get data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data received"
            }), 400
        
        # 2. Validate required fields
        required_fields = ['artist_name', 'painting_title', 'image_data']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }), 400
        
        # 3. Load existing paintings
        paintings = load_paintings()
        
        # 4. Create new painting object
        new_painting = {
            "id": generate_painting_id(),
            "artist_name": data['artist_name'],
            "painting_title": data['painting_title'],
            "canvas_size": data.get('canvas_size', {"width": 800, "height": 600}),
            "image_data": data['image_data'],
            "colors_used": data.get('colors_used', []),
            "brush_size": data.get('brush_size', 5),
            "timestamp": datetime.now().isoformat(),
            "creation_time": data.get('creation_time', 0)
        }
        
        # 5. Add to paintings list
        paintings.append(new_painting)
        
        # 6. Save to JSON file
        if save_paintings(paintings):
            app.logger.info(f"Saved painting: {new_painting['id']} by {new_painting['artist_name']}")
            
            return jsonify({
                "status": "success",
                "message": "Painting saved successfully!",
                "painting_id": new_painting['id'],
                "total_paintings": len(paintings)
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to save painting to file"
            }), 500
    
    except Exception as e:
        app.logger.error(f"Error saving painting: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Server error occurred",
            "error": str(e)
        }), 500


@app.route('/api/get-paintings', methods=['GET'])
def get_paintings():

    # API endpoint to retrieve all paintings
    
    # Returns JSON array of all paintings
    # Supports optional query parameters:
    #  limit: Maximum number of paintings to return
    #  offset: Starting position for pagination

    try:
        # 1. Load paintings from file
        paintings = load_paintings()
        
        # 2. Get query parameters
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # 3. Apply pagination if requested
        if limit:
            paintings = paintings[offset:offset + limit]
        
        # 4. Return paintings
        return jsonify({
            "status": "success",
            "paintings": paintings,
            "total": len(load_paintings()),  # Total count
            "returned": len(paintings)        # Returned count
        }), 200
    
    except Exception as e:
        app.logger.error(f"Error retrieving paintings: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve paintings",
            "error": str(e)
        }), 500


@app.route('/api/get-painting/<painting_id>', methods=['GET'])
def get_painting(painting_id):
    # API endpoint to retrieve a specific painting by ID

    try:
        paintings = load_paintings()
        
        # Find painting with matching ID
        painting = next((p for p in paintings if p['id'] == painting_id), None)
        
        if painting:
            return jsonify({
                "status": "success",
                "painting": painting
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Painting not found"
            }), 404
    
    except Exception as e:
        app.logger.error(f"Error retrieving painting: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve painting",
            "error": str(e)
        }), 500


@app.route('/api/gallery-stats', methods=['GET'])
def gallery_stats():
 
    # API endpoint to get gallery statistics
    
    # Returns:
    #  Total number of paintings
    #  List of all artists
    #  Most used colors
    #  Average painting time
  
    try:
        paintings = load_paintings()
        
        # Calculate statistics
        total_paintings = len(paintings)
        artists = list(set(p['artist_name'] for p in paintings))
        
        # Collect all colors used
        all_colors = []
        for p in paintings:
            all_colors.extend(p.get('colors_used', []))
        
        # Count color frequency
        color_counts = {}
        for color in all_colors:
            color_counts[color] = color_counts.get(color, 0) + 1
        
        # Sort by frequency
        popular_colors = sorted(
            color_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]  # Top 10 colors
        
        # Calculate average creation time
        creation_times = [p.get('creation_time', 0) for p in paintings]
        avg_time = sum(creation_times) / len(creation_times) if creation_times else 0
        
        return jsonify({
            "status": "success",
            "stats": {
                "total_paintings": total_paintings,
                "total_artists": len(artists),
                "artists": artists,
                "popular_colors": [{"color": c, "count": count} for c, count in popular_colors],
                "average_creation_time": round(avg_time, 2)
            }
        }), 200
    
    except Exception as e:
        app.logger.error(f"Error getting stats: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to retrieve statistics",
            "error": str(e)
        }), 500


@app.route('/api/delete-painting/<painting_id>', methods=['DELETE'])
def delete_painting(painting_id):

    # API endpoint to delete a specific painting
    # (Optional - for admin purposes)
   
    try:
        paintings = load_paintings()
        
        # Filter out the painting to delete
        original_count = len(paintings)
        paintings = [p for p in paintings if p['id'] != painting_id]
        
        if len(paintings) < original_count:
            save_paintings(paintings)
            return jsonify({
                "status": "success",
                "message": "Painting deleted successfully"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Painting not found"
            }), 404
    
    except Exception as e:
        app.logger.error(f"Error deleting painting: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Failed to delete painting",
            "error": str(e)
        }), 500


# ============================================
# RUN APPLICATION
# ============================================

if __name__ == '__main__':
    # Ensure data directory exists on startup
    ensure_data_directory()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)