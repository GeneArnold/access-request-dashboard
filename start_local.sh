#!/bin/bash

# Start Local Development Environment
echo "🚀 Starting Data Access Request Dashboard..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install API dependencies
echo "📥 Installing API dependencies..."
cd api
pip install -r requirements.txt
cd ..

# Install UI dependencies  
echo "📥 Installing UI dependencies..."
cd ui
pip install -r requirements.txt
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🔥 To start the services:"
echo "   Terminal 1: cd api && python main.py"
echo "   Terminal 2: cd ui && streamlit run streamlit_app.py"
echo ""
echo "📡 API will be at: http://localhost:8080"
echo "📊 Dashboard will be at: http://localhost:8501"
echo ""
echo "📖 API docs: http://localhost:8080/docs" 