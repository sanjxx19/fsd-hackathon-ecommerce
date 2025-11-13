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
      <div className="fixed top-6 right-6 z-50 space-y-3 max-w-sm">
        {notifications.map(notif => (
          <div
            key={notif.id}
            className={`p-4 rounded-xl shadow-2xl flex items-start gap-3 backdrop-blur-sm animate-slide-in ${
              notif.type === 'success' ? 'bg-emerald-500/95' :
              notif.type === 'error' ? 'bg-rose-500/95' :
              notif.type === 'warning' ? 'bg-amber-500/95' : 'bg-blue-500/95'
            } text-white border border-white/20`}
          >
            {notif.type === 'success' ? <CheckCircle size={20} className="flex-shrink-0 mt-0.5" /> :
             notif.type === 'error' ? <AlertCircle size={20} className="flex-shrink-0 mt-0.5" /> :
             <Bell size={20} className="flex-shrink-0 mt-0.5" />}
            <span className="text-sm font-medium leading-relaxed">{notif.message}</span>
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
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden">
        <div className="bg-gradient-to-br from-purple-600 via-purple-700 to-pink-600 p-8 text-white relative overflow-hidden">
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-0 left-0 w-40 h-40 bg-white rounded-full -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute bottom-0 right-0 w-32 h-32 bg-white rounded-full translate-x-1/2 translate-y-1/2"></div>
          </div>
          <div className="relative">
            <div className="flex justify-between items-center mb-2">
              <h2 className="text-3xl font-bold">
                {mode === 'login' ? 'Welcome Back!' : 'Join FlashDeal'}
              </h2>
              <button onClick={onClose} className="text-white/80 hover:text-white transition-colors">
                <X size={28} />
              </button>
            </div>
            <p className="text-purple-100">
              {mode === 'login' ? 'Sign in to continue shopping' : 'Create an account to get started'}
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-8 space-y-5">
          {mode === 'register' && (
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Full Name</label>
              <input
                type="text"
                placeholder="John Doe"
                required
                className="w-full px-4 py-3.5 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-purple-500 focus:ring-4 focus:ring-purple-500/10 transition-all"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
          )}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Email Address</label>
            <input
              type="email"
              placeholder="you@example.com"
              required
              className="w-full px-4 py-3.5 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-purple-500 focus:ring-4 focus:ring-purple-500/10 transition-all"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Password</label>
            <input
              type="password"
              placeholder="••••••••"
              required
              className="w-full px-4 py-3.5 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-purple-500 focus:ring-4 focus:ring-purple-500/10 transition-all"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            />
          </div>
          
          {error && (
            <div className="p-4 bg-rose-50 border-2 border-rose-200 rounded-xl text-rose-700 text-sm font-medium flex items-start gap-2">
              <AlertCircle size={18} className="flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-600 via-purple-700 to-pink-600 text-white py-4 rounded-xl font-bold text-lg shadow-lg shadow-purple-500/30 hover:shadow-xl hover:shadow-purple-500/40 hover:-translate-y-0.5 disabled:opacity-50 disabled:hover:translate-y-0 transition-all"
          >
            {loading ? 'Processing...' : mode === 'login' ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <div className="px-8 pb-8 text-center border-t pt-6">
          <button
            onClick={() => {
              setMode(mode === 'login' ? 'register' : 'login');
              setError('');
            }}
            className="text-purple-600 hover:text-purple-700 font-semibold text-sm"
          >
            {mode === 'login' ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
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
    <div className="inline-flex items-center gap-3 bg-gradient-to-r from-rose-500 via-orange-500 to-amber-500 text-white px-6 py-3 rounded-full shadow-lg font-bold">
      <Clock size={20} className="animate-pulse" />
      <div className="flex items-center gap-1.5">
        <div className="flex flex-col items-center">
          <span className="text-2xl leading-none">{hours.toString().padStart(2, '0')}</span>
          <span className="text-[10px] opacity-75 uppercase">hrs</span>
        </div>
        <span className="text-xl">:</span>
        <div className="flex flex-col items-center">
          <span className="text-2xl leading-none">{minutes.toString().padStart(2, '0')}</span>
          <span className="text-[10px] opacity-75 uppercase">min</span>
        </div>
        <span className="text-xl">:</span>
        <div className="flex flex-col items-center">
          <span className="text-2xl leading-none">{seconds.toString().padStart(2, '0')}</span>
          <span className="text-[10px] opacity-75 uppercase">sec</span>
        </div>
      </div>
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
    <div className="bg-white rounded-2xl shadow-md hover:shadow-2xl transition-all duration-300 overflow-hidden group border border-gray-100">
      <div className="relative overflow-hidden">
        <div className="w-full h-56 bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 flex items-center justify-center text-7xl transform group-hover:scale-110 transition-transform duration-500">
          {product.image}
        </div>
        
        <div className="absolute top-3 left-3">
          <div className="bg-emerald-500 text-white px-3 py-1.5 rounded-full text-sm font-bold shadow-lg">
            {product.discountPercent}% OFF
          </div>
        </div>
        
        {product.stock < 10 && product.stock > 0 && (
          <div className="absolute top-3 right-3 bg-rose-500 text-white px-3 py-1.5 rounded-full text-xs font-bold animate-pulse shadow-lg">
            Only {product.stock} left!
          </div>
        )}
        {product.stock === 0 && (
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center">
            <div className="text-white text-center">
              <AlertCircle size={48} className="mx-auto mb-2" />
              <span className="text-xl font-bold">SOLD OUT</span>
            </div>
          </div>
        )}
      </div>
      
      <div className="p-6">
        <h3 className="font-bold text-xl mb-2 text-gray-900 line-clamp-1">{product.name}</h3>
        <p className="text-gray-600 text-sm mb-4 line-clamp-2 leading-relaxed">{product.description}</p>
        
        <div className="flex items-end justify-between mb-4">
          <div>
            <div className="text-3xl font-bold text-purple-600">${product.price}</div>
            <div className="text-sm text-gray-400 line-through">${product.originalPrice}</div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-500 uppercase tracking-wide mb-1">Stock</div>
            <div className={`text-sm font-bold ${product.stock > 10 ? 'text-emerald-600' : 'text-rose-600'}`}>
              {product.stock} units
            </div>
          </div>
        </div>
        
        <button
          onClick={handleAddToCart}
          disabled={product.stock === 0 || adding}
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3.5 rounded-xl font-bold text-base hover:from-purple-700 hover:to-pink-700 hover:shadow-lg hover:-translate-y-0.5 disabled:bg-gray-300 disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed disabled:hover:translate-y-0 transition-all duration-200 flex items-center justify-center gap-2"
        >
          {adding ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              Adding...
            </>
          ) : product.stock === 0 ? (
            'Sold Out'
          ) : (
            <>
              <CartIcon size={18} />
              Add to Cart
            </>
          )}
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
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-end sm:items-center justify-end z-50 p-0 sm:p-4">
      <div className="bg-white h-full sm:h-[90vh] w-full sm:max-w-lg sm:rounded-2xl shadow-2xl flex flex-col">
        <div className="p-6 border-b bg-gradient-to-r from-purple-600 to-pink-600 text-white flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Shopping Cart</h2>
            <p className="text-sm text-purple-100 mt-1">{cartItems.length} {cartItems.length === 1 ? 'item' : 'items'}</p>
          </div>
          <button onClick={onClose} className="text-white/80 hover:text-white hover:bg-white/10 rounded-lg p-2 transition-colors">
            <X size={28} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {cartItems.length === 0 ? (
            <div className="text-center text-gray-400 mt-20">
              <CartIcon size={80} className="mx-auto mb-6 opacity-20" />
              <p className="text-xl font-semibold">Your cart is empty</p>
              <p className="text-sm mt-2">Add some products to get started!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {cartItems.map(item => (
                <div key={item.product._id} className="flex gap-4 p-4 border-2 border-gray-100 rounded-2xl hover:border-purple-200 transition-colors">
                  <div className="w-24 h-24 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl flex items-center justify-center text-4xl flex-shrink-0">
                    {item.product.image}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-lg text-gray-900 mb-1 truncate">{item.product.name}</h3>
                    <p className="text-purple-600 font-bold text-xl mb-3">${item.price.toFixed(2)}</p>
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1">
                        <button
                          onClick={() => updateQuantity(item.product._id, item.quantity - 1)}
                          className="w-8 h-8 flex items-center justify-center bg-white rounded-lg hover:bg-gray-200 transition-colors font-bold text-gray-700"
                        >
                          -
                        </button>
                        <span className="px-3 font-bold text-gray-900">{item.quantity}</span>
                        <button
                          onClick={() => updateQuantity(item.product._id, item.quantity + 1)}
                          className="w-8 h-8 flex items-center justify-center bg-white rounded-lg hover:bg-gray-200 transition-colors font-bold text-gray-700"
                        >
                          +
                        </button>
                      </div>
                      <button
                        onClick={() => removeItem(item.product._id)}
                        className="ml-auto text-rose-500 hover:text-rose-700 font-semibold text-sm"
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
          <div className="p-6 border-t bg-gray-50">
            <div className="flex justify-between items-center mb-6">
              <span className="text-lg font-semibold text-gray-700">Total Amount:</span>
              <span className="text-3xl font-bold text-purple-600">${total.toFixed(2)}</span>
            </div>
            <button
              onClick={checkout}
              disabled={loading}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 rounded-xl font-bold text-lg shadow-lg shadow-purple-500/30 hover:shadow-xl hover:shadow-purple-500/40 hover:-translate-y-0.5 disabled:opacity-50 disabled:hover:translate-y-0 transition-all flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  Processing...
                </>
              ) : (
                <>
                  <CreditCard size={20} />
                  Proceed to Checkout
                </>
              )}
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

  const getMedalColor = (rank) => {
    if (rank === 1) return 'from-yellow-400 to-amber-500';
    if (rank === 2) return 'from-gray-300 to-gray-400';
    if (rank === 3) return 'from-orange-400 to-orange-500';
    return 'from-gray-100 to-gray-200';
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-3xl font-bold flex items-center gap-3">
          <div className="p-3 bg-gradient-to-br from-yellow-400 to-amber-500 rounded-xl">
            <Trophy className="text-white" size={28} />
          </div>
          Leaderboard
        </h2>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-5 py-3 border-2 border-gray-200 rounded-xl font-semibold focus:outline-none focus:border-purple-500 focus:ring-4 focus:ring-purple-500/10 transition-all"
        >
          <option value="totalPurchases">💰 Top Buyers</option>
          <option value="checkoutTime">⚡ Fastest Checkouts</option>
        </select>
      </div>

      <div className="space-y-3">
        {leaders.slice(0, 10).map((leader, idx) => (
          <div 
            key={leader.user.id} 
            className={`flex items-center gap-5 p-5 rounded-2xl transition-all duration-200 hover:scale-[1.02] ${
              idx < 3 ? 'bg-gradient-to-r shadow-md' : 'bg-gray-50 hover:bg-gray-100'
            } ${idx === 0 ? 'from-yellow-50 to-amber-50' : idx === 1 ? 'from-gray-50 to-slate-50' : idx === 2 ? 'from-orange-50 to-red-50' : ''}`}
          >
            <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${getMedalColor(idx + 1)} flex items-center justify-center font-bold text-xl shadow-lg ${
              idx < 3 ? 'text-white' : 'text-gray-600'
            }`}>
              {idx < 3 ? <Trophy size={24} /> : idx + 1}
            </div>
            <div className="flex-1">
              <div className="font-bold text-lg text-gray-900 mb-1">{leader.user.name}</div>
              <div className="text-sm text-gray-600 flex items-center gap-4">
                {sortBy === 'totalPurchases' ? (
                  <>
                    <span className="font-semibold text-purple-600">${leader.totalPurchases.toFixed(2)} spent</span>
                    <span className="text-gray-400">•</span>
                    <span>{leader.totalOrders} orders</span>
                  </>
                ) : (
                  leader.fastestCheckout ? 
                    <span className="font-semibold text-purple-600">⚡ {leader.fastestCheckout.toFixed(2)}s fastest</span> : 
                    <span className="text-gray-400">No checkout yet</span>
                )}
              </div>
            </div>
            {idx < 3 && (
              <Zap className={`${idx === 0 ? 'text-yellow-500' : idx === 1 ? 'text-gray-400' : 'text-orange-500'}`} size={24} />
            )}
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

  if (!analytics) return (
    <div className="text-center py-20">
      <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-200 border-t-purple-600 mx-auto mb-4"></div>
      <p className="text-gray-600 font-medium">Loading analytics...</p>
    </div>
  );

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-4">
        <div className="p-4 bg-gradient-to-br from-purple-600 to-pink-600 rounded-2xl shadow-lg">
          <BarChart3 className="text-white" size={32} />
        </div>
        <div>
          <h2 className="text-4xl font-bold text-gray-900">Analytics Dashboard</h2>
          <p className="text-gray-600 mt-1">Real-time insights and statistics</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-purple-500 to-purple-700 text-white rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <TrendingUp size={28} />
            <div className="p-2 bg-white/20 rounded-lg">
              <Package size={20} />
            </div>
          </div>
          <div className="text-sm opacity-90 uppercase tracking-wide mb-2">Total Sales</div>
          <div className="text-4xl font-bold mb-1">${analytics.totalSales?.toFixed(2)}</div>
          <div className="text-sm opacity-75">{analytics.totalOrders} orders completed</div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-blue-700 text-white rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <TrendingUp size={28} />
            <div className="p-2 bg-white/20 rounded-lg">
              <CreditCard size={20} />
            </div>
          </div>
          <div className="text-sm opacity-90 uppercase tracking-wide mb-2">Avg Order Value</div>
          <div className="text-4xl font-bold mb-1">${analytics.averageOrderValue?.toFixed(2)}</div>
          <div className="text-sm opacity-75">per transaction</div>
        </div>

        <div className="bg-gradient-to-br from-emerald-500 to-emerald-700 text-white rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <TrendingUp size={28} />
            <div className="p-2 bg-white/20 rounded-lg">
              <Zap size={20} />
            </div>
          </div>
          <div className="text-sm opacity-90 uppercase tracking-wide mb-2">Avg Checkout</div>
          <div className="text-4xl font-bold mb-1">{analytics.averageCheckoutTime?.toFixed(1)}s</div>
          <div className="text-sm opacity-75">average speed</div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-700 text-white rounded-2xl p-6 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <TrendingUp size={28} />
            <div className="p-2 bg-white/20 rounded-lg">
              <Clock size={20} />
            </div>
          </div>
          <div className="text-sm opacity-90 uppercase tracking-wide mb-2">Peak Hour</div>
          <div className="text-4xl font-bold mb-1">{analytics.peakHour || 'N/A'}</div>
          <div className="text-sm opacity-75">busiest time</div>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
        <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
          <Trophy className="text-purple-600" size={28} />
          Top Products
        </h3>
        <div className="space-y-4">
          {(analytics.topProducts || []).map((product, idx) => (
            <div key={idx} className="flex items-center gap-5 p-5 bg-gradient-to-r from-gray-50 to-purple-50 rounded-2xl hover:from-purple-50 hover:to-pink-50 transition-all">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl flex items-center justify-center font-bold text-white text-xl shadow-lg">
                {idx + 1}
              </div>
              <div className="flex-1">
                <div className="font-bold text-lg text-gray-900 mb-1">{product.product.name}</div>
                <div className="text-sm text-gray-600 flex items-center gap-4">
                  <span className="font-semibold text-purple-600">{product.unitsSold} sold</span>
                  <span className="text-gray-400">•</span>
                  <span>${product.revenue.toFixed(2)} revenue</span>
                </div>
              </div>
              <ChevronRight className="text-gray-400" size={24} />
            </div>
          ))}
        </div>
      </div>

      {analytics.hourlyBreakdown && analytics.hourlyBreakdown.length > 0 && (
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
          <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Clock className="text-purple-600" size={28} />
            Hourly Sales Performance
          </h3>
          <div className="space-y-4">
            {analytics.hourlyBreakdown.map(hour => {
              const maxSales = Math.max(...analytics.hourlyBreakdown.map(h => h.sales));
              const percentage = (hour.sales / maxSales) * 100;
              return (
                <div key={hour.hour} className="flex items-center gap-4">
                  <div className="w-20 text-sm font-bold text-gray-700">{hour.hour}</div>
                  <div className="flex-1">
                    <div className="relative h-10 bg-gray-100 rounded-xl overflow-hidden">
                      <div 
                        className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-end pr-3"
                        style={{ width: `${percentage}%` }}
                      >
                        {percentage > 15 && (
                          <span className="text-white font-bold text-sm">${hour.sales.toFixed(2)}</span>
                        )}
                      </div>
                      {percentage <= 15 && (
                        <span className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-700 font-bold text-sm">
                          ${hour.sales.toFixed(2)}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="w-16 text-right text-sm font-semibold text-gray-600">
                    {hour.orders} 
                    <span className="text-xs text-gray-400 ml-1">orders</span>
                  </div>
                </div>
              );
            })}
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
    <div className="fixed bottom-6 right-6 w-96 max-w-[calc(100vw-3rem)] h-[600px] max-h-[calc(100vh-3rem)] bg-white rounded-2xl shadow-2xl flex flex-col z-50 border border-gray-200 overflow-hidden">
      <div className="bg-gradient-to-r from-purple-600 via-purple-700 to-pink-600 text-white p-5 flex items-center justify-between relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-32 h-32 bg-white rounded-full -translate-y-1/2 translate-x-1/2"></div>
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-white rounded-full translate-y-1/2 -translate-x-1/2"></div>
        </div>
        <div className="flex items-center gap-3 relative z-10">
          <div className="p-2 bg-white/20 rounded-lg">
            <MessageSquare size={24} />
          </div>
          <div>
            <span className="font-bold text-lg">AI Assistant</span>
            <div className="text-xs text-purple-100 flex items-center gap-1">
              <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
              Online
            </div>
          </div>
        </div>
        <button onClick={onClose} className="hover:bg-white/20 rounded-lg p-2 transition-colors relative z-10">
          <X size={24} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-gradient-to-b from-gray-50 to-white">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-4 rounded-2xl shadow-sm ${
              msg.role === 'user' 
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-br-none' 
                : 'bg-white text-gray-800 rounded-bl-none border border-gray-200'
            }`}>
              <p className="text-sm leading-relaxed">{msg.content}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white p-4 rounded-2xl rounded-bl-none border border-gray-200 shadow-sm">
              <div className="flex gap-1.5">
                <div className="w-2.5 h-2.5 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2.5 h-2.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2.5 h-2.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="p-5 border-t bg-white">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type your message..."
            className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-purple-500 focus:ring-4 focus:ring-purple-500/10 transition-all"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-5 py-3 rounded-xl hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:hover:translate-y-0 transition-all font-semibold"
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
      const res = await fetch(`${API_BASE_URL}/cart/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ productId: product._id, quantity: 1 })
      });
      
      const data = await res.json();
      
      if (res.ok) {
        addNotification(`${product.name} added to cart!`, 'success');
        fetchProducts();
      } else {
        addNotification(data.error || 'Failed to add to cart', 'error');
      }
    } catch (err) {
      addNotification('Network error. Please try again.', 'error');
    }
  };

  const openAuth = (mode) => {
    setAuthMode(mode);
    setAuthModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      <header className="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-40 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button 
                onClick={() => setMenuOpen(!menuOpen)}
                className="md:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Menu size={24} className="text-gray-700" />
              </button>
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl shadow-lg">
                  <Zap className="text-white" size={28} />
                </div>
                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 bg-clip-text text-transparent">
                    FlashDeal
                  </h1>
                  <p className="text-xs text-gray-500 font-medium hidden sm:block">Lightning fast deals</p>
                </div>
              </div>
            </div>

            <div className="hidden md:flex items-center">
              <CountdownTimer endTime={saleEndTime} />
            </div>

            <div className="flex items-center gap-3">
              {user ? (
                <>
                  <button
                    onClick={() => setCartOpen(true)}
                    className="relative p-3 hover:bg-gray-100 rounded-xl transition-all hover:scale-105"
                  >
                    <CartIcon size={24} className="text-gray-700" />
                    <div className="absolute -top-1 -right-1 w-5 h-5 bg-gradient-to-br from-rose-500 to-pink-600 rounded-full flex items-center justify-center text-[10px] font-bold text-white shadow-lg">
                      0
                    </div>
                  </button>
                  <div className="hidden md:flex items-center gap-3 pl-3 border-l">
                    <div className="text-right">
                      <div className="text-sm font-bold text-gray-900">{user.name}</div>
                      <div className="text-xs text-gray-500">Member</div>
                    </div>
                    <button
                      onClick={logout}
                      className="px-4 py-2 text-sm text-rose-600 hover:bg-rose-50 rounded-lg transition-colors font-semibold"
                    >
                      Logout
                    </button>
                  </div>
                </>
              ) : (
                <div className="flex gap-2">
                  <button
                    onClick={() => openAuth('login')}
                    className="flex items-center gap-2 px-4 py-2.5 text-purple-600 hover:bg-purple-50 rounded-xl transition-all font-semibold"
                  >
                    <LogIn size={18} />
                    <span className="hidden sm:inline">Login</span>
                  </button>
                  <button
                    onClick={() => openAuth('register')}
                    className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:shadow-lg hover:-translate-y-0.5 transition-all font-semibold"
                  >
                    <UserPlus size={18} />
                    <span className="hidden sm:inline">Register</span>
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="md:hidden mt-4 flex justify-center">
            <CountdownTimer endTime={saleEndTime} />
          </div>

          {menuOpen && (
            <div className="md:hidden mt-4 pb-2 border-t pt-4">
              <nav className="space-y-2">
                <button
                  onClick={() => { setCurrentPage('products'); setMenuOpen(false); }}
                  className={`w-full text-left px-4 py-3 rounded-xl transition-all font-semibold flex items-center gap-3 ${
                    currentPage === 'products' 
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg' 
                      : 'hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  <Package size={20} />
                  Products
                </button>
                <button
                  onClick={() => { setCurrentPage('leaderboard'); setMenuOpen(false); }}
                  className={`w-full text-left px-4 py-3 rounded-xl transition-all font-semibold flex items-center gap-3 ${
                    currentPage === 'leaderboard' 
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg' 
                      : 'hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  <Trophy size={20} />
                  Leaderboard
                </button>
                <button
                  onClick={() => { setCurrentPage('analytics'); setMenuOpen(false); }}
                  className={`w-full text-left px-4 py-3 rounded-xl transition-all font-semibold flex items-center gap-3 ${
                    currentPage === 'analytics' 
                      ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg' 
                      : 'hover:bg-gray-100 text-gray-700'
                  }`}
                >
                  <BarChart3 size={20} />
                  Analytics
                </button>
                {user && (
                  <>
                    <div className="border-t my-2"></div>
                    <div className="px-4 py-2">
                      <div className="text-sm font-bold text-gray-900">{user.name}</div>
                      <div className="text-xs text-gray-500">Member</div>
                    </div>
                    <button
                      onClick={() => { logout(); setMenuOpen(false); }}
                      className="w-full text-left px-4 py-3 text-rose-600 hover:bg-rose-50 rounded-xl font-semibold flex items-center gap-3"
                    >
                      <LogIn size={20} />
                      Logout
                    </button>
                  </>
                )}
              </nav>
            </div>
          )}
        </div>
      </header>

      <nav className="hidden md:block bg-white/50 backdrop-blur-sm border-b border-gray-100 sticky top-[73px] z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage('products')}
              className={`px-6 py-4 font-semibold transition-all flex items-center gap-2 ${
                currentPage === 'products'
                  ? 'text-purple-600 border-b-4 border-purple-600 bg-purple-50/50'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <Package size={20} />
              Products
            </button>
            <button
              onClick={() => setCurrentPage('leaderboard')}
              className={`px-6 py-4 font-semibold transition-all flex items-center gap-2 ${
                currentPage === 'leaderboard'
                  ? 'text-purple-600 border-b-4 border-purple-600 bg-purple-50/50'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <Trophy size={20} />
              Leaderboard
            </button>
            <button
              onClick={() => setCurrentPage('analytics')}
              className={`px-6 py-4 font-semibold transition-all flex items-center gap-2 ${
                currentPage === 'analytics'
                  ? 'text-purple-600 border-b-4 border-purple-600 bg-purple-50/50'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              <BarChart3 size={20} />
              Analytics
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {currentPage === 'products' && (
          <div>
            <div className="mb-12 text-center">
              <div className="inline-flex items-center gap-2 bg-gradient-to-r from-rose-100 to-amber-100 px-6 py-2 rounded-full mb-4">
                <Zap className="text-orange-600" size={20} />
                <span className="font-bold text-orange-700 uppercase tracking-wide text-sm">Live Now</span>
              </div>
              <h2 className="text-5xl font-bold mb-4 bg-gradient-to-r from-purple-600 via-pink-600 to-orange-600 bg-clip-text text-transparent">
                Flash Sale Event 🔥
              </h2>
              <p className="text-gray-600 text-lg max-w-2xl mx-auto">
                Grab amazing deals before they're gone! Limited stock available on selected items.
              </p>
            </div>

            {products.length === 0 ? (
              <div className="text-center py-20">
                <div className="animate-spin rounded-full h-16 w-16 border-4 border-purple-200 border-t-purple-600 mx-auto mb-6"></div>
                <p className="text-gray-600 text-lg font-medium">Loading products...</p>
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
          className="fixed bottom-6 right-6 p-5 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full shadow-2xl hover:shadow-purple-500/50 hover:scale-110 transition-all z-40 group"
        >
          <MessageSquare size={28} />
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full animate-ping"></div>
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full"></div>
        </button>
      )}

      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        mode={authMode}
      />
      <ShoppingCart isOpen={cartOpen} onClose={() => setCartOpen(false)} />
      <AIChatbot isOpen={chatOpen} onClose={() => setChatOpen(false)} />

      <footer className="bg-white border-t mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
            <div className="md:col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2.5 bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl">
                  <Zap className="text-white" size={24} />
                </div>
                <h3 className="font-bold text-2xl bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  FlashDeal
                </h3>
              </div>
              <p className="text-gray-600 leading-relaxed mb-4">
                Your destination for the best flash sales and unbeatable deals. Shop smart, save big!
              </p>
              <div className="flex gap-3">
                <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-purple-100 hover:text-purple-600 transition-colors cursor-pointer">
                  <Users size={20} />
                </div>
                <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-purple-100 hover:text-purple-600 transition-colors cursor-pointer">
                  <Bell size={20} />
                </div>
                <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center hover:bg-purple-100 hover:text-purple-600 transition-colors cursor-pointer">
                  <MessageSquare size={20} />
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-bold text-gray-900 mb-4 text-lg">Quick Links</h4>
              <div className="space-y-3 text-gray-600">
                <div className="hover:text-purple-600 cursor-pointer transition-colors">About Us</div>
                <div className="hover:text-purple-600 cursor-pointer transition-colors">Contact</div>
                <div className="hover:text-purple-600 cursor-pointer transition-colors">Careers</div>
                <div className="hover:text-purple-600 cursor-pointer transition-colors">Blog</div>
              </div>
            </div>
            
            <div>
              <h4 className="font-bold text-gray-900 mb-4 text-lg">Support</h4>
              <div className="space-y-3 text-gray-600">
                <div className="hover:text-purple-600 cursor-pointer transition-colors">Help Center</div>
                <div className="hover:text-purple-600 cursor-pointer transition-colors">Shipping Info</div>
                <div className="hover:text-purple-600 cursor-pointer transition-colors">Returns</div>
                <div className="hover:text-purple-600 cursor-pointer transition-colors">Track Order</div>
              </div>
            </div>
          </div>
          
          <div className="mt-12 pt-8 border-t text-center">
            <p className="text-gray-500 text-sm">
              © 2024 FlashDeal. All rights reserved. Made with ❤️ for amazing shoppers.
            </p>
          </div>
        </div>
      </footer>
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