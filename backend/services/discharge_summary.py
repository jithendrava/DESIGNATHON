from backend.services.genai_service import GenAIService

_service = GenAIService()


def summary(name, language="English", risk=0, drivers=None, interventions=None):
    return _service.generate("discharge_summary", {
        "name": name,
        "language": language,
        "risk": risk,
        "drivers": drivers or [],
        "interventions": interventions or [],
    })