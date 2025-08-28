cmake_minimum_required(VERSION 3.15)
project(PERFORMIA VERSION 1.0.0)

# Add JUCE subdirectory
add_subdirectory(JUCE)

# Add our audio application target
juce_add_gui_app(Performia
    PRODUCT_NAME "Performia"
    COMPANY_NAME "PerformiaAudio"
    BUNDLE_ID "com.performia.audio"
    ICON_BIG ""
    NEEDS_MIDI_INPUT TRUE
    NEEDS_MIDI_OUTPUT TRUE)

# Generate the JUCE header
juce_generate_juce_header(Performia)

# Add source files
target_sources(Performia
    PRIVATE
        Source/Main.cpp
        Source/MainComponent.cpp
        Source/AudioEngine.cpp
        Source/LookAndFeel.cpp)

# Set C++ standard
target_compile_features(Performia PRIVATE cxx_std_17)

# Link required JUCE modules
target_link_libraries(Performia
    PRIVATE
        juce::juce_audio_basics
        juce::juce_audio_devices
        juce::juce_audio_formats
        juce::juce_audio_processors
        juce::juce_audio_utils
        juce::juce_core
        juce::juce_data_structures
        juce::juce_events
        juce::juce_graphics
        juce::juce_gui_basics
        juce::juce_gui_extra
        juce::juce_opengl
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags)
