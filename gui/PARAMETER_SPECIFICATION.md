# Performia System - Complete Parameter Specification

## 1. System-Level Parameters

### Audio Configuration
- **Audio Driver** (dropdown)
  - Available system audio interfaces
  - Default: System default
  
- **Sample Rate** (dropdown)
  - 44100 Hz
  - 48000 Hz
  - 96000 Hz
  - 192000 Hz
  
- **Buffer Size** (dropdown/slider)
  - 64 samples (1.3ms @ 48kHz)
  - 128 samples (2.7ms @ 48kHz)
  - 256 samples (5.3ms @ 48kHz)
  - 512 samples (10.7ms @ 48kHz)
  - 1024 samples (21.3ms @ 48kHz)

### System Control
- **Power** (toggle)
  - Start/Stop entire system
  
- **Mode** (radio/toggle)
  - Autonomous (agents play independently)
  - Interactive (respond to audio input)
  - Hybrid (both autonomous and reactive)
  
- **Master Volume** (slider)
  - 0-100% (-inf to 0 dB)
  
- **Master Limiter** (toggle)
  - On/Off
  - Threshold (-6 dB default)
  
- **Panic/Reset** (button)
  - Stop all sounds immediately

## 2. Per-Agent Parameters (x5 agents: Drums, Bass, Melody, Harmony, Listener)

### Audio Controls
- **Volume** (slider)
  - 0-100% (-inf to 0 dB)
  - Logarithmic scale
  
- **Pan** (knob/slider)
  - -100 to +100 (L to R)
  - Center detent
  
- **Mute** (toggle button)
  - On/Off
  
- **Solo** (toggle button)
  - On/Off (exclusive or additive?)
  
- **Send Levels** (multiple sliders)
  - To Reverb (0-100%)
  - To Delay (0-100%)
  - To Other Effects (0-100%)

### Personality Parameters
- **Aggression** (slider 0-1)
  - Controls: dynamics, attack times, note density, dissonance level
  - Low: soft, gentle, sparse
  - High: loud, sharp, dense, dissonant
  
- **Creativity** (slider 0-1)
  - Controls: pattern variation, harmonic exploration, rhythmic complexity
  - Low: predictable, simple patterns
  - High: experimental, complex variations
  
- **Responsiveness** (slider 0-1)
  - Controls: reaction time to other agents, interaction likelihood
  - Low: independent, slow to respond
  - High: highly interactive, immediate responses
  
- **Stability** (slider 0-1)
  - Controls: tendency to maintain vs change patterns
  - Low: constantly changing
  - High: maintains patterns longer
  
- **Leader Tendency** (slider 0-1)
  - Controls: likelihood to initiate vs follow
  - Low: follower
  - High: leader

### Avatar Visual Parameters
- **Avatar Enable** (toggle)
  - Show/Hide avatar
  
- **Avatar Style** (dropdown)
  - Geometric (abstract shapes)
  - Humanoid (stylized character)
  - Waveform (audio visualization)
  - Particle System
  - Custom (user-uploaded)
  
- **Avatar Size** (slider)
  - Scale: 50% to 200%
  
- **Avatar Position** (XY pad)
  - X position on stage
  - Y position on stage
  
- **Avatar Color Scheme** (color pickers)
  - Primary color
  - Secondary color
  - Glow/Accent color
  - Auto-sync to audio (toggle)
  
- **Animation Intensity** (slider)
  - Subtle to Extreme (0-100%)
  - Reacts to audio amplitude
  
- **Animation Style** (dropdown)
  - Pulse (with beat)
  - Flow (smooth morphing)
  - Glitch (digital artifacts)
  - Bounce (physics-based)
  - Kaleidoscope (symmetrical)
  
- **Visual Effects** (toggles)
  - Trails (motion blur)
  - Glow (bloom effect)
  - Distortion (audio-reactive)
  - Particles (emanating)
  - Shadows (depth)
  
- **Emotion State** (dropdown/AI-controlled)
  - Neutral
  - Energetic
  - Contemplative
  - Aggressive
  - Playful
  - Melancholic
  - (Auto-detect from music)

### Musical Parameters
- **Octave Range** (dual slider)
  - Min octave: C0-C8
  - Max octave: C0-C8
  
- **Note Density** (slider)
  - 0-100% (silence to constant notes)
  
- **Rhythm Complexity** (slider)
  - 0-100% (straight to syncopated)
  
- **Harmonic Complexity** (slider)
  - 0-100% (simple to extended/altered)
  
- **Dynamic Range** (dual slider)
  - Min velocity: 0-127
  - Max velocity: 0-127

### Agent-Specific Parameters

#### Drums Only
- **Kit Selection** (dropdown)
  - Acoustic, Electronic, Hybrid, Percussion
- **Pattern Style** (dropdown)
  - Rock, Jazz, Electronic, Latin, African, etc.
- **Fill Frequency** (slider)
  - Never to Constant
- **Ghost Note Density** (slider)
  - None to Heavy

#### Bass Only
- **Playing Style** (dropdown)
  - Walking, Groove, Melodic, Drone
- **Note Duration** (slider)
  - Staccato to Legato
- **Octave Jump Frequency** (slider)
  - Never to Frequent

#### Melody Only
- **Scale/Mode** (dropdown)
  - Major, Minor, Dorian, Phrygian, etc.
- **Phrase Length** (slider)
  - 1-16 bars
- **Ornamentation** (slider)
  - None to Heavy

#### Harmony Only
- **Chord Complexity** (slider)
  - Triads to Extended/Altered
- **Voice Leading** (dropdown)
  - Smooth, Angular, Parallel
- **Inversion Preference** (slider)
  - Root position to Inversions

## 3. Interactive Mode Parameters (when audio input active)

### Input Configuration
- **Input Source** (dropdown)
  - Audio interface channels
  
- **Input Gain** (slider)
  - 0-100% with LED meter
  
- **Noise Gate** (toggle + threshold)
  - On/Off
  - Threshold slider
  
- **Input Monitor** (toggle)
  - Direct monitoring on/off

### Listening Modes
- **Mode Selection** (radio/dropdown)
  - Chord Follow
  - Call & Response
  - Rhythmic Sync
  - Ambient Layer
  - Counterpoint
  - Harmonizer
  
### Response Parameters
- **Response Time** (slider)
  - Immediate to Delayed (0-5000ms)
  
- **Response Intensity** (slider)
  - Subtle to Dramatic (0-100%)
  
- **Harmonic Matching** (slider)
  - Ignore to Strict (0-100%)
  
- **Rhythmic Matching** (slider)
  - Ignore to Lockstep (0-100%)

### Chord Detection
- **Detection Sensitivity** (slider)
  - Low to High
  
- **Chord Display** (visual)
  - Current detected chord
  - Confidence level
  - History (last 8 chords)

## 4. Global Musical Parameters

### Tempo
- **BPM** (slider/number input)
  - 20-300 BPM
  - Tap tempo button
  - Sync to external clock option
  
### Key & Scale
- **Root Note** (dropdown)
  - C through B (all 12 notes)
  
- **Scale/Mode** (dropdown)
  - Major, Minor, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian
  - Harmonic Minor, Melodic Minor
  - Blues, Pentatonic, Whole Tone, Chromatic
  
### Time Signature
- **Numerator** (dropdown)
  - 1-16
  
- **Denominator** (dropdown)
  - 2, 4, 8, 16
  
### Dynamics
- **Global Dynamics** (slider)
  - ppp to fff (-60dB to 0dB)
  
- **Dynamic Curve** (dropdown)
  - Linear, Logarithmic, Exponential
  
## 5. Effects Parameters (Global or Per-Agent)

### Reverb
- **Dry/Wet** (slider)
- **Room Size** (slider)
- **Damping** (slider)
- **Pre-delay** (slider)

### Delay
- **Dry/Wet** (slider)
- **Time** (slider/sync to tempo)
- **Feedback** (slider)
- **Filter** (high/low pass)

### Compression
- **Threshold** (slider)
- **Ratio** (slider)
- **Attack** (slider)
- **Release** (slider)
- **Makeup Gain** (slider)

### EQ (3-band minimum)
- **Low** (gain + freq)
- **Mid** (gain + freq + Q)
- **High** (gain + freq)

## 6. Visualization & Monitoring

### Meters
- **Level Meters** (per agent + master)
  - Peak hold
  - RMS vs Peak option
  
- **CPU Meter** (visual)
  - Overall usage
  - Per-core display
  
- **Latency Display** (numeric + graph)
  - Current latency
  - Historical graph
  
- **Memory Usage** (visual)
  - RAM usage
  - Buffer status

### Visual Feedback
- **Agent Activity** (animated visualization)
  - Note triggers
  - Pattern visualization
  - Inter-agent communication lines
  
- **Spectrum Analyzer** (optional)
  - FFT display
  - Per-agent or master
  
- **Waveform Display** (optional)
  - Real-time waveform
  
## 7. Preset Management

### Preset Controls
- **Load Preset** (dropdown + button)
- **Save Preset** (button + name input)
- **Delete Preset** (button with confirmation)
- **Export/Import** (file management)

### Preset Categories
- Factory Presets (read-only)
- User Presets
- Quick Slots (1-8 for fast switching)

### Morphing
- **A/B Comparison** (toggle)
- **Morph** (slider between A and B)
- **Randomize** (button with amount control)

## 8. MIDI Control

### MIDI Input
- **MIDI Device** (dropdown)
- **Channel** (1-16 or Omni)
- **Control Mapping** (learn mode)

### Foot Pedals
- **Pedal 1-4 Assignment** (dropdown per pedal)
  - Start/Stop
  - Mode Switch
  - Preset Change
  - Tap Tempo
  - Mute/Solo
  - Parameter Control

## 9. Recording & Export

### Recording
- **Record** (button)
- **Recording Format** (dropdown)
  - WAV, AIFF, FLAC
  - Bit depth: 16/24/32
  - Sample rate: match system
  
- **Recording Mode** (radio)
  - Master output only
  - Multitrack (stems)
  - With/without input
  
### MIDI Export
- **Export MIDI** (button)
- **Per-agent or combined** (option)

## 10. Live Performance Visual System

### Visual Director AI (Separate Agent)
- **Director Enable** (toggle)
  - Activate AI visual director
  
- **Director Mode** (dropdown)
  - Automatic (fully autonomous)
  - Assisted (follows cues)
  - Manual (full control)
  - Hybrid (AI suggestions)
  
- **Scene Transition Style** (dropdown)
  - Cut (instant)
  - Fade (smooth)
  - Glitch (digital)
  - Morph (fluid)
  - Wipe (directional)
  
- **Transition Speed** (slider)
  - 0.1s to 5s
  
- **Camera Controls** (virtual cameras)
  - Wide shot (all avatars)
  - Close-up (single avatar)
  - Split screen (2-4 views)
  - Dynamic (AI-controlled movement)
  - First-person (from avatar POV)
  
- **Background/Environment** (dropdown)
  - Void (black)
  - Gradient (color transitions)
  - Particles (star field, etc.)
  - Geometric (patterns)
  - Video feed (external input)
  - Generative (AI-created)
  
- **Visual Effects Layer** (global)
  - Strobe (beat-synced)
  - Color grading (LUT selection)
  - Film grain
  - Glitch effects
  - Kaleidoscope
  - Echo/trails
  
- **Text Overlays** (optional)
  - Song title
  - Agent names
  - Performance credits
  - Custom messages
  - Lyrics (if available)
  
### Performance Stage View
- **Stage Layout** (dropdown)
  - Linear (side by side)
  - Circle (agents in circle)
  - Stacked (vertical layers)
  - Free (manual positioning)
  - Dynamic (movement patterns)
  
- **Lighting System** (virtual)
  - Spotlights per avatar
  - Ambient lighting
  - Color washes
  - Strobe effects
  - Moving lights (automated)
  
- **Crowd/Audience Visualization** (toggle)
  - Show virtual audience
  - Audience energy level
  - Crowd particles
  
### Output Configuration
- **Resolution** (dropdown)
  - 1920x1080 (Full HD)
  - 3840x2160 (4K)
  - Custom resolution
  
- **Output Target** (multiple)
  - Preview window
  - External display
  - NDI stream
  - RTMP stream
  - Syphon/Spout (for VJ software)
  
- **Frame Rate** (dropdown)
  - 30 fps
  - 60 fps
  - 120 fps (if supported)
  
### Visual Cue System
- **Cue List** (programmable)
  - Pre-programmed visual changes
  - Triggered by time, bar count, or events
  - Manual trigger buttons
  
- **Beat Reactivity** (slider)
  - How much visuals react to beat
  - 0% (no reaction) to 100% (maximum)
  
- **Frequency Reactivity** (per band)
  - Low frequencies (bass response)
  - Mid frequencies
  - High frequencies (treble response)

## 11. Advanced/Developer Parameters

### Debug
- **Debug Mode** (toggle)
- **Log Level** (dropdown)
- **Show Internal State** (toggle)

### Performance Tuning
- **Thread Priority** (slider)
- **Core Affinity** (checkboxes)
- **Memory Lock** (toggle)

### Network
- **OSC Port** (number)
- **WebSocket Port** (number)
- **Remote Control** (toggle)

---

## Priority Levels for Implementation

### Phase 1 (MVP - Must Have)
- System Power On/Off
- Mode Selection (Autonomous/Interactive)
- Per-Agent: Volume, Mute, Solo
- Per-Agent: Core Personality (Aggression, Creativity)
- Global: Tempo, Key
- Basic Meters (Level, CPU)
- **Basic Avatar Display (Static)** ← Added

### Phase 2 (Core Features)
- All Personality Parameters
- Input Configuration
- Listening Modes
- Preset System
- Pan Controls
- Recording
- **Avatar Animation Controls** ← Added
- **Avatar Style Selection** ← Added

### Phase 3 (Enhanced)
- Effects (Reverb, Delay)
- Advanced Musical Parameters
- MIDI Control
- Morphing
- Visualization
- **Avatar Visual Effects** ← Added
- **Basic Visual Director** ← Added
- **Performance Stage View** ← Added

### Phase 4 (Professional)
- Full EQ
- Compression
- Multitrack Recording
- Network Control
- Advanced Debug Tools
- **AI Visual Director** ← Added
- **Live Streaming Output** ← Added
- **Visual Cue System** ← Added