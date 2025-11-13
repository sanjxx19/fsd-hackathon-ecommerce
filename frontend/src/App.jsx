import React, { useState, useEffect, createContext, useContext } from 'react';
import { ShoppingCart as CartIcon, LogIn, UserPlus, TrendingUp, Clock, Package, CreditCard, Users, BarChart3, Bell, MessageSquare, X, ChevronRight, Trophy, Zap, CheckCircle, AlertCircle, Menu } from 'lucide-react';

// API Base URL - Update this to your backend URL
const API_BASE_URL = 'http://localhost:5000/api';

// Auth Context
const AuthContext = createContext(null);

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      fetchCurrentUser();
    }
  }, [token]);

  const fetchCurrentUser = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data.user);
      } else {
        logout();
      }
    } catch (err) {
      console.error('Failed to fetch user:', err);
    }
  };

  const login = async (email, password) => {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (res.ok) {
        setToken(data.token);
        setUser(data.user);
        localStorage.setItem('token', data.token);
        return { success: true };
      }
      return { success: false, message: data.error || 'Login failed' };
    } catch (err) {
      return { success: false, message: 'Network error. Please try again.' };
    }
  };

  const register = async (name, email, password) => {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
      });
      const data = await res.json();
      if (res.ok) {
        setToken(data.token);
        setUser(data.user);
        localStorage.setItem('token', data.token);
        return { success: true };
      }
      return { success: false, message: data.error || 'Registration failed' };
    } catch (err) {
      return { success: false, message: 'Network error. Please try again.' };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => useContext(AuthContext);

// Notification System
const NotificationContext = createContext(null);

const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);

  const addNotification = (message, type = 'info') => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  return (
    <NotificationContext.Provider value={{ addNotification }}>
      {children}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {notifications.map(notif => (
          <div
            key={notif.id}
            className={`p-4 rounded-lg shadow-lg flex items-center gap-3 animate-slide-in ${
              notif.type === 'success' ? 'bg-green-500' :
              notif.type === 'error' ? 'bg-red-500' :
              notif.type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
            } text-white`}
          >
            <Bell size={20} />
            <span>{notif.message}</span>
          </div>
        ))}
      </div>
    </NotificationContext.Provider>
  );
};

const useNotification = () => useContext(NotificationContext);

// Login/Register Component
const AuthModal = ({ isOpen, onClose, mode: initialMode }) => {
  const [mode, setMode] = useState(initialMode);
  const [formData, setFormData] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const { addNotification } = useNotification();

  useEffect(() => {
    setMode(initialMode);
    setError('');
  }, [initialMode]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let result;
      if (mode === 'login') {
        result = await login(formData.email, formData.password);
      } else {
        if (formData.password.length < 6) {
          setError('Password must be at least 6 characters');
          setLoading(false);
          return;
        }
        result = await register(formData.name, formData.email, formData.password);
      }

      if (result.success) {
        addNotification(`${mode === 'login' ? 'Logged in' : 'Registered'} successfully!`, 'success');
        onClose();
      } else {
        setError(result.message || 'Authentication failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
    setLoading(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            {mode === 'login' ? 'Welcome Back' : 'Create Account'}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <input
              type="text"
              placeholder="Full Name"
              required
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          )}
          <input
            type="email"
            placeholder="Email"
            required
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
          <input
            type="password"
            placeholder="Password"
            required
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          />
          
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 disabled:opacity-50"
          >
            {loading ? 'Processing...' : mode === 'login' ? 'Login' : 'Register'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setMode(mode === 'login' ? 'register' : 'login');
              setError('');
            }}
            className="text-purple-600 hover:text-purple-700 font-medium"
          >
            {mode === 'login' ? "Don't have an account? Register" : 'Already have an account? Login'}
          </button>
        </div>
      </div>
    </div>
  );
};

// Countdown Timer Component
const CountdownTimer = ({ endTime }) => {
  const [timeLeft, setTimeLeft] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date().getTime();
      const end = new Date(endTime).getTime();
      const diff = Math.max(0, end - now);
      setTimeLeft(diff);
    }, 1000);

    return () => clearInterval(interval);
  }, [endTime]);

  const hours = Math.floor(timeLeft / (1000 * 60 * 60));
  const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

  return (
    <div className="flex items-center gap-2 bg-gradient-to-r from-red-500 to-orange-500 text-white px-4 py-2 rounded-full">
      <Clock size={18} />
      <span className="font-bold">
        {hours.toString().padStart(2, '0')}:{minutes.toString().padStart(2, '0')}:{seconds.toString().padStart(2, '0')}
      </span>
    </div>
  );
};

// Product Card Component
const ProductCard = ({ product, onAddToCart }) => {
  const [adding, setAdding] = useState(false);

  const handleAddToCart = async () => {
    setAdding(true);
    await onAddToCart(product);
    setAdding(false);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-2xl transition-all">
      <div className="relative">
        <div className="w-full h-48 bg-gradient-to-br from-purple-100 to-pink-100 flex items-center justify-center text-6xl">
          {product.image}
        </div>
        {product.stock < 10 && product.stock > 0 && (
          <div className="absolute top-2 right-2 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold animate-pulse">
            Only {product.stock} left!
          </div>
        )}
        {product.stock === 0 && (
          <div className="absolute inset-0 bg-black bg-opacity-60 flex items-center justify-center">
            <span className="text-white text-xl font-bold">SOLD OUT</span>
          </div>
        )}
      </div>
      <div className="p-4">
        <h3 className="font-bold text-lg mb-2">{product.name}</h3>
        <p className="text-gray-600 text-sm mb-3">{product.description}</p>
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="text-2xl font-bold text-purple-600">${product.price}</div>
            <div className="text-sm text-gray-500 line-through">${product.originalPrice}</div>
          </div>
          <div className="text-sm font-semibold text-green-600 bg-green-50 px-2 py-1 rounded">
            {product.discountPercent}% OFF
          </div>
        </div>
        <div className="mb-3 text-sm text-gray-600">
          <span className="font-semibold">Stock:</span> {product.stock} units
        </div>
        <button
          onClick={handleAddToCart}
          disabled={product.stock === 0 || adding}
          className="w-full bg-purple-600 text-white py-2 rounded-lg font-semibold hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {adding ? 'Adding...' : product.stock === 0 ? 'Sold Out' : 'Add to Cart'}
        </button>
      </div>
    </div>
  );
};

// Shopping Cart Component
const ShoppingCart = ({ isOpen, onClose }) => {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const { token } = useAuth();
  const { addNotification } = useNotification();

  useEffect(() => {
    if (isOpen && token) {
      fetchCart();
    }
  }, [isOpen, token]);

  const fetchCart = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/cart`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      if (res.ok) {
        setCart(data.cart);
      }
    } catch (err) {
      console.error('Failed to fetch cart:', err);
    }
  };

  const updateQuantity = async (productId, quantity) => {
    try {
      const res = await fetch(`${API_BASE_URL}/cart/item/${productId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ quantity })
      });
      if (res.ok) {
        fetchCart();
        addNotification('Cart updated', 'success');
      }
    } catch (err) {
      console.error('Failed to update quantity:', err);
    }
  };

  const removeItem = async (productId) => {
    try {
      const res = await fetch(`${API_BASE_URL}/cart/item/${productId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        fetchCart();
        addNotification('Item removed from cart', 'success');
      }
    } catch (err) {
      console.error('Failed to remove item:', err);
    }
  };

  const checkout = async () => {
    setLoading(true);
    try {
      const checkoutStartTime = new Date().toISOString();
      const res = await fetch(`${API_BASE_URL}/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          checkoutStartTime,
          paymentMethod: 'card'
        })
      });
      const data = await res.json();
      if (res.ok) {
        addNotification(`Order placed! Checkout time: ${data.order.checkoutTime}s`, 'success');
        setCart(null);
        onClose();
      } else {
        addNotification(data.error || 'Checkout failed', 'error');
      }
    } catch (err) {
      addNotification('Checkout failed', 'error');
    }
    setLoading(false);
  };

  const cartItems = cart?.items || [];
  const total = cart?.total || 0;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-end justify-end z-50">
      <div className="bg-white h-full w-full max-w-md shadow-2xl flex flex-col">
        <div className="p-6 border-b flex items-center justify-between">
          <h2 className="text-2xl font-bold">Shopping Cart</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {cartItems.length === 0 ? (
            <div className="text-center text-gray-500 mt-12">
              <CartIcon size={64} className="mx-auto mb-4 opacity-30" />
              <p>Your cart is empty</p>
            </div>
          ) : (
            <div className="space-y-4">
              {cartItems.map(item => (
                <div key={item.product._id} className="flex gap-4 border-b pb-4">
                  <div className="w-20 h-20 bg-gradient-to-br from-purple-100 to-pink-100 rounded flex items-center justify-center text-3xl">
                    {item.product.image}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold">{item.product.name}</h3>
                    <p className="text-purple-600 font-bold">${item.price}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <button
                        onClick={() => updateQuantity(item.product._id, item.quantity - 1)}
                        className="px-2 py-1 bg-gray-200 rounded hover:bg-gray-300"
                      >
                        -
                      </button>
                      <span className="px-3">{item.quantity}</span>
                      <button
                        onClick={() => updateQuantity(item.product._id, item.quantity + 1)}
                        className="px-2 py-1 bg-gray-200 rounded hover:bg-gray-300"
                      >
                        +
                      </button>
                      <button
                        onClick={() => removeItem(item.product._id)}
                        className="ml-auto text-red-500 hover:text-red-700"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {cartItems.length > 0 && (
          <div className="p-6 border-t">
            <div className="flex justify-between items-center mb-4">
              <span className="text-xl font-bold">Total:</span>
              <span className="text-2xl font-bold text-purple-600">${total.toFixed(2)}</span>
            </div>
            <button
              onClick={checkout}
              disabled={loading}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 disabled:opacity-50"
            >
              {loading ? 'Processing...' : 'Checkout'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Leaderboard Component
const Leaderboard = () => {
  const [leaders, setLeaders] = useState([]);
  const [sortBy, setSortBy] = useState('totalPurchases');

  useEffect(() => {
    fetchLeaderboard();
  }, [sortBy]);

  const fetchLeaderboard = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/leaderboard?sortBy=${sortBy}`);
      const data = await res.json();
      if (res.ok) {
        setLeaders(data.leaderboard || []);
      }
    } catch (err) {
      console.error('Failed to fetch leaderboard:', err);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Trophy className="text-yellow-500" />
          Leaderboard
        </h2>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="totalPurchases">Top Buyers</option>
          <option value="checkoutTime">Fastest Checkouts</option>
        </select>
      </div>

      <div className="space-y-3">
        {leaders.slice(0, 10).map((leader, idx) => (
          <div key={leader.user.id} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
              idx === 0 ? 'bg-yellow-400 text-white' :
              idx === 1 ? 'bg-gray-300 text-white' :
              idx === 2 ? 'bg-orange-400 text-white' :
              'bg-gray-200 text-gray-600'
            }`}>
              {idx + 1}
            </div>
            <div className="flex-1">
              <div className="font-semibold">{leader.user.name}</div>
              <div className="text-sm text-gray-600">
                {sortBy === 'totalPurchases' 
                  ? `$${leader.totalPurchases.toFixed(2)} spent • ${leader.totalOrders} orders`
                  : leader.fastestCheckout ? `${leader.fastestCheckout.toFixed(2)}s fastest checkout` : 'No checkout yet'}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Analytics Dashboard Component
const AnalyticsDashboard = () => {
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/analytics/sales`);
      const data = await res.json();
      if (res.ok) {
        setAnalytics(data.analytics);
      }
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
    }
  };

  if (!analytics) return <div className="text-center py-12">Loading analytics...</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold flex items-center gap-2">
        <BarChart3 className="text-purple-600" />
        Analytics Dashboard
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-purple-500 to-purple-700 text-white rounded-xl p-6">
          <div className="text-sm opacity-90">Total Sales</div>
          <div className="text-3xl font-bold mt-2">${analytics.totalSales?.toFixed(2)}</div>
          <div className="text-sm mt-1">{analytics.totalOrders} orders</div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-blue-700 text-white rounded-xl p-6">
          <div className="text-sm opacity-90">Avg Order Value</div>
          <div className="text-3xl font-bold mt-2">${analytics.averageOrderValue?.toFixed(2)}</div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-700 text-white rounded-xl p-6">
          <div className="text-sm opacity-90">Avg Checkout</div>
          <div className="text-3xl font-bold mt-2">{analytics.averageCheckoutTime?.toFixed(1)}s</div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-700 text-white rounded-xl p-6">
          <div className="text-sm opacity-90">Peak Hour</div>
          <div className="text-3xl font-bold mt-2">{analytics.peakHour || 'N/A'}</div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold mb-4">Top Products</h3>
        <div className="space-y-3">
          {(analytics.topProducts || []).map((product, idx) => (
            <div key={idx} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center font-bold text-purple-600">
                {idx + 1}
              </div>
              <div className="flex-1">
                <div className="font-semibold">{product.product.name}</div>
                <div className="text-sm text-gray-600">
                  {product.unitsSold} sold • ${product.revenue.toFixed(2)} revenue
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {analytics.hourlyBreakdown && analytics.hourlyBreakdown.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold mb-4">Hourly Sales</h3>
          <div className="space-y-2">
            {analytics.hourlyBreakdown.map(hour => (
              <div key={hour.hour} className="flex items-center gap-4">
                <div className="w-16 text-sm font-medium text-gray-600">{hour.hour}</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <div 
                      className="h-8 bg-gradient-to-r from-purple-400 to-pink-400 rounded"
                      style={{ width: `${(hour.sales / Math.max(...analytics.hourlyBreakdown.map(h => h.sales))) * 100}%` }}
                    ></div>
                    <span className="text-sm font-semibold">${hour.sales.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// AI Chatbot Component
const AIChatbot = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I can help you with product information, order status, and flash sale details. How can I assist you?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    setTimeout(() => {
      const lowerInput = input.toLowerCase();
      let response = '';

      if (lowerInput.includes('sale') || lowerInput.includes('discount')) {
        response = "Our flash sale is live now with discounts up to 70% off! Hurry, limited stock available. Check out our Electronics and Accessories categories for the best deals!";
      } else if (lowerInput.includes('shipping') || lowerInput.includes('delivery')) {
        response = "We offer free shipping on all orders! Standard delivery takes 3-5 business days. Express shipping is available for faster delivery.";
      } else if (lowerInput.includes('return') || lowerInput.includes('refund')) {
        response = "We have a 30-day return policy. If you're not satisfied, you can return your items for a full refund. No questions asked!";
      } else if (lowerInput.includes('payment') || lowerInput.includes('card')) {
        response = "We accept all major credit cards, debit cards, and digital wallets. All transactions are secure and encrypted.";
      } else if (lowerInput.includes('track') || lowerInput.includes('order')) {
        response = "You can track your orders in the 'My Orders' section after logging in. You'll receive updates via email too!";
      } else if (lowerInput.includes('stock') || lowerInput.includes('available')) {
        response = "Stock is limited during flash sales! Items showing 'Only X left' are selling fast. Add them to your cart quickly to secure your purchase.";
      } else if (lowerInput.includes('checkout') || lowerInput.includes('fast')) {
        response = "Pro tip: Save your payment details for faster checkout! The fastest shoppers get featured on our leaderboard. Current record is under 5 seconds!";
      } else {
        const responses = [
          "Our flash sale ends soon! Don't miss out on amazing deals up to 70% off.",
          "Check out our top-rated products - customers love our Premium Headphones and Smart Watch Pro!",
          "Need help finding something specific? I can recommend products based on your interests.",
          "All our products come with warranty and free shipping. Shop with confidence!",
          "Want to know a secret? New flash sales drop every week. Follow us to stay updated!"
        ];
        response = responses[Math.floor(Math.random() * responses.length)];
      }
      
      const aiMessage = { role: 'assistant', content: response };
      setMessages(prev => [...prev, aiMessage]);
      setLoading(false);
    }, 1000);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 w-96 h-[500px] bg-white rounded-xl shadow-2xl flex flex-col z-50">
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-4 rounded-t-xl flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MessageSquare size={24} />
          <span className="font-bold">AI Shopping Assistant</span>
        </div>
        <button onClick={onClose} className="hover:bg-white/20 rounded p-1">
          <X size={20} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg ${
              msg.role === 'user' 
                ? 'bg-purple-600 text-white rounded-br-none' 
                : 'bg-gray-100 text-gray-800 rounded-bl-none'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-3 rounded-lg">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask me anything..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            onClick={sendMessage}
            disabled={loading}
            className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

// Main App Component
const App = () => {
  const [currentPage, setCurrentPage] = useState('products');
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [cartOpen, setCartOpen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [products, setProducts] = useState([]);
  const [saleEndTime] = useState(new Date(Date.now() + 8 * 60 * 60 * 1000));
  const [menuOpen, setMenuOpen] = useState(false);

  const { user, logout, token } = useAuth();
  const { addNotification } = useNotification();

  useEffect(() => {
    fetchProducts();
    const interval = setInterval(fetchProducts, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchProducts = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/products`);
      const data = await res.json();
      if (res.ok) {
        setProducts(data.products || []);
      }
    } catch (err) {
      console.error('Failed to fetch products:', err);
    }
  };

  const addToCart = async (product) => {
    if (!token) {
      setAuthMode('login');
      setAuthModalOpen(true);
      addNotification('Please login to add items to cart', 'warning');
      return;
    }

    try {
      console.log('Adding to cart:', { productId: product._id, quantity: 1 });
      
      const res = await fetch(`${API_BASE_URL}/cart/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ productId: product._id, quantity: 1 })
      });
      
      const data = await res.json();
      console.log('Add to cart response:', data);
      
      if (res.ok) {
        addNotification(`${product.name} added to cart!`, 'success');
        fetchProducts(); // Refresh products to show updated stock
      } else {
        addNotification(data.error || 'Failed to add to cart', 'error');
      }
    } catch (err) {
      console.error('Cart error:', err);
      addNotification('Network error. Please try again.', 'error');
    }
  };

  const openAuth = (mode) => {
    setAuthMode(mode);
    setAuthModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      <header className="bg-white shadow-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button 
                onClick={() => setMenuOpen(!menuOpen)}
                className="md:hidden"
              >
                <Menu size={24} />
              </button>
              <div className="flex items-center gap-2">
                <Zap className="text-purple-600" size={32} />
                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  FlashDeal
                </h1>
              </div>
            </div>

            <div className="hidden md:flex items-center gap-2">
              <CountdownTimer endTime={saleEndTime} />
            </div>

            <div className="flex items-center gap-3">
              {user ? (
                <>
                  <button
                    onClick={() => setCartOpen(true)}
                    className="relative p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <CartIcon size={24} />
                  </button>
                  <div className="hidden md:flex items-center gap-2">
                    <span className="text-sm font-medium">Hi, {user.name}</span>
                    <button
                      onClick={logout}
                      className="text-sm text-red-600 hover:text-red-700 font-medium"
                    >
                      Logout
                    </button>
                  </div>
                </>
              ) : (
                <div className="flex gap-2">
                  <button
                    onClick={() => openAuth('login')}
                    className="flex items-center gap-1 px-4 py-2 text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                  >
                    <LogIn size={18} />
                    <span className="hidden sm:inline">Login</span>
                  </button>
                  <button
                    onClick={() => openAuth('register')}
                    className="flex items-center gap-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-colors"
                  >
                    <UserPlus size={18} />
                    <span className="hidden sm:inline">Register</span>
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="md:hidden mt-3 flex justify-center">
            <CountdownTimer endTime={saleEndTime} />
          </div>

          {menuOpen && (
            <div className="md:hidden mt-4 pb-2 border-t pt-4">
              <nav className="space-y-2">
                <button
                  onClick={() => { setCurrentPage('products'); setMenuOpen(false); }}
                  className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                    currentPage === 'products' ? 'bg-purple-100 text-purple-700' : 'hover:bg-gray-100'
                  }`}
                >
                  Products
                </button>
                <button
                  onClick={() => { setCurrentPage('leaderboard'); setMenuOpen(false); }}
                  className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                    currentPage === 'leaderboard' ? 'bg-purple-100 text-purple-700' : 'hover:bg-gray-100'
                  }`}
                >
                  Leaderboard
                </button>
                <button
                  onClick={() => { setCurrentPage('analytics'); setMenuOpen(false); }}
                  className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                    currentPage === 'analytics' ? 'bg-purple-100 text-purple-700' : 'hover:bg-gray-100'
                  }`}
                >
                  Analytics
                </button>
                {user && (
                  <button
                    onClick={() => { logout(); setMenuOpen(false); }}
                    className="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                  >
                    Logout
                  </button>
                )}
              </nav>
            </div>
          )}
        </div>
      </header>

      <nav className="hidden md:block bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex gap-1">
            <button
              onClick={() => setCurrentPage('products')}
              className={`px-6 py-3 font-medium transition-colors ${
                currentPage === 'products'
                  ? 'text-purple-600 border-b-2 border-purple-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Package className="inline mr-2" size={18} />
              Products
            </button>
            <button
              onClick={() => setCurrentPage('leaderboard')}
              className={`px-6 py-3 font-medium transition-colors ${
                currentPage === 'leaderboard'
                  ? 'text-purple-600 border-b-2 border-purple-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Trophy className="inline mr-2" size={18} />
              Leaderboard
            </button>
            <button
              onClick={() => setCurrentPage('analytics')}
              className={`px-6 py-3 font-medium transition-colors ${
                currentPage === 'analytics'
                  ? 'text-purple-600 border-b-2 border-purple-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <BarChart3 className="inline mr-2" size={18} />
              Analytics
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {currentPage === 'products' && (
          <div>
            <div className="mb-8 text-center">
              <h2 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                Flash Sale Live Now! 🔥
              </h2>
              <p className="text-gray-600">Grab amazing deals before they're gone!</p>
            </div>

            {products.length === 0 ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Loading products...</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {products.map(product => (
                  <ProductCard
                    key={product._id}
                    product={product}
                    onAddToCart={addToCart}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {currentPage === 'leaderboard' && <Leaderboard />}
        {currentPage === 'analytics' && <AnalyticsDashboard />}
      </main>

      {!chatOpen && (
        <button
          onClick={() => setChatOpen(true)}
          className="fixed bottom-4 right-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-shadow z-40"
        >
          <MessageSquare size={24} />
        </button>
      )}

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        mode={authMode}
      />
      <ShoppingCart isOpen={cartOpen} onClose={() => setCartOpen(false)} />
      <AIChatbot isOpen={chatOpen} onClose={() => setChatOpen(false)} />

      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                <Zap className="text-purple-600" />
                FlashDeal
              </h3>
              <p className="text-gray-600 text-sm">
                Your destination for the best flash sales and unbeatable deals.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Quick Links</h4>
              <div className="space-y-2 text-sm text-gray-600">
                <div>About Us</div>
                <div>Contact</div>
                <div>Terms of Service</div>
                <div>Privacy Policy</div>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-3">Customer Support</h4>
              <div className="space-y-2 text-sm text-gray-600">
                <div>FAQ</div>
                <div>Shipping Info</div>
                <div>Returns</div>
                <div>Track Order</div>
              </div>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t text-center text-sm text-gray-600">
            © 2024 FlashDeal. All rights reserved.
          </div>
        </div>
      </footer>

      <style>{`
        @keyframes slide-in {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        .animate-slide-in {
          animation: slide-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default function FlashSaleApp() {
  return (
    <AuthProvider>
      <NotificationProvider>
        <App />
      </NotificationProvider>
    </AuthProvider>
  );
}
