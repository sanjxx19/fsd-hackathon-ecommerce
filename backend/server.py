from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import configuration
from config.db import db
from config.socket import init_socketio

# Import middleware
from middleware.error_handler import register_error_handlers

# Import routes
from routes.auth import auth_bp
from routes.products import products_bp
from routes.cart import cart_bp
from routes.orders import orders_bp
from routes.leaderboard import leaderboard_bp
from routes.analytics import analytics_bp
from routes.payment import payment_bp

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET', 'your_super_secret_jwt_key_change_this_in_production')
app.config['JSON_SORT_KEYS'] = False

# Enable CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Connect to database
try:
    db.connect()
except Exception as e:
    print(f"Failed to connect to database: {e}")
    exit(1)

# Initialize Socket.IO
socketio = init_socketio(app)

# Register error handlers
register_error_handlers(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(products_bp, url_prefix='/api/products')
app.register_blueprint(cart_bp, url_prefix='/api/cart')
app.register_blueprint(orders_bp, url_prefix='/api/orders')
app.register_blueprint(leaderboard_bp, url_prefix='/api/leaderboard')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(payment_bp, url_prefix='/api/payment')

# Root endpoint
@app.route('/')
def index():
    return jsonify({
        'message': 'Flash Sale API',
        'version': '1.0.0',
        'status': 'running'
    })

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'database': 'connected'
    }), 200

# API info endpoint
@app.route('/api')
def api_info():
    return jsonify({
        'message': 'Flash Sale API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'products': '/api/products',
            'cart': '/api/cart',
            'orders': '/api/orders',
            'leaderboard': '/api/leaderboard',
            'analytics': '/api/analytics',
            'payment': '/api/payment'
        }
    })

# Graceful shutdown
import signal
import sys

def signal_handler(sig, frame):
    print('\n🛑 Shutting down server...')
    db.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Run server
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('NODE_ENV', 'development') == 'development'

    print(f"""
╔═══════════════════════════════════════════════════════╗
║          🚀 Flash Sale Backend Server                 ║
║                                                       ║
║  Server:    http://localhost:{port}                      ║
║  Status:    Running                                   ║
║  Mode:      {'Development' if debug else 'Production'}                                ║
║  Database:  MongoDB Connected                         ║
║  Socket.IO: Enabled                                   ║
╚═══════════════════════════════════════════════════════╝
""")

    # Run with eventlet for Socket.IO support
    socketio.run(app, host='0.0.0.0', port=port, debug=debug)
