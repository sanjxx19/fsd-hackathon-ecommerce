#!/bin/bash

# Flash Sale Backend - Quick Start Script

echo "🚀 Flash Sale Backend - Quick Start"
echo "===================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating default .env file..."
    cat >.env <<EOF
PORT=5000
MONGODB_URI=mongodb://localhost:27017/flash_sale
JWT_SECRET=your_super_secret_jwt_key_change_this_in_production
NODE_ENV=development
GEMINI_API_KEY=your_gemini_api_key_here
EOF
    echo "✅ Created .env file"
fi

# Check if database is seeded
echo "🌱 Checking database..."
if python3 -c "from config.db import get_database; db = get_database(); exit(0 if db.products.count_documents({}) > 0 else 1)" 2>/dev/null; then
    echo "✅ Database already seeded"
else
    echo "🌱 Seeding database with sample data..."
    python3 seed_data.py
fi

echo ""
echo "🎉 Setup complete! Starting server..."
echo ""

# Start server
python3 server.py
