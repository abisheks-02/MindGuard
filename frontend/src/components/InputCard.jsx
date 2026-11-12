import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Mic, Square, Loader2, Sparkles } from 'lucide-react';

export default function InputCard({ onAnalyze, isLoading }) {
  const [text, setText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorder = useRef(null);
  const startTime = useRef(null);

  const handleAnalyze = () => {
    if (text.trim()) {
      onAnalyze(text);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      mediaRecorder.current.start();
      startTime.current = Date.now();
      setIsRecording(true);
      const audioChunks = [];
      mediaRecorder.current.addEventListener("dataavailable", event => {
        audioChunks.push(event.data);
      });
      mediaRecorder.current.addEventListener("stop", async () => {
        const durationSecs = (Date.now() - startTime.current) / 1000;
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('file', audioBlob);
        formData.append('duration', durationSecs.toString());
        try {
          const res = await axios.post('http://localhost:8000/analyze/voice', formData);
          // Update the text box with the transcribed text so user sees what they said
          setText(res.data.transcribed_text);
          // Fire the analyze event to update the parent component's dashboard
          onAnalyze(res.data.transcribed_text, res.data);
        } catch (e) {
          console.error("Voice analysis failed", e);
        }
      });
    } catch (e) {
      console.error("Microphone access denied");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current) {
      mediaRecorder.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="glass-card mb-6 relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-32 h-32 bg-cyan/10 rounded-full blur-3xl -mr-10 -mt-10 pointer-events-none"></div>
      
      <div className="relative z-10 flex gap-4">
        <div className="flex-1">
          <textarea
            placeholder="Type how you are feeling, or click the microphone to speak..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={isLoading || isRecording}
            className="w-full h-32 bg-transparent border-0 focus:ring-0 resize-none text-slate-700 placeholder:text-slate-400 font-medium"
          />
          <div className="flex justify-between items-center mt-2 border-t border-slate-100 pt-4">
            <span className="text-xs font-semibold text-slate-400 tracking-wider">
              {text.length} CHARACTERS
            </span>
            <div className="flex gap-3">
              {isRecording ? (
                <button onClick={stopRecording} className="flex items-center gap-2 px-4 py-2 rounded-full bg-coral/10 text-coral font-medium border border-coral/30 hover:bg-coral hover:text-white transition-all animate-pulse">
                  <Square size={16} fill="currentColor" /> Stop Recording
                </button>
              ) : (
                <button onClick={startRecording} disabled={isLoading} className="flex items-center gap-2 px-4 py-2 rounded-full bg-slate-50 text-slate-600 font-medium border border-slate-200 hover:border-cyan hover:text-cyan transition-all">
                  <Mic size={16} /> Voice Note
                </button>
              )}
              <button 
                className="btn-primary flex items-center gap-2" 
                onClick={handleAnalyze}
                disabled={!text.trim() || isLoading || isRecording}
              >
                {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Sparkles size={18} />}
                {isLoading ? 'Analyzing...' : 'Analyze'}
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
