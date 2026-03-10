import os
import re
from pydub import AudioSegment, silence
import speech_recognition as sr
from django.conf import settings

def analyze_speech(audio_file_path):
    """
    Analyzes an audio file for speech speed, filler words, and pauses.
    Returns a dictionary of results.
    """
    results = {
        'transcription': '',
        'wpm': 0.0,
        'total_fillers': 0,
        'filler_details': {},
        'pause_count': 0,
        'total_pause_duration': 0.0,
        'confidence_score': 0.0,
        'ai_feedback': ''
    }

    try:
        # Load audio (pydub requires ffmpeg)
        try:
            audio = AudioSegment.from_file(audio_file_path)
            duration_sec = len(audio) / 1000.0
        except (RuntimeError, Exception) as e:
            results['ai_feedback'] = "Audio processing skipped. Please ensure 'ffmpeg' is installed on the server for full analysis. "
            results['transcription'] = "[Audio Processing Error]"
            return results
        
        # 1. Pause Analysis
        try:
            pauses = silence.detect_silence(audio, min_silence_len=500, silence_thresh=audio.dBFS-16)
            results['pause_count'] = len(pauses)
            results['total_pause_duration'] = sum([(end - start) for start, end in pauses]) / 1000.0
        except Exception:
            results['ai_feedback'] += "Could not calculate pauses. "

        # 2. Transcription (using SpeechRecognition)
        r = sr.Recognizer()
        
        wav_path = audio_file_path + ".wav"
        try:
            audio.export(wav_path, format="wav")
            with sr.AudioFile(wav_path) as source:
                audio_data = r.record(source)
                text = r.recognize_google(audio_data)
                results['transcription'] = text
        except sr.UnknownValueError:
            results['transcription'] = "[Unintelligible]"
            results['ai_feedback'] += "The audio was too quiet or unclear to transcribe."
        except sr.RequestError:
            results['transcription'] = "[Transcription API Error]"
            results['ai_feedback'] += "Could not reach the transcription service."
        except Exception as e:
            results['transcription'] = "[Error]"
            results['ai_feedback'] += f"Transcription failed: {str(e)}"
        finally:
            if os.path.exists(wav_path):
                os.remove(wav_path)

        # Only continue with deep analysis if we have text
        if results['transcription'] and not results['transcription'].startswith("["):
            # 3. Speed Analysis (WPM)
            words = results['transcription'].split()
            word_count = len(words)
            if duration_sec > 0:
                results['wpm'] = (word_count / duration_sec) * 60

            # 4. Filler Word Detection
            filler_list = ['um', 'uh', 'ah', 'like', 'actually', 'basically', 'literally', 'you know']
            filler_counts = {}
            total_fillers = 0
            
            for filler in filler_list:
                pattern = r'\b' + re.escape(filler) + r'\b'
                matches = re.findall(pattern, results['transcription'], re.IGNORECASE)
                if matches:
                    count = len(matches)
                    filler_counts[filler] = count
                    total_fillers += count
            
            results['filler_details'] = filler_counts
            results['total_fillers'] = total_fillers

            # 5. Confidence Score and Feedback
            base_score = 100
            
            # WPM penalty
            if results['wpm'] < 110:
                base_score -= 15
                results['ai_feedback'] += "Try to speak a bit faster. "
            elif results['wpm'] > 170:
                base_score -= 15
                results['ai_feedback'] += "Speak a bit slower to ensure clarity. "
            else:
                results['ai_feedback'] += "Your speaking pace is excellent! "

            # Filler penalty
            if total_fillers > (word_count * 0.05):
                base_score -= 20
                results['ai_feedback'] += f"You used {total_fillers} filler words. "
            
            results['confidence_score'] = max(0, min(100, base_score))
        else:
            results['confidence_score'] = 0.0

    except Exception as e:
        results['ai_feedback'] = f"An unexpected error occurred: {str(e)}"
    
    return results
