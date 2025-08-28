// Fix around line 96 - setAudioChannels returns String not auto
    juce::String result = setAudioChannels (256, 2);  // Request many input channels
    
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