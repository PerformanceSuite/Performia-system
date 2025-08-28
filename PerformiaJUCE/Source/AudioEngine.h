#pragma once

#include <JuceHeader.h>

class AudioEngine
{
public:
    AudioEngine();
    ~AudioEngine();
    
    void prepare (int samplesPerBlock, double sampleRate);
    void process (juce::AudioBuffer<float>& buffer);
    void release();
    
    void setInputGain (float gain);
    void setOutputVolume (float volume);
    
    float getInputLevel() const { return inputLevel; }
    float getOutputLevel() const { return outputLevel; }
    
private:
    float inputGain = 0.5f;
    float outputVolume = 0.75f;
    float inputLevel = 0.0f;
    float outputLevel = 0.0f;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (AudioEngine)
};
