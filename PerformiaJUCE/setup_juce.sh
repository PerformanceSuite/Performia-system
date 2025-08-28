#!/bin/bash

# Download and setup JUCE for Performia project

echo "Setting up JUCE for Performia..."

# Create project directory structure
cd /Users/danielconnolly/Desktop/PerformiaJUCE

# Download JUCE
echo "Downloading JUCE..."
curl -L https://github.com/juce-framework/JUCE/archive/refs/tags/8.0.4.zip -o juce.zip

# Unzip JUCE
echo "Extracting JUCE..."
unzip -q juce.zip
mv JUCE-8.0.4 JUCE

# Clean up
rm juce.zip

echo "JUCE downloaded successfully!"
echo ""
echo "Next steps:"
echo "1. We'll create a CMake project for Performia"
echo "2. Set up the audio processor and GUI"
echo "3. Build the application"
