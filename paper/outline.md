# Beyond Accuracy: Evaluating Deferral and Escalation Policies for Clinical AI in High-Stakes Triage

## Core claim
Clinical AI should not be evaluated only by prediction performance. In high-stakes settings, a useful system must also know when to answer, when to defer, and when to escalate.

## Research question
Does a safety-gated deferral / escalation layer reduce unsafe autonomous outputs compared with a raw triage model alone?

## Hypothesis
A structured safety layer will reduce unsafe outputs and improve handling of uncertain or high-risk cases, even if it reduces autonomous coverage.

## Methods
- Structured triage dataset
- Baseline multiclass risk classifier
- Safety gate using:
  - low confidence
  - self-consistency disagreement
  - missing critical information
  - high-risk rule triggers
- Compare raw model vs gated model

## Primary outcomes
- baseline accuracy
- unsafe raw output rate
- unsafe gated output rate
- defer rate
- escalate rate
- answer rate

## Figures to create
1. System diagram
2. Coverage vs safety plot
3. Unsafe output comparison bar chart
4. Action distribution chart