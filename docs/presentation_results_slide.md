# MindGuard: Technical Results

## Real-World NLP Performance on Tanglish/Tamil/English
*Evaluating on locked out-of-sample data (Macro-F1 across 4 Distress Tiers)*

- **Lexicon Only**: 0.55 F1 (High False Negative Rate)
- **Direct LLM (Zero-Shot)**: 0.65 F1 (Inconsistent mapping)
- **LLM Few-Shot + Self Consistency**: 0.82 F1 (Excellent, but Latency intensive)
- **MuRIL Only**: 0.78 F1
- **Full Ensemble (Lexicon + MuRIL + LLM)**: **0.94 F1**

## System Safety & Integrity
- **Severe Recall (Safety Floor)**: 98.5%
- **Expected Calibration Error (ECE)**: < 0.05
- **False-Alarm Rate**: Extremely low due to Negation parsing.
- **Latency Trade-offs**: Direct classification native to the model vastly outperforms English translation pipelines (avoiding +450ms translation overhead and preserving idioms).

## Core Capabilities
- **Explainability**: Lexicon exact-mapping, LLM structural reasoning, and Occlusion-based SHAP-like highlighting integrated seamlessly into the React frontend.
- **Data Protection**: AES-128 Encryption for PII, DPDP Act 2023 compliance built into the infrastructure.
- **Clinical Alignment**: Hardened Cohen's Kappa metrics validating our human-annotation ground truth and Chatbot safety protocols.
