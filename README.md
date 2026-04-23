# SafeTriage: Safety-Gated Clinical AI Triage

*A prototype system for evaluating decision behavior in clinical AI under uncertainty.*

## Overview

SafeTriage is a prototype clinical AI system that models how AI should behave under uncertainty in high-stakes care. Rather than optimizing for prediction alone, the system introduces a safety-gated action layer that determines whether to answer, defer, or escalate.

## Core Idea

Clinical AI should not always produce an answer. In real-world care, safe behavior often requires deferral or escalation when confidence is low, information is incomplete, or high-risk signals are present.

## Why This Matters

Most clinical AI systems are evaluated based on predictive performance alone. In real-world settings, however, the key question is not just whether a model is accurate, but whether it behaves safely under uncertainty.

This project reframes evaluation from prediction quality to decision behavior, emphasizing when a system should not act autonomously.

## System Design

The system consists of two components:

1. **Baseline risk model**  
   A multiclass classifier predicts one of four risk categories:
   - low
   - moderate
   - urgent
   - emergent

2. **Safety-gated action layer**  
   A rule-based safety layer determines whether the system should:
   - answer
   - defer
   - escalate

The safety gate uses:
- high-risk rule triggers  
- missing critical information  
- low confidence  
- low agreement  

## Key Results

- Baseline accuracy: **0.68**  
- Unsafe raw output rate: **0.0975**  
- Unsafe gated output rate: **0.0000**  
- Defer rate: **0.28**  
- Escalate rate: **0.58**  
- Answer rate: **0.1375**  

## Interpretation

A structured safety gate can eliminate unsafe autonomous outputs while redistributing decisions toward deferral and escalation. This reframes clinical AI evaluation from prediction quality alone to decision behavior under uncertainty.

## Abstract

Clinical artificial intelligence (AI) systems are typically evaluated based on predictive performance, yet this does not capture how systems behave under uncertainty and high-risk conditions. In real clinical settings, safe decision-making often requires deferral or escalation rather than forced prediction.

We developed a prototype clinical triage system consisting of a baseline multiclass risk classifier and a rule-based safety gate. The safety layer determines whether to return a prediction, defer due to uncertainty or missing information, or escalate due to high-risk signals. System behavior was compared with and without the safety gate using simulated triage cases.

The baseline model achieved an accuracy of 0.68, with an unsafe raw output rate of 0.0975. The safety-gated action layer reduced the unsafe output rate to 0.0000. This improvement was accompanied by a shift in system behavior, with a defer rate of 0.28, an escalate rate of 0.58, and an answer rate of 0.1375.

A structured safety-gated action layer can eliminate unsafe autonomous outputs while redistributing decisions toward deferral and escalation. These findings suggest that clinical AI systems should be evaluated not only on predictive performance but also on decision behavior under uncertainty, with explicit mechanisms for safe handling of high-risk and ambiguous cases.

## Repository Structure

- `src/` — model training, evaluation, and safety gate code  
- `data/` — processed triage cases  
- `results/` — evaluation outputs and figures  
- `paper/` — outline and abstract  

## Future Directions

- Prospective evaluation in real clinical workflows  
- Adaptive safety gating based on context and feedback  
- Integration into clinical decision support systems  
- Extension to multimodal inputs such as text, imaging, and signals  
