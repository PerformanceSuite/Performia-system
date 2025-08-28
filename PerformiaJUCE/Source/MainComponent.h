#pragma once

#include <JuceHeader.h>

//==============================================================================
class MainComponent : public juce::AudioAppComponent,
                      public juce::Timer,
                      public juce::ChangeListener,
                      public juce::Button::Listener
{
public:
    //==============================================================================
    MainComponent();
    ~MainComponent() override;

    //==============================================================================
    void prepareToPlay (int samplesPerBlockExpected, double sampleRate) override;
    void getNextAudioBlock (const juce::AudioSourceChannelInfo& bufferToFill) override;
    void releaseResources() override;

    //==============================================================================
    void paint (juce::Graphics& g) override;
    void resized() override;
    void timerCallback() override;
    void changeListenerCallback (juce::ChangeBroadcaster* source) override;
    void buttonClicked (juce::Button* button) override;

private:
    //==============================================================================
    // Audio Settings
    std::unique_ptr<juce::AudioDeviceSelectorComponent> audioSetupComp;
    juce::TextButton showAudioSettingsButton {"AUDIO SETTINGS"};
    juce::TextButton refreshDevicesButton {"REFRESH DEVICES"};
    
    // UI Components
    juce::TextButton powerButton {"SYSTEM OFF"};
    juce::TextButton testToneButton {"TEST TONE OFF"};
    juce::TextButton inputMonitorButton {"MONITOR OFF"};
    
    juce::Slider inputGainSlider;
    juce::Slider outputVolumeSlider;
    juce::Slider testFreqSlider;
    
    juce::Label inputGainLabel;
    juce::Label outputVolumeLabel;
    juce::Label testFreqLabel;
    juce::Label statusLabel;
    juce::Label deviceInfoLabel;
    
    // Combo boxes for direct device selection
    juce::ComboBox inputDeviceSelector;
    juce::ComboBox outputDeviceSelector;
    juce::Label inputDeviceLabel;
    juce::Label outputDeviceLabel;
    
    // Channel selectors
    juce::ComboBox inputChannelSelector;
    juce::Label inputChannelLabel;
    
    // Level meters
    std::atomic<float> inputLevel {0.0f};
    std::atomic<float> outputLevel {0.0f};
    float smoothedInputLevel = 0.0f;
    float smoothedOutputLevel = 0.0f;
    
    // Peak hold
    float inputPeakHold = 0.0f;
    float outputPeakHold = 0.0f;
    int inputPeakHoldCounter = 0;
    int outputPeakHoldCounter = 0;
    
    // System state
    bool systemOn = false;
    bool testToneActive = false;
    bool inputMonitoring = false;
    double currentSampleRate = 48000.0;
    int currentBufferSize = 512;
    
    // Test tone
    double testTonePhase = 0.0;
    double testToneFrequency = 440.0;
    
    // Look and Feel
    juce::LookAndFeel_V4 darkLookAndFeel;
    
    void updateDeviceList();
    void setAudioDevice(const juce::String& deviceName, bool isInput);
    void updateChannelSelector();
    void logMessage(const juce::String& message);
    void drawLevelMeter (juce::Graphics& g, juce::Rectangle<float> bounds, 
                        float level, float peakHold, bool isInput);
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (MainComponent)
};
