# SuperTuxKart Mobile - Android APK Builder
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    wget \
    unzip \
    openjdk-11-jdk \
    autoconf \
    automake \
    libtool \
    pkg-config \
    cmake \
    build-essential \
    ccache \
    libffi-dev \
    libssl-dev \
    libpng-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Install Python dependencies
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install buildozer cython kivy

# Download Android SDK
RUN mkdir -p /opt/android-sdk
WORKDIR /opt/android-sdk
RUN wget https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip
RUN unzip commandlinetools-linux-8512546_latest.zip
RUN mkdir -p cmdline-tools/latest
RUN mv cmdline-tools/* cmdline-tools/latest/ || true
RUN rm commandlinetools-linux-8512546_latest.zip

# Set Android environment
ENV ANDROID_HOME=/opt/android-sdk
ENV ANDROID_SDK_ROOT=/opt/android-sdk
ENV PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

# Accept Android licenses
RUN yes | sdkmanager --licenses || true
RUN sdkmanager "platform-tools" "platforms;android-30" "build-tools;30.0.3"

# Download Android NDK
RUN wget https://dl.google.com/android/repository/android-ndk-r25b-linux.zip
RUN unzip android-ndk-r25b-linux.zip
ENV ANDROID_NDK_HOME=/opt/android-sdk/android-ndk-r25b
ENV PATH="$ANDROID_NDK_HOME:$PATH"

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Ensure main.py exists
RUN cp supertuxkart_mobile.py main.py 2>/dev/null || echo "main.py already exists"

# Build APK
CMD ["buildozer", "android", "debug"]