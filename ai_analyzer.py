import json
import os
from openai import OpenAI

class AIAnalyzer:
    def __init__(self):
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
    
    def analyze_speech_performance(self, transcript, speech_metrics):
        """Analyze speech performance using AI and provide insights"""
        if not self.client:
            return self._fallback_analysis(speech_metrics)
        
        try:
            # Prepare analysis prompt
            prompt = self._create_analysis_prompt(transcript, speech_metrics)
            
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional speech coach and linguist with expertise in "
                                 "communication analysis. Provide detailed, constructive feedback on speech "
                                 "performance based on the provided transcript and metrics. Respond with "
                                 "structured JSON output."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            if content is None:
                return self._fallback_analysis(speech_metrics)
            result = json.loads(content)
            return self._validate_and_format_response(result)
            
        except Exception as e:
            print(f"AI analysis failed: {str(e)}")
            return self._fallback_analysis(speech_metrics)
    
    def _create_analysis_prompt(self, transcript, metrics):
        """Create detailed analysis prompt"""
        return f"""
        Please analyze the following speech performance data and provide comprehensive feedback:

        TRANSCRIPT:
        "{transcript}"

        SPEECH METRICS:
        - Speaking pace: {metrics['words_per_minute']:.1f} words per minute
        - Total words: {metrics['total_words']}
        - Duration: {metrics['duration']:.2f} seconds
        - Filler words: {metrics['filler_count']} ({metrics['filler_percentage']:.1f}%)
        - Common fillers: {', '.join(metrics['common_fillers'][:3])}
        - Average word length: {metrics['avg_word_length']:.1f} characters
        - Volume stability: {metrics['volume_stability']:.1f}/10
        - Average volume: {metrics['avg_volume']:.2f} dB

        Please provide analysis in the following JSON format:
        {{
            "overall_assessment": "Brief overall assessment of the speech performance",
            "language_proficiency": {{
                "grammar_score": [1-10 score],
                "vocabulary_score": [1-10 score],
                "fluency_score": [1-10 score],
                "level": "[Beginner/Intermediate/Advanced/Native]",
                "explanation": "Brief explanation of proficiency assessment"
            }},
            "strengths": ["strength1", "strength2", "strength3"],
            "areas_for_improvement": ["area1", "area2", "area3"],
            "recommendations": [
                {{
                    "title": "Recommendation title",
                    "description": "Detailed recommendation with actionable steps"
                }},
                {{
                    "title": "Another recommendation",
                    "description": "Another detailed recommendation"
                }}
            ]
        }}

        Focus on:
        1. Language proficiency (grammar, vocabulary, fluency)
        2. Communication effectiveness
        3. Speaking pace and rhythm
        4. Use of filler words
        5. Overall clarity and confidence
        6. Specific, actionable improvement suggestions
        """
    
    def _validate_and_format_response(self, result):
        """Validate and format AI response"""
        # Ensure all required fields exist
        formatted_result = {
            "overall_assessment": result.get("overall_assessment", "Speech analysis completed."),
            "language_proficiency": {
                "grammar_score": min(10, max(1, result.get("language_proficiency", {}).get("grammar_score", 7))),
                "vocabulary_score": min(10, max(1, result.get("language_proficiency", {}).get("vocabulary_score", 7))),
                "fluency_score": min(10, max(1, result.get("language_proficiency", {}).get("fluency_score", 7))),
                "level": result.get("language_proficiency", {}).get("level", "Intermediate"),
                "explanation": result.get("language_proficiency", {}).get("explanation", "Assessment based on speech analysis.")
            },
            "strengths": result.get("strengths", []),
            "areas_for_improvement": result.get("areas_for_improvement", []),
            "recommendations": result.get("recommendations", [])
        }
        
        return formatted_result
    
    def _fallback_analysis(self, speech_metrics):
        """Provide fallback analysis when AI is not available"""
        wpm = speech_metrics['words_per_minute']
        filler_percentage = speech_metrics['filler_percentage']
        volume_stability = speech_metrics['volume_stability']
        
        # Generate basic assessment based on metrics
        strengths = []
        improvements = []
        recommendations = []
        
        # Analyze speaking pace
        if 140 <= wpm <= 180:
            strengths.append("Excellent speaking pace - clear and easy to follow")
        elif wpm < 120:
            improvements.append("Speaking pace is quite slow - consider increasing tempo")
            recommendations.append({
                "title": "Increase Speaking Pace",
                "description": "Practice speaking at 140-160 words per minute for optimal clarity and engagement."
            })
        elif wpm > 200:
            improvements.append("Speaking pace is very fast - consider slowing down")
            recommendations.append({
                "title": "Moderate Speaking Pace",
                "description": "Slow down to 140-180 words per minute to ensure your audience can follow along easily."
            })
        
        # Analyze filler words
        if filler_percentage < 2:
            strengths.append("Excellent control of filler words")
        elif filler_percentage > 5:
            improvements.append("High usage of filler words detected")
            recommendations.append({
                "title": "Reduce Filler Words",
                "description": "Practice pausing instead of using filler words. Record yourself and identify patterns."
            })
        
        # Analyze volume stability
        if volume_stability >= 7:
            strengths.append("Good volume control and consistency")
        else:
            improvements.append("Volume inconsistency detected")
            recommendations.append({
                "title": "Improve Volume Consistency",
                "description": "Practice maintaining steady volume levels. Consider using a metronome for rhythm."
            })
        
        # Determine proficiency level based on metrics
        proficiency_score = (10 - filler_percentage/2 + volume_stability + min(10, wpm/15)) / 3
        if proficiency_score >= 8:
            level = "Advanced"
        elif proficiency_score >= 6:
            level = "Intermediate"
        else:
            level = "Beginner"
        
        return {
            "overall_assessment": f"Analysis complete. Speaking pace: {wpm:.1f} WPM, Filler percentage: {filler_percentage:.1f}%, Volume stability: {volume_stability:.1f}/10",
            "language_proficiency": {
                "grammar_score": min(10, max(1, int(proficiency_score))),
                "vocabulary_score": min(10, max(1, int(proficiency_score))),
                "fluency_score": min(10, max(1, int(10 - filler_percentage/2))),
                "level": level,
                "explanation": "Assessment based on speaking metrics analysis"
            },
            "strengths": strengths if strengths else ["Speech analysis completed successfully"],
            "areas_for_improvement": improvements if improvements else ["Continue practicing for improvement"],
            "recommendations": recommendations if recommendations else [
                {
                    "title": "General Practice",
                    "description": "Continue practicing speaking to improve overall fluency and confidence."
                }
            ]
        }
