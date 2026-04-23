Background:
Clinical artificial intelligence (AI) systems are typically evaluated based on predictive performance, yet this does not capture how systems behave under uncertainty or in high-risk situations. In real clinical settings, safe decision-making often requires deferral or escalation rather than forced prediction.

Objective:
To evaluate whether a structured safety-gated action layer can reduce unsafe autonomous outputs while providing a more realistic representation of decision behavior in clinical triage.

Methods:
We developed a prototype clinical triage system consisting of a baseline multiclass risk classifier and a rule-based safety gate. The safety layer determines whether to return a prediction, defer due to uncertainty or missing information, or escalate due to high-risk signals. System behavior was compared with and without the safety gate using simulated triage cases.

Results:
The baseline model achieved an accuracy of 0.68, with an unsafe raw output rate of 0.0975. The safety-gated action layer reduced the unsafe output rate to 0.0000. This improvement was accompanied by a shift in system behavior, with a defer rate of 0.28, an escalate rate of 0.58, and an answer rate of 0.1375.

Conclusion:
A structured safety-gated action layer can eliminate unsafe autonomous outputs while redistributing decisions toward deferral and escalation. These findings suggest that clinical AI systems should be evaluated not only on predictive performance but also on decision behavior under uncertainty, with explicit mechanisms for safe handling of high-risk and ambiguous cases.