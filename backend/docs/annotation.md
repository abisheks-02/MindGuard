# MindGuard Annotation Guidelines

## Overview
These guidelines dictate how annotators should label the DravidianCodeMix subset and synthetic dev examples into our 4-tier severity system.

## The 4-Tier Severity Scale

### 0 - Normal
- **Definition**: General statements, positive emotions, or routine daily complaints with no distress.
- **Examples**:
  - "Innaiku romba nalla irunthuchu." (Today was very good.)
  - "I am watching a movie."

### 1 - Mild
- **Definition**: Minor stress, tiredness, situational sadness, or boredom. Easily resolvable.
- **Examples**:
  - "Office work is exhausting me."
  - "Konjam stress ah iruku." (Feeling a bit stressed.)

### 2 - Moderate
- **Definition**: Intense emotional pain, loneliness, clinical depression symptoms, or feeling like a burden. No explicit mention of death/self-harm.
- **Examples**:
  - "valikithu, everything is falling apart." (It hurts...)
  - "I feel so lonely all the time."
  - "Manasu romba kashtama iruku." (My mind is very troubled.)

### 3 - Severe
- **Definition**: Explicit or strong implicit mention of suicide, self-harm, giving up on life, or absolute hopelessness.
- **Examples**:
  - "I want to end it all."
  - "Sagalam pola iruku." (I feel like dying.)
  - "No point in living anymore."

## Annotation Procedure
1. Two independent annotators will label 200 samples.
2. Cohen's Kappa will be computed. If $\kappa < 0.70$, conflict resolution is required.
3. Discrepancies involving `Severe` cases must be reviewed by a lead clinician.
