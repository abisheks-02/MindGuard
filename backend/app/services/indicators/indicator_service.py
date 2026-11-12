import logging
import librosa
import numpy as np
import yaml
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.models.indicator import ExploratoryIndicator

logger = logging.getLogger(__name__)

class IndicatorsService:
    def __init__(self, db: Session, config_path: str = "config/indicators.yaml"):
        self.db = db
        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load indicator config, using defaults: {e}")
            self.config = {"compute_speech_metrics": True, "compute_linguistic_metrics": True}

    def process_audio(self, session_id: str, file_path: str, transcript: str) -> dict:
        """Processes audio file and transcript to generate non-diagnostic indicators."""
        metrics = {}
        
        if self.config.get("compute_speech_metrics", True):
            try:
                speech_metrics = self._extract_speech_metrics(file_path)
                metrics.update(speech_metrics)
            except Exception as e:
                logger.error(f"Speech metric extraction failed: {e}")
                
        if self.config.get("compute_linguistic_metrics", True) and transcript:
            try:
                ling_metrics = self._extract_linguistic_metrics(transcript)
                metrics.update(ling_metrics)
            except Exception as e:
                logger.error(f"Linguistic metric extraction failed: {e}")

        # Store raw metrics
        indicator = ExploratoryIndicator(
            session_id=session_id,
            wpm=metrics.get("wpm"),
            pause_ratio=metrics.get("pause_ratio"),
            mean_pause_length=metrics.get("mean_pause_length"),
            pitch_variance=metrics.get("pitch_variance"),
            cmi=metrics.get("cmi"),
            switch_point_freq=metrics.get("switch_point_freq"),
            tamil_roman_ratio=metrics.get("tamil_roman_ratio")
        )
        self.db.add(indicator)
        self.db.commit()
        self.db.refresh(indicator)
        
        # Calculate z-scores against user baseline
        return self._format_response(indicator, transcript)

    def _extract_speech_metrics(self, file_path: str) -> dict:
        """Extracts prosodic features using librosa."""
        # Note: This is an exploratory estimation implementation
        y, sr = librosa.load(file_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Pitch variance (F0)
        f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        valid_f0 = f0[voiced_flag]
        pitch_variance = float(np.var(valid_f0)) if len(valid_f0) > 0 else 0.0

        # Silences / Pauses
        intervals = librosa.effects.split(y, top_db=20)
        total_voiced_duration = sum([(end - start) / sr for start, end in intervals])
        total_pause_duration = duration - total_voiced_duration
        pause_ratio = float(total_pause_duration / duration) if duration > 0 else 0.0
        
        pause_lengths = []
        if len(intervals) > 1:
            for i in range(len(intervals) - 1):
                pause_len = (intervals[i+1][0] - intervals[i][1]) / sr
                if pause_len > 0.1: # Consider pauses > 100ms
                    pause_lengths.append(pause_len)
        mean_pause = float(np.mean(pause_lengths)) if pause_lengths else 0.0

        # WPM (rough estimate based on voiced duration assuming 3 syllables/sec on average)
        estimated_words = total_voiced_duration * 2.5
        wpm = float((estimated_words / duration) * 60) if duration > 0 else 0.0

        return {
            "wpm": round(wpm, 2),
            "pause_ratio": round(pause_ratio, 2),
            "mean_pause_length": round(mean_pause, 2),
            "pitch_variance": round(pitch_variance, 2)
        }

    def _extract_linguistic_metrics(self, transcript: str) -> dict:
        """Extracts code-switching features from tokenized text."""
        tokens = transcript.lower().split()
        if not tokens:
            return {}

        tamil_count = 0
        english_count = 0
        switches = 0
        prev_lang = None

        # Highly simplified heuristic language tagger for demo purposes
        # In prod, we would use an actual token-level LID model or fasttext
        english_common = {"i", "me", "my", "you", "and", "but", "so", "like", "feel", "very", "sad", "the", "is", "a"}
        
        for token in tokens:
            lang = "en" if token in english_common or all(c.isascii() for c in token) else "ta"
            if lang == "en":
                english_count += 1
            else:
                tamil_count += 1

            if prev_lang and lang != prev_lang:
                switches += 1
            prev_lang = lang

        total_tokens = len(tokens)
        cmi = (total_tokens - max(tamil_count, english_count)) / total_tokens if total_tokens > 0 else 0.0
        switch_freq = switches / total_tokens if total_tokens > 0 else 0.0
        t_r_ratio = tamil_count / english_count if english_count > 0 else float(tamil_count)

        return {
            "cmi": round(cmi, 2),
            "switch_point_freq": round(switch_freq, 2),
            "tamil_roman_ratio": round(t_r_ratio, 2)
        }

    def _format_response(self, indicator: ExploratoryIndicator, transcript: str) -> dict:
        """Appends user-specific z-score baselines."""
        history = self.db.query(ExploratoryIndicator).filter(ExploratoryIndicator.session_id == indicator.session_id).all()
        
        def calculate_z(metric_name: str, current_value: float):
            if current_value is None: return None
            values = [getattr(h, metric_name) for h in history if getattr(h, metric_name) is not None]
            if len(values) < 3:
                return {"value": current_value, "z_score": 0.0, "status": "insufficient_baseline"}
            
            mean = np.mean(values)
            std = np.std(values)
            if std == 0:
                z = 0.0
            else:
                z = (current_value - mean) / std
                
            status = "at_baseline"
            if z > 1.0: status = "above_baseline"
            elif z < -1.0: status = "below_baseline"
                
            return {"value": current_value, "z_score": round(z, 2), "status": status}

        return {
            "disclaimer": "These metrics are exploratory research tools to track personal baselines over time. They are NOT diagnostic indicators and should never replace clinical judgment.",
            "transcript": transcript,
            "wpm": calculate_z("wpm", indicator.wpm),
            "pause_ratio": calculate_z("pause_ratio", indicator.pause_ratio),
            "mean_pause_length": calculate_z("mean_pause_length", indicator.mean_pause_length),
            "pitch_variance": calculate_z("pitch_variance", indicator.pitch_variance),
            "cmi": calculate_z("cmi", indicator.cmi),
            "switch_point_freq": calculate_z("switch_point_freq", indicator.switch_point_freq),
            "tamil_roman_ratio": calculate_z("tamil_roman_ratio", indicator.tamil_roman_ratio),
        }
