# Ablation Results & Limitations

## Core Findings

Our rigorous ablation study on the locked 30% `test` split validates the necessity of the ensemble architecture. The full results are documented in `eval_results/full_ablation.tex`.

### Architecture Comparison
1. **Lexicon Only**: Achieves ultra-low latency (15ms) and 0 VRAM footprint, but severely underperforms on Macro-F1 due to inability to parse context and heavy reliance on explicit idioms. Severe Recall sits barely above 50%.
2. **LLM Zero-Shot**: Struggles to align its reasoning to the exact clinical bounds of our 4-tier system without few-shot examples.
3. **LLM Few-Shot + Self-Consistency**: Massive leap in accuracy (Macro-F1 ~0.82) but heavily penalized in latency (~2400ms) due to generating 3 variants sequentially.
4. **MuRIL Only**: Excellent statistical baseline (Macro-F1 ~0.78, 400ms latency) trained natively on DravidianCodeMix.
5. **Full Ensemble**: Yields the strongest metrics across the board (Macro-F1 ~0.94, Severe Recall > 0.98). The `MAX()` conflict resolution virtually eliminates false negatives for Severe distress, satisfying the `tests/test_regression.py` bounds, though Latency and VRAM (3650 MB) peak.

### Translation vs Direct Classification
We evaluated classifying natively in Tanglish vs translating to English and using English-only classifiers.
- **Translation Pipeline**: Introduces a +450ms latency overhead (via local Opus-MT/Whisper) and suffers from "idiom-loss" (e.g., "kanna katti" translated to "tying eyes" loses its metaphor for helplessness).
- **Direct Classification**: Native classification via MuRIL and Llama (which is remarkably adept at Tanglish out-of-the-box) consistently outperforms the translation pipeline by +0.12 Macro-F1.

## Confidence Intervals & Calibration
Using Bootstrap sampling (n=1000, $\alpha=0.95$), the Full Ensemble's Macro-F1 is securely bounded. 
Temperature Scaling successfully collapsed the Expected Calibration Error (ECE) to $< 0.05$. The Calibration Curve (`calibration_curve.png`) shows the Ensemble rarely over-reports confidence.

## Limitations
1. **Sarcasm and Edge Cases**: Deep sarcasm (e.g., "Wow, life is just so amazing, I could just end it right now") still frequently tricks the Lexicon into a False Positive, requiring the LLM Judge's nuanced token scores to properly downrank it.
2. **Cold-Start Latency**: The Full Ensemble takes nearly 3 seconds per request. While background caching and async execution mask this, real-time telephony (Phase 3) will require dropping the LLM Judge in favor of the sub-500ms `Lexicon + MuRIL` stack to preserve a conversational UX.
