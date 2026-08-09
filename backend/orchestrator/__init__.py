"""Pipeline runner -- the only place modules are sequenced.

Modules never import each other; the orchestrator imports all of them and
passes plain data between stages. It is therefore the only file where the
pipeline's true order is visible, and the only one exempt from the
module-isolation rule.

Wiring lands in SPRINT 1 (walking skeleton, stubbed stages).
"""
