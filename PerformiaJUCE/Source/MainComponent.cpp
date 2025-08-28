#include "MainComponent.h"

//==============================================================================
MainComponent::MainComponent()
{
    // Set up look and feel
    darkLookAndFeel.setColour (juce::Slider::thumbColourId, juce::Colour (0xff00d9ff));
    darkLookAndFeel.setColour (juce::Slider::trackColourId, juce::Colour (0xff1a1a1a));
    setLookAndFeel (&darkLookAndFeel);
    
    // Add all buttons as listeners
    powerButton.addListener (this);
    testToneButton.addListener (this);
    inputMonitorButton.addListener (this);
    showAudioSettingsButton.addListener (this);
    refreshDevicesButton.addListener (this);
    
    // Set button colors
    powerButton.setColour (juce::TextButton::buttonColourId, juce::Colour (0xff1a1a1a));
    testToneButton.setColour (juce::TextButton::buttonColourId, juce::Colour (0xff1a1a1a));
    inputMonitorButton.setColour (juce::TextButton::buttonColourId, juce::Colour (0xff1a1a1a));
    showAudioSettingsButton.setColour (juce::TextButton::buttonColourId, juce::Colour (0xff2a2a2a));
    refreshDevicesButton.setColour (juce::TextButton::buttonColourId, juce::Colour (0xff2a2a2a));
    
    addAndMakeVisible (powerButton);
    addAndMakeVisible (testToneButton);
    addAndMakeVisible (inputMonitorButton);
    addAndMakeVisible (showAudioSettingsButton);
    addAndMakeVisible (refreshDevicesButton);
    
    // Device selectors
    inputDeviceLabel.setText ("INPUT DEVICE:", juce::dontSendNotification);
    inputDeviceLabel.setColour (juce::Label::textColourId, juce::Colour (0xff606060));
    addAndMakeVisible (inputDeviceLabel);
    addAndMakeVisible (inputDeviceSelector);
    
    outputDeviceLabel.setText ("OUTPUT DEVICE:", juce::dontSendNotification);
    outputDeviceLabel.setColour (juce::Label::textColourId, juce::Colour (0xff606060));
    addAndMakeVisible (outputDeviceLabel);
    addAndMakeVisible (outputDeviceSelector);
    
    // Channel selector
    inputChannelLabel.setText ("INPUT CHANNEL:", juce::dontSendNotification);
    inputChannelLabel.setColour (juce::Label::textColourId, juce::Colour (0xff606060));
    addAndMakeVisible (inputChannelLabel);
    addAndMakeVisible (inputChannelSelector);
    
    // Input gain slider
    inputGainSlider.setSliderStyle (juce::Slider::LinearHorizontal);
    inputGainSlider.setRange (0.0, 200.0, 1.0);  // Increased range for weak signals
    inputGainSlider.setValue (100.0);
    inputGainSlider.setTextBoxStyle (juce::Slider::TextBoxRight, false, 50, 20);
    addAndMakeVisible (inputGainSlider);
    
    inputGainLabel.setText ("INPUT GAIN", juce::dontSendNotification);
    inputGainLabel.setColour (juce::Label::textColourId, juce::Colour (0xff606060));
    addAndMakeVisible (inputGainLabel);
    
    // Output volume slider  
    outputVolumeSlider.setSliderStyle (juce::Slider::LinearHorizontal);
    outputVolumeSlider.setRange (0.0, 100.0, 1.0);
    outputVolumeSlider.setValue (75.0);
    outputVolumeSlider.setTextBoxStyle (juce::Slider::TextBoxRight, false, 50, 20);
    addAndMakeVisible (outputVolumeSlider);
    
    outputVolumeLabel.setText ("OUTPUT VOLUME", juce::dontSendNotification);
    outputVolumeLabel.setColour (juce::Label::textColourId, juce::Colour (0xff606060));
    addAndMakeVisible (outputVolumeLabel);
    
    // Test frequency slider
    testFreqSlider.setSliderStyle (juce::Slider::LinearHorizontal);
    testFreqSlider.setRange (100.0, 1000.0, 1.0);
    testFreqSlider.setValue (440.0);
    testFreqSlider.setTextBoxStyle (juce::Slider::TextBoxRight, false, 60, 20);
    testFreqSlider.onValueChange = [this] { testToneFrequency = testFreqSlider.getValue(); };
    addAndMakeVisible (testFreqSlider);
    
    testFreqLabel.setText ("TEST FREQ (Hz)", juce::dontSendNotification);
    testFreqLabel.setColour (juce::Label::textColourId, juce::Colour (0xff606060));
    addAndMakeVisible (testFreqLabel);
    
    // Status labels
    statusLabel.setText ("STATUS: INITIALIZING...", juce::dontSendNotification);
    statusLabel.setColour (juce::Label::textColourId, juce::Colour (0xffffd600));
    statusLabel.setFont (juce::FontOptions("Monaco", 14.0f, juce::Font::bold));
    addAndMakeVisible (statusLabel);
    
    deviceInfoLabel.setText ("", juce::dontSendNotification);
    deviceInfoLabel.setColour (juce::Label::textColourId, juce::Colour (0xff808080));
    deviceInfoLabel.setFont (juce::FontOptions("Monaco", 11.0f, juce::Font::plain));
    deviceInfoLabel.setJustificationType (juce::Justification::topLeft);
    addAndMakeVisible (deviceInfoLabel);
    
    // IMPORTANT: Request maximum channels initially
    // This ensures we can access all available inputs
    auto result = setAudioChannels (256, 2);  // Request many input channels
    
    if (result.isNotEmpty())
    {
        DBG ("Audio setup error: " << result);
        // Try with fewer channels
        result = setAudioChannels (8, 2);
        if (result.isNotEmpty())
        {
            DBG ("Fallback audio setup error: " << result);
            setAudioChannels (2, 2);  // Final fallback
        }
    }
    
    // Add device manager listener
    deviceManager.addChangeListener (this);
    
    // Update device list
    updateDeviceList();
    
    // Device selector callbacks
    inputDeviceSelector.onChange = [this] {
        auto selected = inputDeviceSelector.getText();
        if (selected.isNotEmpty())
            setAudioDevice (selected, true);
    };
    
    outputDeviceSelector.onChange = [this] {
        auto selected = outputDeviceSelector.getText();
        if (selected.isNotEmpty())
            setAudioDevice (selected, false);
    };
    
    inputChannelSelector.onChange = [this] {
        logMessage ("Input channel changed to: " + inputChannelSelector.getText());
    };
    
    // Start timer for UI updates
    startTimer (30);
    
    setSize (1400, 900);
    
    // Log initial state
    if (auto* device = deviceManager.getCurrentAudioDevice())
    {
        DBG ("Initial device: " << device->getName());
        DBG ("Input channels active: " << device->getActiveInputChannels().toString(2));
        DBG ("Output channels active: " << device->getActiveOutputChannels().toString(2));
    }
}

MainComponent::~MainComponent()
{
    deviceManager.removeChangeListener (this);
    shutdownAudio();
    setLookAndFeel (nullptr);
}

//==============================================================================
void MainComponent::prepareToPlay (int samplesPerBlockExpected, double sampleRate)
{
    currentSampleRate = sampleRate;
    currentBufferSize = samplesPerBlockExpected;
    
    DBG ("=== prepareToPlay called ===");
    DBG ("Sample rate: " << sampleRate);
    DBG ("Buffer size: " << samplesPerBlockExpected);
    
    if (auto* device = deviceManager.getCurrentAudioDevice())
    {
        DBG ("Device: " << device->getName());
        DBG ("Active input channels: " << device->getActiveInputChannels().toString(2));
        DBG ("Active output channels: " << device->getActiveOutputChannels().toString(2));
    }
}

void MainComponent::getNextAudioBlock (const juce::AudioSourceChannelInfo& bufferToFill)
{
    // Always clear the buffer first
    bufferToFill.clearActiveBufferRegion();
    
    if (!systemOn)
    {
        inputLevel = 0.0f;
        outputLevel = 0.0f;
        return;
    }
    
    // Get buffer info
    const int numInputChannels = getTotalNumInputChannels();
    const int numOutputChannels = getTotalNumOutputChannels();
    const int numSamples = bufferToFill.numSamples;
    
    // Debug logging (only occasionally to avoid spam)
    static int debugCounter = 0;
    if (++debugCounter > 100)  // Log every ~3 seconds at 30fps
    {
        debugCounter = 0;
        DBG ("=== Audio Callback Debug ===");
        DBG ("Buffer channels: " << bufferToFill.buffer->getNumChannels());
        DBG ("Num input channels: " << numInputChannels);
        DBG ("Num output channels: " << numOutputChannels);
        DBG ("Num samples: " << numSamples);
        
        // Check if we're getting any input signal at all
        for (int ch = 0; ch < numInputChannels && ch < bufferToFill.buffer->getNumChannels(); ++ch)
        {
            auto* data = bufferToFill.buffer->getReadPointer(ch, bufferToFill.startSample);
            float sum = 0.0f;
            for (int i = 0; i < numSamples; ++i)
                sum += std::abs(data[i]);
            
            if (sum > 0.0f)
                DBG ("Channel " << ch << " has signal: " << sum);
        }
    }
    
    // Get selected input channel
    int selectedInputChannel = inputChannelSelector.getSelectedId() - 1;
    if (selectedInputChannel < 0) selectedInputChannel = 0;
    
    // Try all channels if selected channel has no signal
    float maxInput = 0.0f;
    int activeChannel = -1;
    
    // First try selected channel
    if (selectedInputChannel < numInputChannels && 
        selectedInputChannel < bufferToFill.buffer->getNumChannels())
    {
        auto* inputData = bufferToFill.buffer->getReadPointer(selectedInputChannel, 
                                                              bufferToFill.startSample);
        for (int i = 0; i < numSamples; ++i)
        {
            float sample = std::abs(inputData[i]);
            if (sample > maxInput) 
            {
                maxInput = sample;
                activeChannel = selectedInputChannel;
            }
        }
    }
    
    // If no signal on selected channel, scan all channels
    if (maxInput < 0.0001f)  // Threshold for "no signal"
    {
        for (int ch = 0; ch < numInputChannels && ch < bufferToFill.buffer->getNumChannels(); ++ch)
        {
            auto* inputData = bufferToFill.buffer->getReadPointer(ch, bufferToFill.startSample);
            for (int i = 0; i < numSamples; ++i)
            {
                float sample = std::abs(inputData[i]);
                if (sample > maxInput)
                {
                    maxInput = sample;
                    activeChannel = ch;
                }
            }
        }
        
        // If we found signal on a different channel, log it
        if (activeChannel >= 0 && activeChannel != selectedInputChannel)
        {
            DBG ("Signal detected on channel " << (activeChannel + 1) << " instead of selected channel " << (selectedInputChannel + 1));
        }
    }
    
    // Apply gain
    float gain = (float)(inputGainSlider.getValue() / 50.0);
    inputLevel = maxInput * gain;
    
    // Output section
    float outputGain = (float)(outputVolumeSlider.getValue() / 100.0);
    float maxOutput = 0.0f;
    
    // Generate test tone
    if (testToneActive)
    {
        const double cyclesPerSample = testToneFrequency / currentSampleRate;
        
        for (int channel = 0; channel < numOutputChannels && channel < bufferToFill.buffer->getNumChannels(); ++channel)
        {
            auto* outputData = bufferToFill.buffer->getWritePointer(channel, bufferToFill.startSample);
            
            double phase = testTonePhase;
            for (int sample = 0; sample < numSamples; ++sample)
            {
                float currentSample = (float)std::sin(2.0 * juce::MathConstants<double>::pi * phase);
                currentSample *= outputGain * 0.3f;
                outputData[sample] = currentSample;
                
                phase += cyclesPerSample;
                if (phase >= 1.0) phase -= 1.0;
                
                float absSample = std::abs(currentSample);
                if (absSample > maxOutput) maxOutput = absSample;
            }
        }
        testTonePhase = std::fmod(testTonePhase + cyclesPerSample * numSamples, 1.0);
    }
    // Input monitoring - use the channel where we found signal
    else if (inputMonitoring && activeChannel >= 0)
    {
        auto* inputData = bufferToFill.buffer->getReadPointer(activeChannel, bufferToFill.startSample);
        
        for (int channel = 0; channel < numOutputChannels && channel < bufferToFill.buffer->getNumChannels(); ++channel)
        {
            auto* outputData = bufferToFill.buffer->getWritePointer(channel, bufferToFill.startSample);
            
            for (int i = 0; i < numSamples; ++i)
            {
                float sample = inputData[i] * gain * outputGain;
                outputData[i] = sample;
                
                float absSample = std::abs(sample);
                if (absSample > maxOutput) maxOutput = absSample;
            }
        }
    }
    
    outputLevel = maxOutput;
}

void MainComponent::releaseResources()
{
    DBG ("releaseResources called");
}

void MainComponent::changeListenerCallback (juce::ChangeBroadcaster* source)
{
    if (source == &deviceManager)
    {
        DBG ("=== Device Manager Changed ===");
        
        updateDeviceList();
        updateChannelSelector();
        
        if (auto* device = deviceManager.getCurrentAudioDevice())
        {
            currentSampleRate = device->getCurrentSampleRate();
            currentBufferSize = device->getCurrentBufferSizeSamples();
            
            DBG ("New device: " << device->getName());
            DBG ("Sample rate: " << currentSampleRate);
            DBG ("Buffer size: " << currentBufferSize);
            DBG ("Input channels: " << device->getActiveInputChannels().toString(2));
            DBG ("Output channels: " << device->getActiveOutputChannels().toString(2));
        }
    }
}

void MainComponent::buttonClicked (juce::Button* button)
{
    if (button == &powerButton)
    {
        systemOn = !systemOn;
        powerButton.setButtonText (systemOn ? "SYSTEM ON" : "SYSTEM OFF");
        powerButton.setColour (juce::TextButton::buttonColourId, 
                              systemOn ? juce::Colour (0xff00ff41) : juce::Colour (0xff1a1a1a));
        
        DBG ("System power: " << (systemOn ? "ON" : "OFF"));
        
        if (!systemOn)
        {
            testToneActive = false;
            inputMonitoring = false;
            testToneButton.setButtonText ("TEST TONE OFF");
            testToneButton.setColour (juce::TextButton::buttonColourId, juce::Colour (0xff1a1a1a));
            inputMonitorButton.setButtonText ("MONITOR OFF");
            inputMonitorButton.setColour (juce::TextButton::buttonColourId, juce::Colour (0xff1a1a1a));
        }
    }
    else if (button == &testToneButton)
    {
        testToneActive = !testToneActive;
        testToneButton.setButtonText (testToneActive ? "TEST TONE ON" : "TEST TONE OFF");
        testToneButton.setColour (juce::TextButton::buttonColourId, 
                                 testToneActive ? juce::Colour (0xffffd600) : juce::Colour (0xff1a1a1a));
        
        if (testToneActive)
        {
            inputMonitoring = false;
            inputMonitorButton.setButtonText ("MONITOR OFF");
            inputMonitorButton.setColour (juce::TextButton::buttonColourId, juce::Colour (0xff1a1a1a));
        }
    }
    else if (button == &inputMonitorButton)
    {
        inputMonitoring = !inputMonitoring;
        inputMonitorButton.setButtonText (inputMonitoring ? "MONITOR ON" : "MONITOR OFF");
        inputMonitorButton.setColour (juce::TextButton::buttonColourId, 
                                     inputMonitoring ? juce::Colour (0xff00d9ff) : juce::Colour (0xff1a1a1a));
        
        DBG ("Input monitoring: " << (inputMonitoring ? "ON" : "OFF"));
        
        if (inputMonitoring)
        {
            testToneActive = false;
            testToneButton.setButtonText ("TEST TONE OFF");
            testToneButton.setColour (juce::TextButton::buttonColourId, juce::Colour (0xff1a1a1a));
        }
    }
    else if (button == &showAudioSettingsButton)
    {
        auto* dialogWindow = new juce::DialogWindow ("Audio Settings", 
                                                     juce::Colour (0xff2a2a2a), true);
        
        audioSetupComp.reset (new juce::AudioDeviceSelectorComponent (deviceManager,
                                                                      0, 256,  // min/max input channels
                                                                      0, 256,  // min/max output channels
                                                                      false, false,  // MIDI settings
                                                                      true, false));  // show channels as stereo
        
        audioSetupComp->setSize (500, 600);
        dialogWindow->setContentOwned (audioSetupComp.release(), true);
        dialogWindow->centreWithSize (500, 600);
        dialogWindow->setVisible (true);
    }
    else if (button == &refreshDevicesButton)
    {
        DBG ("Refreshing devices...");
        updateDeviceList();
        updateChannelSelector();
        
        // Force audio restart to pick up changes
        auto numIn = getTotalNumInputChannels();
        auto numOut = getTotalNumOutputChannels();
        
        shutdownAudio();
        setAudioChannels (numIn > 0 ? numIn : 2, numOut > 0 ? numOut : 2);
        
        DBG ("Audio restarted with " << numIn << " inputs, " << numOut << " outputs");
    }
}

//==============================================================================
void MainComponent::paint (juce::Graphics& g)
{
    g.fillAll (juce::Colour (0xff0a0a0a));
    
    // Title
    g.setColour (juce::Colours::white);
    g.setFont (juce::FontOptions("Monaco", 36.0f, juce::Font::bold));
    g.drawText ("PERFORMIA", 20, 20, 300, 40, juce::Justification::left);
    
    g.setColour (juce::Colour (0xff00d9ff));
    g.drawText ("AUDIO I/O TEST", 320, 20, 400, 40, juce::Justification::left);
    
    // Draw level meters
    auto inputMeterBounds = juce::Rectangle<float> (500.0f, 300.0f, 40.0f, 250.0f);
    auto outputMeterBounds = juce::Rectangle<float> (850.0f, 300.0f, 40.0f, 250.0f);
    
    drawLevelMeter (g, inputMeterBounds, smoothedInputLevel, inputPeakHold, true);
    drawLevelMeter (g, outputMeterBounds, smoothedOutputLevel, outputPeakHold, false);
    
    // Labels for meters
    g.setColour (juce::Colour (0xff606060));
    g.setFont (juce::FontOptions("Monaco", 12.0f, juce::Font::plain));
    g.drawText ("INPUT", 480, 560, 80, 20, juce::Justification::centred);
    g.drawText ("OUTPUT", 830, 560, 80, 20, juce::Justification::centred);
    
    // Level values
    g.setColour (juce::Colour (0xff00d9ff));
    g.drawText (juce::String((int)(smoothedInputLevel * 100)) + "%", 
               480, 580, 80, 20, juce::Justification::centred);
    
    g.setColour (juce::Colour (0xff00ff41));
    g.drawText (juce::String((int)(smoothedOutputLevel * 100)) + "%", 
               830, 580, 80, 20, juce::Justification::centred);
    
    // Debug info at bottom
    g.setColour (juce::Colour (0xff404040));
    g.setFont (juce::FontOptions("Monaco", 10.0f, juce::Font::plain));
    
    juce::String debugInfo = "Channels In: " + juce::String(getTotalNumInputChannels()) + 
                            " | Out: " + juce::String(getTotalNumOutputChannels());
    g.drawText (debugInfo, 20, getHeight() - 25, 400, 20, juce::Justification::left);
}

void MainComponent::resized()
{
    // Layout controls
    powerButton.setBounds (20, 80, 120, 50);
    showAudioSettingsButton.setBounds (150, 80, 140, 50);
    refreshDevicesButton.setBounds (300, 80, 140, 50);
    
    // Device selectors
    inputDeviceLabel.setBounds (20, 150, 120, 20);
    inputDeviceSelector.setBounds (20, 170, 420, 25);
    
    outputDeviceLabel.setBounds (20, 200, 120, 20);
    outputDeviceSelector.setBounds (20, 220, 420, 25);
    
    inputChannelLabel.setBounds (20, 250, 120, 20);
    inputChannelSelector.setBounds (20, 270, 200, 25);
    
    // Controls
    testToneButton.setBounds (20, 320, 140, 40);
    inputMonitorButton.setBounds (170, 320, 140, 40);
    
    testFreqLabel.setBounds (20, 370, 100, 20);
    testFreqSlider.setBounds (20, 390, 290, 30);
    
    inputGainLabel.setBounds (20, 430, 100, 20);
    inputGainSlider.setBounds (20, 450, 420, 30);
    
    outputVolumeLabel.setBounds (20, 490, 120, 20);
    outputVolumeSlider.setBounds (20, 510, 420, 30);
    
    statusLabel.setBounds (20, 560, 400, 30);
    deviceInfoLabel.setBounds (20, 590, 420, 250);
}

void MainComponent::timerCallback()
{
    // Smooth level meters
    smoothedInputLevel = smoothedInputLevel * 0.8f + inputLevel.load() * 0.2f;
    smoothedOutputLevel = smoothedOutputLevel * 0.8f + outputLevel.load() * 0.2f;
    
    // Update peak hold
    if (smoothedInputLevel > inputPeakHold)
    {
        inputPeakHold = smoothedInputLevel;
        inputPeakHoldCounter = 0;
    }
    else if (++inputPeakHoldCounter > 60)
    {
        inputPeakHold *= 0.95f;
    }
    
    if (smoothedOutputLevel > outputPeakHold)
    {
        outputPeakHold = smoothedOutputLevel;
        outputPeakHoldCounter = 0;
    }
    else if (++outputPeakHoldCounter > 60)
    {
        outputPeakHold *= 0.95f;
    }
    
    // Update status
    if (systemOn)
    {
        statusLabel.setText ("STATUS: ONLINE", juce::dontSendNotification);
        statusLabel.setColour (juce::Label::textColourId, juce::Colour (0xff00ff41));
    }
    else
    {
        statusLabel.setText ("STATUS: OFFLINE", juce::dontSendNotification);
        statusLabel.setColour (juce::Label::textColourId, juce::Colour (0xffff006e));
    }
    
    // Update device info
    if (auto* device = deviceManager.getCurrentAudioDevice())
    {
        juce::String info;
        info << "Current Device: " << device->getName() << "\n";
        info << "Type: " << device->getTypeName() << "\n";
        info << "Sample Rate: " << currentSampleRate << " Hz\n";
        info << "Buffer Size: " << currentBufferSize << " samples\n";
        info << "Latency: " << juce::String((currentBufferSize * 1000.0) / currentSampleRate, 1) << " ms\n";
        
        auto inputChannels = device->getActiveInputChannels();
        auto outputChannels = device->getActiveOutputChannels();
        
        info << "Input Channels Active: " << inputChannels.countNumberOfSetBits();
        info << " [" << inputChannels.toString(2) << "]\n";
        info << "Output Channels Active: " << outputChannels.countNumberOfSetBits();
        info << " [" << outputChannels.toString(2) << "]\n";
        
        info << "\nTotal Channels Available:\n";
        info << "Inputs: " << getTotalNumInputChannels() << "\n";
        info << "Outputs: " << getTotalNumOutputChannels();
        
        deviceInfoLabel.setText (info, juce::dontSendNotification);
    }
    
    repaint();
}

void MainComponent::updateDeviceList()
{
    auto* audioDeviceManager = &deviceManager;
    
    inputDeviceSelector.clear();
    outputDeviceSelector.clear();
    
    // Get current setup
    auto setup = audioDeviceManager->getAudioDeviceSetup();
    
    DBG ("Current setup - Input: " << setup.inputDeviceName << ", Output: " << setup.outputDeviceName);
    
    // Get available device types
    juce::OwnedArray<juce::AudioIODeviceType> types;
    audioDeviceManager->createAudioDeviceTypes (types);
    
    int inputId = 1;
    int outputId = 1;
    
    for (auto* type : types)
    {
        DBG ("Scanning device type: " << type->getTypeName());
        type->scanForDevices();
        
        // Input devices
        auto inputDevices = type->getDeviceNames (true);
        DBG ("Found " << inputDevices.size() << " input devices");
        
        for (auto& device : inputDevices)
        {
            DBG ("  Input: " << device);
            inputDeviceSelector.addItem (device, inputId);
            if (device == setup.inputDeviceName)
                inputDeviceSelector.setSelectedId (inputId);
            inputId++;
        }
        
        // Output devices  
        auto outputDevices = type->getDeviceNames (false);
        DBG ("Found " << outputDevices.size() << " output devices");
        
        for (auto& device : outputDevices)
        {
            DBG ("  Output: " << device);
            outputDeviceSelector.addItem (device, outputId);
            if (device == setup.outputDeviceName)
                outputDeviceSelector.setSelectedId (outputId);
            outputId++;
        }
    }
    
    updateChannelSelector();
}

void MainComponent::setAudioDevice (const juce::String& deviceName, bool isInput)
{
    auto setup = deviceManager.getAudioDeviceSetup();
    
    if (isInput)
    {
        setup.inputDeviceName = deviceName;
        setup.useDefaultInputChannels = false;
        setup.inputChannels.setRange (0, 256, true);  // Enable many channels
    }
    else
    {
        setup.outputDeviceName = deviceName;
        setup.useDefaultOutputChannels = true;
    }
    
    DBG ("Setting " << (isInput ? "input" : "output") << " device to: " << deviceName);
    
    juce::String error = deviceManager.setAudioDeviceSetup (setup, true);
    
    if (error.isNotEmpty())
    {
        DBG ("Error setting device: " << error);
    }
    else
    {
        DBG ("Device set successfully");
        
        // Verify the change
        if (auto* device = deviceManager.getCurrentAudioDevice())
        {
            DBG ("Verified device: " << device->getName());
            DBG ("Input channels: " << device->getActiveInputChannels().toString(2));
        }
    }
}

void MainComponent::updateChannelSelector()
{
    inputChannelSelector.clear();
    
    int numInputs = getTotalNumInputChannels();
    DBG ("Updating channel selector with " << numInputs << " channels");
    
    for (int i = 0; i < numInputs; ++i)
    {
        inputChannelSelector.addItem ("Channel " + juce::String(i + 1), i + 1);
    }
    
    if (numInputs > 0)
        inputChannelSelector.setSelectedId (1);
}

void MainComponent::logMessage (const juce::String& message)
{
    DBG (message);
}

void MainComponent::drawLevelMeter (juce::Graphics& g, juce::Rectangle<float> bounds, 
                                   float level, float peakHold, bool isInput)
{
    // Background
    g.setColour (juce::Colour (0xff1a1a1a));
    g.fillRoundedRectangle (bounds, 5.0f);
    
    // Level bar
    auto meterHeight = bounds.getHeight() * juce::jlimit (0.0f, 1.0f, level);
    auto meterBounds = bounds.removeFromBottom (meterHeight);
    
    // Color based on level
    if (level > 0.9f)
        g.setColour (juce::Colour (0xffff0000));
    else if (level > 0.7f)
        g.setColour (juce::Colour (0xffffd600));
    else
        g.setColour (isInput ? juce::Colour (0xff00d9ff) : juce::Colour (0xff00ff41));
    
    g.fillRoundedRectangle (meterBounds, 5.0f);
    
    // Peak hold line
    if (peakHold > 0.01f)
    {
        float peakY = bounds.getBottom() - (bounds.getHeight() * peakHold);
        g.setColour (juce::Colours::white);
        g.drawLine (bounds.getX(), peakY, bounds.getRight(), peakY, 2.0f);
    }
}
        info << "Latency: " << juce::String((currentBufferSize * 1000.0) / currentSampleRate, 1) << " ms\n";
        
        auto inputChannels = device->getActiveInputChannels();
        auto outputChannels = device->getActiveOutputChannels();
        
        info << "Input Channels Active: " << inputChannels.countNumberOfSetBits();
        info << " [" << inputChannels.toString(2) << "]\n";
        info << "Output Channels Active: " << outputChannels.countNumberOfSetBits();
        info << " [" << outputChannels.toString(2) << "]\n";
        
        info << "\nBuffer Info:\n";
        info << "Available buffer sizes: ";
        auto bufferSizes = device->getAvailableBufferSizes();
        if (bufferSizes.size() > 0)
        {
            for (auto size : bufferSizes)
                info << size << " ";
        }
        else
        {
            info << "Not specified";
        }
        
        deviceInfoLabel.setText (info, juce::dontSendNotification);
    }
    
    repaint();
}

void MainComponent::updateDeviceList()
{
    auto* audioDeviceManager = &deviceManager;
    
    inputDeviceSelector.clear();
    outputDeviceSelector.clear();
    
    // Get current setup
    auto setup = audioDeviceManager->getAudioDeviceSetup();
    
    DBG ("Current setup - Input: " << setup.inputDeviceName << ", Output: " << setup.outputDeviceName);
    
    // Get available device types
    juce::OwnedArray<juce::AudioIODeviceType> types;
    audioDeviceManager->createAudioDeviceTypes (types);
    
    int inputId = 1;
    int outputId = 1;
    
    for (auto* type : types)
    {
        DBG ("Scanning device type: " << type->getTypeName());
        type->scanForDevices();
        
        // Input devices
        auto inputDevices = type->getDeviceNames (true);
        DBG ("Found " << inputDevices.size() << " input devices");
        
        for (auto& device : inputDevices)
        {
            DBG ("  Input: " << device);
            inputDeviceSelector.addItem (device, inputId);
            if (device == setup.inputDeviceName)
                inputDeviceSelector.setSelectedId (inputId);
            inputId++;
        }
        
        // Output devices  
        auto outputDevices = type->getDeviceNames (false);
        DBG ("Found " << outputDevices.size() << " output devices");
        
        for (auto& device : outputDevices)
        {
            DBG ("  Output: " << device);
            outputDeviceSelector.addItem (device, outputId);
            if (device == setup.outputDeviceName)
                outputDeviceSelector.setSelectedId (outputId);
            outputId++;
        }
    }
    
    updateChannelSelector();
}

void MainComponent::setAudioDevice (const juce::String& deviceName, bool isInput)
{
    auto setup = deviceManager.getAudioDeviceSetup();
    
    if (isInput)
    {
        setup.inputDeviceName = deviceName;
        setup.useDefaultInputChannels = false;
        // Enable ALL input channels
        setup.inputChannels.clear();
        setup.inputChannels.setRange (0, 256, true);  // Enable many channels
    }
    else
    {
        setup.outputDeviceName = deviceName;
        setup.useDefaultOutputChannels = true;
    }
    
    DBG ("Setting " << (isInput ? "input" : "output") << " device to: " << deviceName);
    
    juce::String error = deviceManager.setAudioDeviceSetup (setup, true);
    
    if (error.isNotEmpty())
    {
        DBG ("Error setting device: " << error);
        // Try again with default channels
        if (isInput)
        {
            setup.useDefaultInputChannels = true;
            setup.inputChannels.clear();
        }
        error = deviceManager.setAudioDeviceSetup (setup, true);
        
        if (error.isNotEmpty())
        {
            DBG ("Second attempt failed: " << error);
        }
    }
    else
    {
        DBG ("Device set successfully");
        
        // Verify the change
        if (auto* device = deviceManager.getCurrentAudioDevice())
        {
            DBG ("Verified device: " << device->getName());
            DBG ("Input channels: " << device->getActiveInputChannels().toString(2));
            DBG ("Output channels: " << device->getActiveOutputChannels().toString(2));
        }
    }
}

void MainComponent::updateChannelSelector()
{
    inputChannelSelector.clear();
    
    if (auto* device = deviceManager.getCurrentAudioDevice())
    {
        auto activeInputs = device->getActiveInputChannels();
        int numInputs = activeInputs.countNumberOfSetBits();
        
        DBG ("Updating channel selector with " << numInputs << " active channels");
        DBG ("Channel bits: " << activeInputs.toString(2));
        
        int id = 1;
        for (int i = 0; i < activeInputs.size(); ++i)
        {
            if (activeInputs[i])
            {
                inputChannelSelector.addItem ("Channel " + juce::String(i + 1), id++);
            }
        }
        
        if (inputChannelSelector.getNumItems() > 0)
            inputChannelSelector.setSelectedId (1);
    }
}

void MainComponent::logMessage (const juce::String& message)
{
    DBG (message);
}

void MainComponent::drawLevelMeter (juce::Graphics& g, juce::Rectangle<float> bounds, 
                                   float level, float peakHold, bool isInput)
{
    // Background
    g.setColour (juce::Colour (0xff1a1a1a));
    g.fillRoundedRectangle (bounds, 5.0f);
    
    // Level bar
    auto meterHeight = bounds.getHeight() * juce::jlimit (0.0f, 1.0f, level);
    auto meterBounds = bounds.removeFromBottom (meterHeight);
    
    // Color based on level
    if (level > 0.9f)
        g.setColour (juce::Colour (0xffff0000));
    else if (level > 0.7f)
        g.setColour (juce::Colour (0xffffd600));
    else
        g.setColour (isInput ? juce::Colour (0xff00d9ff) : juce::Colour (0xff00ff41));
    
    g.fillRoundedRectangle (meterBounds, 5.0f);
    
    // Peak hold line
    if (peakHold > 0.01f)
    {
        float peakY = bounds.getBottom() - (bounds.getHeight() * peakHold);
        g.setColour (juce::Colours::white);
        g.drawLine (bounds.getX(), peakY, bounds.getRight(), peakY, 2.0f);
    }
}
