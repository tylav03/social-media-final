#!/bin/bash

pip install -r requirements.txt

# Start the Python backend in the background
echo "Starting Python backend..."
python3 app.py &

# Store the backend process ID
BACKEND_PID=$!

# Change directory to frontend and start npm
echo "Starting React frontend..."
cd nba-sentiment-frontend && npm start &

# Store the frontend process ID
FRONTEND_PID=$!

# Function to handle script termination
cleanup() {
    echo "Shutting down services..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

# Set up trap to catch SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# Keep script running
wait 