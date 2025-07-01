#!/bin/bash

# Start the Data Access Request Stories mockup
echo "🚀 Starting Data Access Request Stories mockup..."
echo "📋 This will run on http://localhost:8502"
echo ""

cd ui
python -m streamlit run stories_app.py --server.port 8502

echo "Done!" 