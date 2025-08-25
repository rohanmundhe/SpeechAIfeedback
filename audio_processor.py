import speech_recognition as sr
from pydub import AudioSegment
import numpy as np
import tempfile
import os
from scipy.io import wavfile
from scipy import signal

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def load_audio(self, file_path):
        """Load audio file and return audio data and sample rate"""
        try:
            # Try different loading approaches
            audio_data, sample_rate = self._load_audio_with_fallback(file_path)
            
            # Ensure we have valid audio data
            if len(audio_data) == 0:
                raise Exception("Audio file appears to be empty or corrupted")
            
            return audio_data, sample_rate
                    
        except Exception as e:
            raise Exception(f"Failed to load audio file: {str(e)}")
    
    def _load_audio_with_fallback(self, file_path):
        """Try multiple methods to load audio file"""
        errors = []
        
        # Method 1: Try basic WAV loading with scipy (no ffmpeg needed)
        try:
            return self._load_with_scipy_wav(file_path)
        except Exception as e:
            errors.append(f"WAV loading with scipy failed: {str(e)}")
        
        # Method 2: Try converting to WAV first, then loading
        try:
            return self._load_with_conversion_fallback(file_path)
        except Exception as e:
            errors.append(f"Conversion fallback failed: {str(e)}")
        
        # Method 3: Try loading as MP3 with pydub (requires ffmpeg)
        try:
            return self._load_with_pydub(file_path, 'mp3')
        except Exception as e:
            errors.append(f"MP3 loading failed: {str(e)}")
        
        # Method 4: Try auto-detecting format with pydub
        try:
            return self._load_with_pydub_auto(file_path)
        except Exception as e:
            errors.append(f"Auto-detection failed: {str(e)}")
        
        # Method 5: Try loading as different formats
        formats = ['wav', 'flv', 'mp4', 'm4a', 'ogg']
        for fmt in formats:
            try:
                return self._load_with_pydub(file_path, fmt)
            except Exception as e:
                errors.append(f"{fmt.upper()} loading failed: {str(e)}")
        
        # If all methods failed, raise combined error
        error_msg = "All audio loading methods failed: " + "; ".join(errors)
        raise Exception(error_msg)
    
    def _load_with_pydub(self, file_path, format_hint):
        """Load audio using pydub with specific format hint"""
        if format_hint == 'mp3':
            audio = AudioSegment.from_mp3(file_path)
        elif format_hint == 'wav':
            audio = AudioSegment.from_wav(file_path)
        elif format_hint == 'flv':
            audio = AudioSegment.from_flv(file_path)
        elif format_hint == 'mp4':
            audio = AudioSegment.from_file(file_path, format='mp4')
        elif format_hint == 'm4a':
            audio = AudioSegment.from_file(file_path, format='m4a')
        elif format_hint == 'ogg':
            audio = AudioSegment.from_ogg(file_path)
        else:
            audio = AudioSegment.from_file(file_path, format=format_hint)
        
        return self._convert_pydub_to_numpy(audio)
    
    def _load_with_scipy_wav(self, file_path):
        """Load WAV file using scipy (no ffmpeg needed)"""
        try:
            sample_rate, audio_data = wavfile.read(file_path)
            
            # Convert to float32 and normalize
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
            elif audio_data.dtype == np.int32:
                audio_data = audio_data.astype(np.float32) / 2147483648.0
            elif audio_data.dtype == np.uint8:
                audio_data = (audio_data.astype(np.float32) - 128) / 128.0
            
            # Convert stereo to mono if needed
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            return audio_data, sample_rate
        except Exception as e:
            raise Exception(f"Scipy WAV loading failed: {str(e)}")
    
    def _load_with_conversion_fallback(self, file_path):
        """Try to load file by assuming it's WAV even if extension suggests otherwise"""
        try:
            # Sometimes MP3/other files are actually WAV with wrong extension
            return self._load_with_scipy_wav(file_path)
        except Exception as e:
            raise Exception(f"Conversion fallback failed: {str(e)}")
    
    def _save_numpy_as_wav(self, audio_data, sample_rate):
        """Save numpy audio data as temporary WAV file"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            # Ensure audio_data is in the right format for wavfile
            if audio_data.dtype != np.int16:
                # Convert float32 to int16
                audio_data_int16 = (audio_data * 32767).astype(np.int16)
            else:
                audio_data_int16 = audio_data
            
            wavfile.write(tmp_file.name, sample_rate, audio_data_int16)
            return tmp_file.name
    
    def _load_with_pydub_auto(self, file_path):
        """Load audio with pydub auto-detection"""
        audio = AudioSegment.from_file(file_path)
        return self._convert_pydub_to_numpy(audio)
    
    def _convert_pydub_to_numpy(self, audio):
        """Convert pydub AudioSegment to numpy array"""
        # Convert to mono if stereo
        if audio.channels > 1:
            audio = audio.set_channels(1)
        
        # Get sample rate
        sample_rate = audio.frame_rate
        
        # Convert to numpy array
        audio_data = np.array(audio.get_array_of_samples(), dtype=np.float32)
        
        # Normalize based on sample width
        if audio.sample_width == 1:
            audio_data = (audio_data - 128) / 128.0
        elif audio.sample_width == 2:
            audio_data = audio_data / 32768.0
        elif audio.sample_width == 4:
            audio_data = audio_data / 2147483648.0
        else:
            # Fallback normalization
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val
        
        return audio_data, sample_rate
    
    def transcribe_audio(self, file_path):
        """Transcribe audio file to text using speech recognition with robust error handling"""
        wav_path = None
        errors = []
        
        try:
            # Try multiple approaches to convert audio for speech recognition
            wav_path = self._convert_for_speech_recognition(file_path)
            
            # Use speech recognition
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = self.recognizer.record(source)
            
            # Try different speech recognition services
            return self._recognize_speech_with_fallback(audio_data)
                
        except sr.UnknownValueError:
            return ""  # No speech detected
        except sr.RequestError as e:
            raise Exception(f"Speech recognition service error: {str(e)}")
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
        finally:
            # Clean up temporary WAV file
            if wav_path and os.path.exists(wav_path):
                try:
                    os.unlink(wav_path)
                except:
                    pass
    
    def _convert_for_speech_recognition(self, file_path):
        """Convert audio file to WAV format suitable for speech recognition"""
        errors = []
        
        # Method 1: Try using the same loading approach as before
        try:
            audio_data, sample_rate = self._load_audio_with_fallback(file_path)
            return self._save_numpy_as_wav(audio_data, sample_rate)
        except Exception as e:
            errors.append(f"Numpy conversion failed: {str(e)}")
        
        # Method 2: Direct pydub conversion with multiple format attempts
        formats_to_try = ['mp3', 'wav', 'mp4', 'm4a', 'ogg', 'flv']
        
        for fmt in formats_to_try:
            try:
                if fmt == 'mp3':
                    audio = AudioSegment.from_mp3(file_path)
                elif fmt == 'wav':
                    audio = AudioSegment.from_wav(file_path)
                elif fmt == 'mp4':
                    audio = AudioSegment.from_file(file_path, format='mp4')
                elif fmt == 'm4a':
                    audio = AudioSegment.from_file(file_path, format='m4a')
                elif fmt == 'ogg':
                    audio = AudioSegment.from_ogg(file_path)
                elif fmt == 'flv':
                    audio = AudioSegment.from_flv(file_path)
                
                # Convert to mono and standard sample rate for better recognition
                if audio.channels > 1:
                    audio = audio.set_channels(1)
                if audio.frame_rate != 16000:
                    audio = audio.set_frame_rate(16000)
                
                # Create temporary WAV file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
                    audio.export(wav_file.name, format='wav')
                    return wav_file.name
                    
            except Exception as e:
                errors.append(f"{fmt.upper()} conversion failed: {str(e)}")
                continue
        
        # If all methods failed, raise combined error
        error_msg = "All audio conversion methods failed: " + "; ".join(errors)
        raise Exception(error_msg)
    
    def _save_numpy_as_wav(self, audio_data, sample_rate):
        """Save numpy audio data as WAV file"""
        # Convert to 16-bit integers
        audio_int = (audio_data * 32767).astype(np.int16)
        
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
            wavfile.write(wav_file.name, sample_rate, audio_int)
            return wav_file.name
    
    def _recognize_speech_with_fallback(self, audio_data):
        """Try multiple speech recognition methods"""
        errors = []
        
        # Method 1: Google Speech Recognition (free)
        try:
            transcript = self.recognizer.recognize_google(audio_data)
            if transcript.strip():
                return transcript
        except Exception as e:
            errors.append(f"Google recognition failed: {str(e)}")
        
        # Method 2: Google Speech Recognition with different language settings
        try:
            transcript = self.recognizer.recognize_google(audio_data, language='en-US')
            if transcript.strip():
                return transcript
        except Exception as e:
            errors.append(f"Google (en-US) recognition failed: {str(e)}")
        
        # If no transcript was obtained, return empty string
        return ""
    
    def extract_audio_features(self, audio_data, sample_rate):
        """Extract various audio features for analysis using scipy"""
        try:
            features = {}
            
            # Duration
            features['duration'] = len(audio_data) / sample_rate
            
            # RMS (Root Mean Square) for volume analysis
            frame_length = 2048
            hop_length = 512
            
            # Calculate RMS values in frames
            rms_values = []
            for i in range(0, len(audio_data) - frame_length, hop_length):
                frame = audio_data[i:i+frame_length]
                rms = np.sqrt(np.mean(frame**2))
                rms_values.append(rms)
            
            rms_values = np.array(rms_values)
            features['rms_values'] = rms_values
            features['avg_rms'] = np.mean(rms_values)
            features['rms_variance'] = np.var(rms_values)
            
            # Convert RMS to dB
            rms_db = 20 * np.log10(np.maximum(rms_values, 1e-10))
            features['avg_volume_db'] = np.mean(rms_db)
            features['volume_variance'] = np.var(rms_db)
            
            # Basic spectral features using scipy
            f, psd = signal.welch(audio_data, sample_rate, nperseg=1024)
            spectral_centroid = np.sum(f * psd) / np.sum(psd)
            features['spectral_centroid'] = spectral_centroid
            
            # Zero crossing rate
            zcr_values = []
            for i in range(0, len(audio_data) - frame_length, hop_length):
                frame = audio_data[i:i+frame_length]
                zcr = np.sum(np.diff(np.sign(frame)) != 0) / (2 * len(frame))
                zcr_values.append(zcr)
            
            features['zero_crossing_rate'] = np.mean(zcr_values)
            
            # Simple tempo estimation (basic)
            features['tempo'] = 120  # Default tempo as we don't have librosa beat tracking
            
            return features
            
        except Exception as e:
            raise Exception(f"Feature extraction failed: {str(e)}")
