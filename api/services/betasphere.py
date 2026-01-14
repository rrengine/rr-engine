class BetaSphere:
    def decide(self, event_type: str, payload: dict) -> dict:

        # System lifecycle
        if event_type == "system_boot":
            return {
                "decision_type": "act",
                "action": "continue_monitoring",
                "reason": "boot_ok"
            }

        # 🔑 DESIGN INTELLIGENCE
        if event_type == "design_intent":
            intent = payload.get("intent")

            if intent == "optimize_comfort":
                return {
                    "decision_type": "act",
                    "action": "optimize_comfort",
                    "reason": "explicit design intent"
                }

            if intent == "modify_geometry":
                return {
                    "decision_type": "act",
                    "action": "modify_geometry",
                    "reason": "geometry modification requested"
                }

            return {
                "decision_type": "act",
                "action": intent or "no_op",
                "reason": "generic design intent"
            }

        # Default safe behavior
        return {
            "decision_type": "act",
            "action": "no_op",
            "reason": "no matching decision rule"
        }
