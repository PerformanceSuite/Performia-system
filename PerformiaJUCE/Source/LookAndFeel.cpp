#include <JuceHeader.h>

class PerformiaLookAndFeel : public juce::LookAndFeel_V4
{
public:
    PerformiaLookAndFeel()
    {
        // Dark theme colors
        setColour (juce::ResizableWindow::backgroundColourId, juce::Colour (0xff0a0a0a));
        setColour (juce::TextButton::buttonColourId, juce::Colour (0xff1a1a1a));
        setColour (juce::TextButton::textColourOffId, juce::Colour (0xff606060));
        setColour (juce::Slider::thumbColourId, juce::Colour (0xff00d9ff));
        setColour (juce::Slider::trackColourId, juce::Colour (0xff2a2a2a));
        setColour (juce::Slider::backgroundColourId, juce::Colour (0xff1a1a1a));
    }
};
