#include "AudioEngine.h"

AudioEngine::AudioEngine()
{
}

AudioEngine::~AudioEngine()
{
}

void AudioEngine::prepare (int samplesPerBlock, double sampleRate)
{
    // Prepare any DSP here
}

void AudioEngine::process (juce::AudioBuffer<float>& buffer)
{
    // Process audio
    auto numChannels = buffer.getNumChannels();
    auto numSamples = buffer.getNumSamples();
    
    // Apply gain
    for (int channel = 0; channel < numChannels; ++channel)
    {
        auto* channelData = buffer.getWritePointer (channel);
        
        for (int sample = 0; sample < numSamples; ++sample)
        {
            channelData[sample] *= outputVolume;
        }
    }
}

void AudioEngine::release()
{
    // Clean up
}

void AudioEngine::setInputGain (float gain)
{
    inputGain = gain;
}

void AudioEngine::setOutputVolume (float volume)
{
    outputVolume = volume;
}
