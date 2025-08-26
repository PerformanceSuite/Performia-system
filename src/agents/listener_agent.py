_context.get('tempo_estimate', 120)
            
            # Create rhythm sync event
            event = {
                'type': 'rhythm_sync',
                'source': 'guitar_input',
                'tempo': tempo,
                'onset': True,
                'dynamics': analysis.get('dynamics', 0.5),
                'timestamp': analysis['timestamp']
            }
            
            await self.memory.write_event(event)
            
            # Signal agents to align their timing
            await self.memory.write_event({
                'type': 'tempo_update',
                'bpm': tempo,
                'confidence': 0.7 if len(self.input_context['onset_times']) > 4 else 0.3
            })
            
            self.logger.debug(f"Rhythm sync: {tempo:.1f} BPM")
    
    async def _ambient_layer_strategy(self, analysis: Dict):
        """
        Strategy: Create ambient textures based on input
        """
        # Use dynamics and pitch for ambient parameters
        dynamics = analysis.get('dynamics', 0)
        pitch = analysis.get('pitch')
        
        # Create ambient parameters based on input
        event = {
            'type': 'ambient_layer',
            'source': 'guitar_input',
            'intensity': dynamics,
            'center_pitch': pitch if pitch else None,
            'harmonic_content': analysis.get('chord'),
            'timestamp': analysis['timestamp']
        }
        
        await self.memory.write_event(event)
        
        # Adjust overall density based on input activity
        avg_dynamics = np.mean(self.input_context['dynamics_history']) if self.input_context['dynamics_history'] else 0
        
        await self.memory.write_event({
            'type': 'density_control',
            'target_density': avg_dynamics,
            'fade_time': 2.0  # Smooth transitions
        })
    
    def _analyze_phrase(self) -> Optional[Dict]:
        """Analyze a completed phrase for musical characteristics"""
        if not self.input_context['phrase_buffer']:
            return None
        
        phrase = self.input_context['phrase_buffer']
        
        # Extract phrase characteristics
        phrase_data = {
            'length': phrase[-1]['time'] - phrase[0]['time'],
            'note_count': sum(1 for p in phrase if p['data'].get('onset')),
            'dynamics': {
                'mean': np.mean([p['data'].get('dynamics', 0) for p in phrase]),
                'max': max(p['data'].get('dynamics', 0) for p in phrase),
                'variation': np.std([p['data'].get('dynamics', 0) for p in phrase])
            },
            'pitches': [p['data'].get('pitch') for p in phrase if p['data'].get('pitch')],
            'chords': [p['data'].get('chord') for p in phrase if p['data'].get('chord')]
        }
        
        # Determine phrase type
        if phrase_data['note_count'] == 1:
            phrase_data['type'] = 'single_note'
        elif phrase_data['note_count'] < 4:
            phrase_data['type'] = 'short_motif'
        elif phrase_data['length'] < 2:
            phrase_data['type'] = 'fast_run'
        else:
            phrase_data['type'] = 'melodic_phrase'
        
        return phrase_data
    
    def _detect_chord_quality(self, chord_name: str) -> str:
        """Detect the quality of a chord (major, minor, etc.)"""
        if not chord_name:
            return 'unknown'
        
        if 'dim' in chord_name:
            return 'diminished'
        elif 'm7b5' in chord_name:
            return 'half_diminished'
        elif 'aug' in chord_name:
            return 'augmented'
        elif 'm' in chord_name and 'maj' not in chord_name:
            return 'minor'
        elif 'maj7' in chord_name:
            return 'major7'
        elif '7' in chord_name:
            return 'dominant'
        elif 'sus' in chord_name:
            return 'suspended'
        else:
            return 'major'
    
    async def on_listening_start(self):
        """Called when pedal triggers listening start"""
        self.listening = True
        
        # Reset context for new listening session
        self.input_context = {
            'current_chord': None,
            'previous_chord': None,
            'chord_history': [],
            'tempo_estimate': 120,
            'dynamics_history': [],
            'onset_times': [],
            'phrase_buffer': [],
            'last_analysis_time': 0
        }
        
        # Notify other agents
        await self.memory.write_event({
            'type': 'listening_started',
            'source': self.agent_id,
            'mode': self.listening_mode.value,
            'timestamp': asyncio.get_event_loop().time()
        })
        
        self.logger.info(f"Started listening in {self.listening_mode.value} mode")
    
    async def on_listening_stop(self):
        """Called when pedal triggers listening stop"""
        self.listening = False
        
        # Final phrase analysis if buffer not empty
        if self.input_context['phrase_buffer']:
            phrase_data = self._analyze_phrase()
            if phrase_data:
                await self.memory.write_event({
                    'type': 'final_phrase',
                    'source': 'guitar_input',
                    'phrase': phrase_data,
                    'timestamp': asyncio.get_event_loop().time()
                })
        
        # Notify other agents
        await self.memory.write_event({
            'type': 'listening_stopped',
            'source': self.agent_id,
            'timestamp': asyncio.get_event_loop().time()
        })
        
        self.logger.info("Stopped listening")
    
    async def on_mode_change(self, new_mode: ListeningMode):
        """Called when listening mode changes"""
        self.listening_mode = new_mode
        
        # Notify other agents of mode change
        await self.memory.write_event({
            'type': 'mode_changed',
            'source': self.agent_id,
            'mode': new_mode.value,
            'timestamp': asyncio.get_event_loop().time()
        })
        
        self.logger.info(f"Changed mode to: {new_mode.value}")
    
    async def on_expression_pedal(self, value: float):
        """
        Handle expression pedal input (0-1 range)
        Can be used for dynamic control, filtering, etc.
        """
        # Use expression pedal to control response sensitivity
        self.response_threshold = 0.05 + (0.2 * (1 - value))  # Inverse: heel down = more sensitive
        
        # Also affect agent personality parameters
        await self.memory.write_event({
            'type': 'expression_control',
            'source': self.agent_id,
            'value': value,
            'timestamp': asyncio.get_event_loop().time()
        })
    
    async def on_tap_tempo(self, bpm: float):
        """Handle tap tempo input"""
        self.input_context['tempo_estimate'] = bpm
        
        # Update global tempo
        await self.memory.write_event({
            'type': 'tempo_tap',
            'source': self.agent_id,
            'bpm': bpm,
            'confidence': 1.0,  # Manual tap is high confidence
            'timestamp': asyncio.get_event_loop().time()
        })
        
        self.logger.info(f"Tap tempo: {bpm:.1f} BPM")
    
    def get_status(self) -> Dict:
        """Get current listener status"""
        return {
            'listening': self.listening,
            'mode': self.listening_mode.value,
            'current_chord': self.input_context.get('current_chord'),
            'tempo': self.input_context.get('tempo_estimate', 120),
            'phrase_buffer_size': len(self.input_context.get('phrase_buffer', [])),
            'response_threshold': self.response_threshold
        }
