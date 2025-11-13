from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request

socketio = None

def init_socketio(app):
    """Initialize Socket.IO with Flask app"""
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

    @socketio.on('connect')
    def handle_connect():
        print(f"🔌 Client connected: {request.sid}")
        emit('connected', {'message': 'Connected to Flash Sale server'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"🔌 Client disconnected: {request.sid}")

    @socketio.on('join')
    def handle_join(data):
        """Join user-specific room"""
        user_id = data.get('userId')
        if user_id:
            join_room(f"user_{user_id}")
            print(f"👤 User {user_id} joined their room")
            emit('joined', {'userId': user_id, 'room': f"user_{user_id}"})

    @socketio.on('leave')
    def handle_leave(data):
        """Leave user-specific room"""
        user_id = data.get('userId')
        if user_id:
            leave_room(f"user_{user_id}")
            print(f"👤 User {user_id} left their room")

    @socketio.on('trackCheckout')
    def handle_track_checkout(data):
        """Track checkout start time"""
        user_id = data.get('userId')
        print(f"⏱️  Tracking checkout for user: {user_id}")
        emit('checkoutTracked', {'userId': user_id, 'timestamp': data.get('timestamp')})

    print("✅ Socket.IO initialized")
    return socketio

def get_socketio():
    """Get Socket.IO instance"""
    return socketio

def emit_stock_update(product_id, stock):
    """Emit stock update to all connected clients"""
    if socketio:
        try:
            socketio.emit('stockUpdate', {
                'productId': str(product_id),
                'stock': stock
            }, namespace='/')
            print(f"📢 Stock update emitted for product {product_id}: {stock}")
        except Exception as e:
            print(f"⚠️  Failed to emit stock update: {e}")

def emit_order_success(user_id, order_data):
    """Emit order success to specific user"""
    if socketio:
        try:
            socketio.emit('orderSuccess', order_data, room=f"user_{user_id}", namespace='/')
            print(f"📢 Order success emitted to user {user_id}")
        except Exception as e:
            print(f"⚠️  Failed to emit order success: {e}")

def emit_leaderboard_update():
    """Emit leaderboard update to all clients"""
    if socketio:
        try:
            socketio.emit('leaderboardUpdate', {}, namespace='/')
            print(f"📢 Leaderboard update emitted")
        except Exception as e:
            print(f"⚠️  Failed to emit leaderboard update: {e}")

def emit_product_sold_out(product_id, product_name):
    """Emit product sold out notification"""
    if socketio:
        try:
            socketio.emit('productSoldOut', {
                'productId': str(product_id),
                'productName': product_name
            }, namespace='/')
            print(f"📢 Product sold out emitted: {product_name}")
        except Exception as e:
            print(f"⚠️  Failed to emit product sold out: {e}")

def emit_sale_ended():
    """Emit sale ended notification"""
    if socketio:
        try:
            socketio.emit('saleEnded', {}, namespace='/')
            print(f"📢 Sale ended emitted")
        except Exception as e:
            print(f"⚠️  Failed to emit sale ended: {e}")
