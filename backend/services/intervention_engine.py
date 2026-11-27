def recommend(risk, drivers=None):
    drivers = drivers or []
    if risk >= 70:
        actions = ["Priority 48-hour follow-up call", "Medication reconciliation", "Care manager review"]
    elif risk >= 40:
        actions = ["Schedule 7-day follow-up", "Medication review"]
    else:
        actions = ["Standard discharge education"]

    driver_text = " ".join(drivers).lower()
    if "length" in driver_text:
        actions.append("Post-discharge condition check")
    if "admission" in driver_text:
        actions.append("Coordinate community support")
    if "medication" in driver_text or "polypharmacy" in driver_text:
        actions.append("Pharmacist counseling")

    return list(dict.fromkeys(actions))