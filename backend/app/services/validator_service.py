import json


def validate_rule(rule_query: str, event: dict):
    """
    Validates whether an event matches the Sigma detection rule.
    Returns a detailed verdict.
    """
    print("rule_query:", repr(rule_query))
    detection = json.loads(rule_query)

    detection = json.loads(rule_query)

    # Support both formats:
    # 1. {"detection":{"selection":{}}}
    # 2. {"selection":{}}

    if "detection" in detection:
        selection = detection.get("detection", {}).get(
            "selection",
            {}
        )
    else:
        selection = detection.get(
            "selection",
            {}
        )


    matched_fields = []

    print("Selection:", selection)
    print("Event:", event)


    for key, value in selection.items():

        event_value = event.get(key)


        if event_value is None:
            return {
                "status": "Missed",
                "confidence": 0,
                "matched_fields": matched_fields,
                "message": f"Field '{key}' is missing."
            }


        expected = value.replace("*", "").lower()


        if expected not in event_value.lower():
            return {
                "status": "Missed",
                "confidence": 0,
                "matched_fields": matched_fields,
                "message": f"Field '{key}' did not match."
            }


        matched_fields.append(key)


    return {
        "status": "Detected",
        "confidence": 95,
        "matched_fields": matched_fields,
        "message": "All required fields matched."
    }