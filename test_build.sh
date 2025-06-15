#!/usr/bin/env bash
# Test script to verify build.sh works correctly

echo "🧪 Testing build script execution..."

# Set environment variables for testing
export DEBUG=False
export SECRET_KEY=test-secret-key-for-build-testing
export DATABASE_URL=postgresql://neondb_owner:npg_nHl0UNigTdm4@ep-frosty-brook-a8iocmrc-pooler.eastus2.azure.neon.tech/neondb?sslmode=require
export ALLOWED_HOSTS=127.0.0.1,localhost
export DJANGO_SETTINGS_MODULE=entrepreneurship_lms.settings

echo "🔧 Environment variables set for testing"

# Run the build script with timeout to prevent hanging
echo "⏱️ Running build script with 5-minute timeout..."
timeout 300 ./build.sh

# Check exit code
BUILD_EXIT_CODE=$?

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo "✅ Build script completed successfully!"
    echo "🔍 Checking for any remaining processes..."
    
    # Check for any Python processes that might be hanging
    PYTHON_PROCS=$(pgrep -f python || true)
    if [ -n "$PYTHON_PROCS" ]; then
        echo "⚠️ Found remaining Python processes: $PYTHON_PROCS"
        ps aux | grep python | grep -v grep
    else
        echo "✅ No hanging Python processes found"
    fi
    
    echo "🎉 Build test completed successfully!"
    exit 0
elif [ $BUILD_EXIT_CODE -eq 124 ]; then
    echo "❌ Build script timed out after 5 minutes!"
    echo "🔍 Checking for hanging processes..."
    ps aux | grep -E "(python|gunicorn)" | grep -v grep
    exit 1
else
    echo "❌ Build script failed with exit code: $BUILD_EXIT_CODE"
    exit 1
fi
