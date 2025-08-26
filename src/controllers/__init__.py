"""Controllers module for input devices"""

from .midi_controller import MidiPedalController
from .audio_input import AudioInputController

__all__ = ['MidiPedalController', 'AudioInputController']
