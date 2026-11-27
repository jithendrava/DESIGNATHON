def summary(name, language="English"):
    if language == "Hindi":
        return (
            f"{name} के लिए: निर्धारित दवाएँ तय समय पर लें, लाल झंडे वाले लक्षणों पर तुरंत मदद लें, "
            "और अपनी नियोजित डिस्चार्ज के बाद की मुलाक़ात में शामिल हों।"
        )
    return (
        f"{name}: Take all medicines exactly as prescribed, watch for worsening symptoms, "
        "and attend your scheduled follow-up appointment."
    )