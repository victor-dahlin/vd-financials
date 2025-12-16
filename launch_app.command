#!/bin/bash
cd /Users/victordahlin/.gemini/antigravity/scratch/financial_analysis_system

# Activate environment
source venv/bin/activate

echo "=========================================="
echo "   Financial Analysis System Launcher"
echo "=========================================="
echo "Directory: $(pwd)"
echo "Python: $(which python)"

# Launch Streamlit
echo "Starting Streamlit..."
# We use & to run in background so we can try to force open browser if needed, 
# but actually streamlit should block. 
# Let's run it normally but catch exit.

streamlit run src/app.py

if [ $? -ne 0 ]; then
    echo "ERROR: Streamlit crashed or failed to start."
fi

echo ""
echo "Program exited."
read -p "Press [Enter] to close this window..."
