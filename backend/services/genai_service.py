import os
from typing import Any

import requests


class GenAIService:
    """Safe, structured language-generation service for the readmission demo."""

    def __init__(self) -> None:
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")

    def is_configured(self) -> bool:
        return bool(self.endpoint and self.api_key and self.deployment)

    def generate(self, task: str, payload: dict[str, Any]) -> dict[str, Any]:
        language = payload.get("language", "English")
        name = payload.get("name", "the patient")
        risk = payload.get("risk", 0)
        drivers = payload.get("drivers", [])
        interventions = payload.get("interventions", [])

        if self.is_configured():
            try:
                return self._call_azure(task, language, name, risk, drivers, interventions)
            except requests.RequestException as exc:
                return self._fallback(task, language, name, risk, drivers, interventions,
                                      detail=f"Gen AI provider unavailable: {exc}")

        return self._fallback(task, language, name, risk, drivers, interventions)

    def _call_azure(self, task: str, language: str, name: str, risk: int,
                    drivers: list[str], interventions: list[str]) -> dict[str, Any]:
        instructions = (
            "You are a clinical communication assistant. Write concise, patient-safe draft text. "
            "Do not diagnose, change medicines, or calculate risk. Use only the supplied structured facts. "
            "Label the text as a draft requiring clinician review. "
            "Use plain language and include urgent warning-sign guidance for emergencies."
        )

        if task == "discharge_summary":
            request_text = (
                f"Create a {language} discharge summary for {name}. "
                f"Readmission risk tier: {risk}%. Top drivers: {', '.join(drivers)}. "
                f"Clinician-approved interventions: {', '.join(interventions) or 'standard follow-up'}."
            )
        elif task == "clinician_note":
            request_text = (
                f"Draft a concise clinician review note for {name}, readmission risk {risk}%. "
                f"Risk drivers: {', '.join(drivers)}. Proposed interventions: {', '.join(interventions)}. "
                "Do not approve or replace clinical judgment; provide a neutral draft for review."
            )
        else:
            request_text = (
                f"Draft a short {language} post-discharge reminder for {name}. "
                f"Risk drivers: {', '.join(drivers)}. Follow-up actions: {', '.join(interventions)}."
            )

        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions"
        response = requests.post(
            url,
            headers={"api-key": self.api_key, "Content-Type": "application/json"},
            params={"api-version": self.api_version},
            json={
                "messages": [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": request_text},
                ],
                "temperature": 0.2,
                "max_tokens": 350,
            },
            timeout=30,
        )
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"].strip()
        return {"text": text, "provider": "azure-openai", "draft": True,
                "clinician_review_required": True}

    def _fallback(self, task: str, language: str, name: str, risk: int,
                  drivers: list[str], interventions: list[str], detail: str | None = None) -> dict[str, Any]:
        if language.lower() == "hindi":
            if task == "clinician_note":
                text = (
                    f"{name} का पढ़मित 30-दिन पुन: भर्ती जोखिम {risk}% है। प्रमुख संकेतक: "
                    f"{', '.join(drivers) or 'कोई प्रमुख संकेतक उपलब्ध नहीं'}। प्रस्तावित कार्य: "
                    f"{', '.join(interventions) or 'मानक फॉलो-अप'}। कृपया चिकित्सकीय निर्णय दर्ज करें।"
                )
            elif task == "reminder":
                text = (
                    f"{name}, कृपया निर्धारित फॉलो-अप रखें, दवाएँ निर्धारित समय पर लें, "
                    "और किसी खतरे के संकेत पर तुरंत चिकित्सकीय सहायता लें।"
                )
            else:
                text = (
                    f"ड्राफ्ट — {name} के लिए: निर्धारित दवाएँ तय समय पर लें, "
                    "लक्षण बिगड़ने या आपात स्थिति में तुरंत सहायता लें, और नियोजित फॉलो-अप में शामिल हों। "
                    "इस सामग्री की चिकित्सक से समीक्षा आवश्यक है।"
                )
        else:
            if task == "clinician_note":
                text = (
                    f"Draft review note: {name} has an estimated 30-day readmission risk of {risk}%. "
                    f"Top drivers include {', '.join(drivers) or 'no dominant driver identified'}. "
                    f"Consider {', '.join(interventions) or 'standard follow-up'} and document final clinical judgment."
                )
            elif task == "reminder":
                text = (
                    f"Hello {name}. Please attend your follow-up, take medicines exactly as prescribed, "
                    "and seek urgent help if your symptoms worsen."
                )
            else:
                text = (
                    f"Draft for {name}: Take all medicines exactly as prescribed, watch for worsening symptoms, "
                    "and attend your scheduled follow-up. Seek urgent medical help if warning signs develop. "
                    "Please ask a clinician to review this draft before use."
                )

        result = {"text": text, "provider": "offline-safe-fallback", "draft": True,
                  "clinician_review_required": True}
        if detail:
            result["warning"] = detail
        return result
