import re
import numpy as np
from collections import Counter
from scipy import signal

class SpeechAnalyzer:
    def __init__(self):
        # Common filler words in English
        self.filler_words = [
            'um', 'uh', 'er', 'ah', 'like', 'you know', 'actually', 'basically',
            'literally', 'so', 'well', 'okay', 'right', 'i mean', 'sort of',
            'kind of', 'you see', 'obviously', 'clearly', 'honestly'
        ]
    
    def analyze_speech(self, audio_data, sample_rate, transcript):
        """Comprehensive speech analysis"""
        try:
            # Extract audio features
            audio_features = self._extract_audio_features(audio_data, sample_rate)
            
            # Analyze transcript
            text_analysis = self._analyze_text(transcript)
            
            # Calculate speaking pace
            duration = len(audio_data) / sample_rate
            words_per_minute = (text_analysis['word_count'] / duration) * 60 if duration > 0 else 0
            
            # Volume stability score
            rms_values = audio_features.get('rms_values', np.array([]))
            volume_stability = self._calculate_volume_stability(rms_values)
            
            # Calculate confidence score based on various factors
            confidence_score = self._calculate_confidence_score(
                words_per_minute, 
                text_analysis['filler_percentage'],
                volume_stability
            )
            
            # Combine all metrics
            metrics = {
                'duration': duration,
                'total_words': text_analysis['word_count'],
                'words_per_minute': words_per_minute,
                'confidence_score': confidence_score,
                'filler_count': text_analysis['filler_count'],
                'filler_percentage': text_analysis['filler_percentage'],
                'common_fillers': text_analysis['common_fillers'],
                'avg_word_length': text_analysis['avg_word_length'],
                'volume_stability': volume_stability,
                'avg_volume': audio_features['avg_volume_db'],
                'volume_variance': audio_features['volume_variance'],
                'spectral_centroid': audio_features['spectral_centroid'],
                'zero_crossing_rate': audio_features['zero_crossing_rate'],
                'rms_values': audio_features.get('rms_values', []),  # For visualization
                'tempo': audio_features.get('tempo', 0)
            }
            
            return metrics
            
        except Exception as e:
            raise Exception(f"Speech analysis failed: {str(e)}")
    
    def _extract_audio_features(self, audio_data, sample_rate):
        """Extract audio features for analysis using scipy"""
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
        
        rms = np.array(rms_values)
        features['rms_values'] = rms
        
        # Convert RMS to dB
        rms_db = 20 * np.log10(np.maximum(rms, 1e-10))
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
        
        # Basic tempo estimation
        features['tempo'] = 120  # Default value since we don't have advanced beat tracking
        
        return features
    
    def _analyze_text(self, transcript):
        """Analyze text content for linguistic patterns"""
        if not transcript.strip():
            return {
                'word_count': 0,
                'filler_count': 0,
                'filler_percentage': 0,
                'common_fillers': [],
                'avg_word_length': 0
            }
        
        # Clean and tokenize text
        words = re.findall(r'\b\w+\b', transcript.lower())
        word_count = len(words)
        
        # Count filler words
        filler_count = 0
        found_fillers = []
        
        # Check for single-word fillers
        for word in words:
            if word in self.filler_words:
                filler_count += 1
                found_fillers.append(word)
        
        # Check for multi-word fillers
        transcript_lower = transcript.lower()
        for filler in self.filler_words:
            if len(filler.split()) > 1:  # Multi-word fillers
                count = len(re.findall(r'\b' + re.escape(filler) + r'\b', transcript_lower))
                filler_count += count
                if count > 0:
                    found_fillers.extend([filler] * count)
        
        # Calculate filler percentage
        filler_percentage = (filler_count / word_count * 100) if word_count > 0 else 0
        
        # Most common fillers
        common_fillers = [word for word, _ in Counter(found_fillers).most_common(5)]
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        return {
            'word_count': word_count,
            'filler_count': filler_count,
            'filler_percentage': filler_percentage,
            'common_fillers': common_fillers,
            'avg_word_length': avg_word_length
        }
    
    def _calculate_confidence_score(self, wpm, filler_percentage, volume_stability):
        """Calculate confidence score based on multiple factors"""
        # Base score starts at 10
        score = 10.0
        
        # Penalize for speaking too fast or too slow
        if wpm < 120:  # Too slow
            score -= (120 - wpm) / 20
        elif wpm > 200:  # Too fast
            score -= (wpm - 200) / 30
        
        # Penalize for high filler percentage
        score -= filler_percentage / 5
        
        # Penalize for poor volume stability
        score -= (10 - volume_stability) / 2
        
        # Ensure score is between 1 and 10
        return max(1.0, min(10.0, score))
    
    def _calculate_volume_stability(self, rms_values):
        """Calculate volume stability score (1-10)"""
        if rms_values is None or len(rms_values) == 0:
            return 5.0  # Default middle score if no data
        
        try:
            # Ensure rms_values is a numpy array
            if not isinstance(rms_values, np.ndarray):
                rms_values = np.array(rms_values)
            
            # Filter out invalid values
            valid_rms = rms_values[np.isfinite(rms_values) & (rms_values > 0)]
            if len(valid_rms) == 0:
                return 5.0
            
            # Calculate coefficient of variation
            mean_rms = np.mean(valid_rms)
            std_rms = np.std(valid_rms)
            
            if mean_rms == 0:
                return 5.0
            
            cv = std_rms / mean_rms
            
            # Convert to 1-10 scale (lower CV = higher stability)
            # CV of 0 = score 10, CV of 1 = score 1
            stability_score = max(1.0, min(10.0, 10 - (cv * 10)))
            
            return stability_score
        except Exception as e:
            # Return default score if calculation fails
            return 5.0
