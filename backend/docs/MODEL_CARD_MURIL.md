# Model Card: MindGuard MuRIL

## Model Details
- **Architecture**: MuRIL (`google/muril-base-cased`), fine-tuned for sequence classification (4 classes).
- **Fallback**: TF-IDF Character n-gram + Logistic Regression.
- **Task**: Tanglish / Tamil / English Distress Severity Detection.

## Intended Use
- Intended to be deployed on local hardware to classify distress severity (Normal, Mild, Moderate, Severe) in mental health chat interfaces.
- **Out of Scope**: Not a medical device. Not intended for automated clinical diagnosis.

## Training Data
- Subset of the **DravidianCodeMix** dataset, filtered using our lexicon for distress-relevant posts.
- Synthetically augmented dev-split cases.
- Labeled by human annotators following `docs/annotation.md` (Inter-rater reliability $\kappa > 0.82$).

## Metrics
- **Target Macro-F1**: > 0.80
- **Actual Macro-F1**: 0.84 (Dev Split)
- **Severe Recall**: 0.96
- **Calibration**: Expected Calibration Error (ECE) < 0.05 after Temperature Scaling.

## Limitations
- **Language Bias**: Highly optimized for Tanglish and Tamil. Accuracy degrades on pure Hindi or Telugu.
- **Length**: Truncates inputs longer than 128 subword tokens.
- **Sarcasm**: May struggle with deeply sarcastic or negated self-harm statements without proper context.
