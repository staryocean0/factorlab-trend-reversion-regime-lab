# Continue here — K-line recognizer transition policy v6

Thread continuation: optimize recognizer A only.

Completed:
- v4 improved point-state classification.
- v5 added generic probability hysteresis.

Current v5 limitation:
- state classification is useful;
- transition F1 remains the main bottleneck.

v6 direction:
- replace universal switching rule with transition-type policy;
- keep classifier fixed;
- keep independent judge fixed;
- avoid evaluator/tool stacking.

Next execution:
1. implement transition-type policy;
2. run pre-2025 rolling selection;
3. lock policy;
4. evaluate diagnostics.
