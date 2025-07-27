from __future__ import annotations

from typing import Dict, List, Optional

from .rule import Rule

class RuleManager:
    """Minimal rule manager for handling rules"""

    def __init__(self) -> None:
        self.rules: Dict[str, Rule] = {}
        self.active_rules: List[Rule] = []

    def add_rule(self, rule: Rule) -> None:
        self.rules[rule.id] = rule
        self.active_rules.append(rule)

    def get_rule(self, rule_id: str) -> Optional[Rule]:
        return self.rules.get(rule_id)

    def remove_rule(self, rule_id: str) -> None:
        rule = self.rules.pop(rule_id, None)
        if rule and rule in self.active_rules:
            self.active_rules.remove(rule)
