#!/bin/bash
"""
Docker-based Android APK Build Script
Uses official buildozer Docker image to build SuperTuxKart Mobile APK
"""

echo "🐳 Starting Docker-based APK build..."
echo "========================================"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    echo "📥 Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Prepare build files
echo "📁 Preparing build files..."
cp supertuxkart_mobile.py main.py

# Create dockerfile for buildozer environment
cat > Dockerfile.buildozer << 'EOF'
FROM kivy/buildozer:latest

# Install additional dependencies
RUN apt-get update && apt-get install -y \
    autoconf \
    automake \
    libtool \
    pkg-config \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Build APK
CMD ["buildozer", "android", "debug"]
EOF

echo "🐳 Building Docker image..."
docker build -f Dockerfile.buildozer -t supertuxkart-builder .

echo "🔨 Building APK in Docker container..."
docker run --rm -v "$(pwd)":/app -w /app supertuxkart-builder

echo "✅ Docker build complete!"
echo "📱 APK should be available in bin/ directory"
ls -la bin/*.apk 2>/dev/null || echo "❌ No APK found - check build logs above"