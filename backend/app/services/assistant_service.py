"""Multilingual Agricultural AI Assistant Service.

Provides context-aware advisory in 8 languages:
English (en), Kannada (kn), Hindi (hi), Telugu (te),
Tamil (ta), Malayalam (ml), Marathi (mr), Bengali (bn).
"""

from __future__ import annotations

import re
from typing import Any
from app.schemas.assistant import AssistantContext


SUPPORTED_LANGUAGES = {
    "en": "English",
    "kn": "Kannada",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
}

# Multi-lingual keyword maps for intent detection across 8 languages
INTENT_KEYWORDS = {
    "crop_recommendation": [
        # English
        "crop", "recommend", "plant", "grow", "cultivate", "sow", "variety", "which crop",
        # Kannada (ಕನ್ನಡ)
        "ಬೆಳೆ", "ಶಿಫಾರಸು", "ಯಾವ ಬೆಳೆ", "ಬಿತ್ತನೆ", "ಬೆಳೆಯಬೇಕು", "ಕೃಷಿ", "ತಳಿ",
        # Hindi (हिन्दी)
        "फसल", "सिफारिश", "कौन सी फसल", "बोना", "उगाना", "पैदावार", "किस्म",
        # Telugu (తెలుగు)
        "పంట", "సిఫార్సు", "ఏ పంట", "విత్తడం", "సాగు", "రకం",
        # Tamil (தமிழ்)
        "பயிர்", "பரிந்துரை", "எந்த பயிர்", "விதைக்க", "பயிரிட", "வகை",
        # Malayalam (മലയാളം)
        "വിള", "ശുപാർശ", "ഏത് വിള", "കൃഷി", "വിത്ത്",
        # Marathi (मराठी)
        "पीक", "शिफारस", "कोणते पीक", "पेरणी", "लागवड", "वाण",
        # Bengali (বাংলা)
        "ফসল", "সুপারিশ", "কোন ফসল", "বপন", "চাষ", "জাত",
    ],
    "soil_npk": [
        # English
        "npk", "nitrogen", "phosphorus", "potassium", "fertilizer", "nutrient", "urea", "dap", "potash",
        # Kannada
        "ಸಾರಜನಕ", "ರಂಜಕ", "ಪೊಟ್ಯಾಷ್", "ರಸಗೊಬ್ಬರ", "ಪೋಷಕಾಂಶ", "ಯೂರಿಯಾ", "ಎನ್ಪಿಕೆ",
        # Hindi
        "नाइट्रोजन", "फास्फोरस", "पोटाश", "उर्वरक", "खाद", "पोषक तत्व", "यूरिया", "एनपीके",
        # Telugu
        "నత్రజని", "భాస్వరం", "పొటాషియం", "ఎరువులు", "పోషకాలు", "యూరియా",
        # Tamil
        "நைட்ரஜன்", "பாஸ்பரஸ்", "பொட்டாசியம்", "உரம்", "யூரியா",
        # Malayalam
        "നൈട്രജൻ", "ഫോസ്ഫറസ്", "പൊട്ടാസ്യം", "വളം", "യൂറിയ",
        # Marathi
        "नायट्रोजन", "फॉस्फरस", "पोटॅश", "खत", "युरिया", "पोषकद्रव्ये",
        # Bengali
        "নাইট্রোজেন", "ফসফরাস", "পটাশিয়াম", "সার", "ইউরিয়া", "পুষ্টি",
    ],
    "soil_ph": [
        # English
        "ph", "acid", "alkaline", "saline", "lime", "gypsum", "soil health",
        # Kannada
        "ಪಿಎಚ್", "ಆಮ್ಲೀಯ", "ಕ್ಷಾರೀಯ", "ಸುಣ್ಣ", "ಜಿಪ್ಸಮ್", "ಮಣ್ಣಿನ ಆರೋಗ್ಯ",
        # Hindi
        "पीएच", "अम्लीय", "क्षारीय", "चूना", "जिप्सम", "मृदा स्वास्थ्य",
        # Telugu
        "పీహెచ్", "ఆమ్ల", "క్షార", "సున్నం", "జిప్సం",
        # Tamil
        "பிஹெச்", "அமில", "கார", "சுண்ணாம்பு", "ஜிப்சம்",
        # Malayalam
        "പിഎച്ച്", "അമ്ല", "ക്ഷാര", "കുമ്മായം", "ജിപ്സം",
        # Marathi
        "पीएच", "आम्ल", "अल्कधर्मी", "चुना", "जिप्सम",
        # Bengali
        "পিএইচ", "অম্লীয়", "ক্ষারীয়", "চুন", "জিপসাম",
    ],
    "soil_moisture": [
        # English
        "moisture", "water", "irrigation", "dry", "drip", "sprinkler",
        # Kannada
        "ತೇವಾಂಶ", "ನೀರು", "ನೀರಾವರಿ", "ಒಣ", "ಹನಿ ನೀರಾವರಿ",
        # Hindi
        "नमी", "पानी", "सिंचाई", "सूखा", "ड्रिप", "फुहारा",
        # Telugu
        "తేమ", "నీరు", "నీటిపారుదల", "డ్రిప్",
        # Tamil
        "ஈரப்பதம்", "தண்ணீர்", "பாசனம்", "சொட்டு நீர்",
        # Malayalam
        "ഈർപ്പം", "വെള്ളം", "നനയ്ക്കൽ", "തുള്ളി നന",
        # Marathi
        "ओलावा", "पाणी", "सिंचन", "ठिबक",
        # Bengali
        "আর্দ্রতা", "জল", "সেচ", "ড্রিপ",
    ],
    "weather": [
        # English
        "weather", "rain", "temperature", "forecast", "monsoon", "climate", "storm",
        # Kannada
        "ಹವಾಮಾನ", "ಮಳೆ", "ತಾಪಮಾನ", "ಮುನ್ಸೂಚನೆ", "ಮಾನ್ಸೂನ್",
        # Hindi
        "मौसम", "बारिश", "तापमान", "पूर्वानुमान", "मानसून",
        # Telugu
        "వాతావరణం", "వర్షం", "ఉష్ణోగ్రత", "అంచనా",
        # Tamil
        "வானிலை", "மழை", "வெப்பநிலை", "முன்னறிவிப்பு",
        # Malayalam
        "കാലാവസ്ഥ", "മഴ", "താപനില", "പ്രവചനം",
        # Marathi
        "हवामान", "पाऊस", "तापमान", "अंदाज",
        # Bengali
        "আবহাওয়া", "বৃষ্টি", "তাপমাত্রা", "পূর্বাভাস",
    ],
    "msp": [
        # English
        "msp", "minimum support price", "floor price", "government price", "fair price",
        # Kannada
        "ಎಂಎಸ್ಪಿ", "ಬೆಂಬಲ ಬೆಲೆ", "ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ", "ಸರ್ಕಾರಿ ದರ",
        # Hindi
        "एमएसपी", "न्यूनतम समर्थन मूल्य", "सरकारी मूल्य", "समर्थन मूल्य",
        # Telugu
        "ఎంఎస్పీ", "మద్దతు ధర", "కనీస మద్దతు ధర",
        # Tamil
        "எம்எஸ்பி", "குறைந்தபட்ச ஆதரவு விலை", "அரசு விலை",
        # Malayalam
        "എംഎസ്പി", "താങ്ങുവില",
        # Marathi
        "एमएसपी", "हमीभाव", "किमान आधारभूत किंमत",
        # Bengali
        "এমএসপি", "ন্যূনতম সহায়ক মূল্য", "সহায়ক মূল্য",
    ],
    "mandi_price": [
        # English
        "mandi", "market price", "modal price", "rates", "wholesale", "selling",
        # Kannada
        "ಮಂಡಿ", "ಮಾರುಕಟ್ಟೆ ಬೆಲೆ", "ದರ", "ಮಾರಾಟ",
        # Hindi
        "मंडी", "बाजार भाव", "मंडी भाव", "दाम", "कीमत",
        # Telugu
        "మండి", "మార్కెట్ ధర", "రేటు", "ధరలు",
        # Tamil
        "மண்டி", "சந்தை விலை", "விலை",
        # Malayalam
        "മാർക്കറ്റ് വില", "ചന്ത വില",
        # Marathi
        "बाजारभाव", "मंडी भाव", "किंमत",
        # Bengali
        "মন্ডি", "বাজার দর", "দাম",
    ],
    "pest_disease": [
        # English
        "pest", "disease", "insect", "fungus", "pesticide", "neem", "blight", "cure",
        # Kannada
        "ಕೀಟ", "ರೋಗ", "ಹುಳು", "ಶಿಲೀಂಧ್ರ", "ಕೀಟನಾಶಕ", "ಬೇವು",
        # Hindi
        "कीट", "रोग", "बीमारी", "कीड़ा", "कीटनाशक", "फफूंद", "नीम",
        # Telugu
        "తెగులు", "కీటకాలు", "పురుగులు", "పురుగుమందు",
        # Tamil
        "பூச்சி", "நோய்", "பூச்சிக்கொல்லி",
        # Malayalam
        "കീടം", "രോഗം", "കീടനാശിനി",
        # Marathi
        "कीड", "रोग", "अळी", "कीटकनाशक", "बुरशी",
        # Bengali
        "কীটপতঙ্গ", "রোগ", "পোকা", "কীটনাশক",
    ],
}


def _detect_intent(message: str) -> str:
    """Detect the farmer's intent using multi-lingual keyword analysis."""
    text = message.lower()
    scores: dict[str, int] = {}
    for intent, kws in INTENT_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in text)
        if score > 0:
            scores[intent] = score

    if scores:
        return max(scores, key=scores.get)  # type: ignore[arg-type]
    return "general"


def _format_context_summary(context: AssistantContext | None) -> dict[str, Any]:
    if not context:
        return {}
    summary: dict[str, Any] = {}
    if context.farm_id is not None:
        summary["farm_id"] = context.farm_id
    if context.area_acres is not None:
        summary["area_acres"] = context.area_acres
    if context.soil_ph is not None:
        summary["soil_ph"] = context.soil_ph
    if context.nitrogen is not None:
        summary["nitrogen"] = context.nitrogen
    if context.phosphorus is not None:
        summary["phosphorus"] = context.phosphorus
    if context.potassium is not None:
        summary["potassium"] = context.potassium
    if context.moisture is not None:
        summary["moisture"] = context.moisture
    if context.soil_type:
        summary["soil_type"] = context.soil_type
    if context.temperature is not None:
        summary["temperature"] = context.temperature
    if context.weather_condition:
        summary["weather_condition"] = context.weather_condition
    if context.recommended_crops:
        summary["recommended_crops"] = context.recommended_crops
    if context.mandi_price is not None:
        summary["mandi_price"] = context.mandi_price
    if context.msp_price is not None:
        summary["msp_price"] = context.msp_price
    return summary


# Advisory generators for each of the 8 languages
def _generate_en(intent: str, ctx: AssistantContext | None) -> tuple[str, list[str]]:
    has_soil = ctx and (ctx.nitrogen is not None or ctx.soil_ph is not None)
    has_weather = ctx and ctx.temperature is not None
    has_reco = ctx and ctx.recommended_crops

    if intent == "crop_recommendation":
        resp = "🌾 **Crop Recommendation Advisory**\n\n"
        if has_reco:
            recos = ", ".join(ctx.recommended_crops[:3])
            resp += f"Based on your farm's soil and local weather analysis, your top recommended crops are **{recos}**.\n\n"
        elif has_soil:
            resp += f"With your soil NPK ({ctx.nitrogen or '--'} N, {ctx.phosphorus or '--'} P, {ctx.potassium or '--'} K) and pH {ctx.soil_ph or '--'}, cereal crops such as Wheat and Maize or leguminous pulses like Chickpea and Soyabean are highly suitable.\n\n"
        else:
            resp += "To give you accurate crop recommendations, ensure your farm soil readings (N, P, K, pH, and moisture) are recorded in the 'My Farms' tab.\n\n"
        resp += "• **Sowing Advice:** Plant during the recommended seasonal window with certified seeds.\n• **Soil Prep:** Ensure deep ploughing and basal application of well-decomposed organic manure (FYM).\n• **Spacing:** Follow recommended inter-row spacing to maximize yield."
        suggs = ["What fertilizer dosage is needed?", "How is the market price for these crops?", "What is the weather impact on sowing?"]
        return resp, suggs

    if intent == "soil_npk":
        resp = "🧪 **Soil Nutrient (NPK) Management**\n\n"
        if has_soil:
            n = ctx.nitrogen if ctx.nitrogen is not None else "N/A"
            p = ctx.phosphorus if ctx.phosphorus is not None else "N/A"
            k = ctx.potassium if ctx.potassium is not None else "N/A"
            resp += f"**Your Farm Readings:** Nitrogen: **{n} kg/ha**, Phosphorus: **{p} kg/ha**, Potassium: **{k} kg/ha**.\n\n"
            if isinstance(ctx.nitrogen, (int, float)) and ctx.nitrogen < 50:
                resp += "⚠️ **Low Nitrogen:** Apply split doses of Urea (46% N) or Neem-coated urea at sowing and tillering stage.\n"
            elif isinstance(ctx.nitrogen, (int, float)) and ctx.nitrogen >= 50:
                resp += "✅ **Adequate Nitrogen:** Maintain current balanced application without over-fertilizing.\n"
            if isinstance(ctx.phosphorus, (int, float)) and ctx.phosphorus < 25:
                resp += "⚠️ **Phosphorus Deficiency:** Incorporate DAP (Di-Ammonium Phosphate) or Single Super Phosphate (SSP) near root zone.\n"
            if isinstance(ctx.potassium, (int, float)) and ctx.potassium < 30:
                resp += "⚠️ **Potassium Deficiency:** Apply Muriate of Potash (MOP) to boost disease resistance and grain filling.\n"
        else:
            resp += "A balanced N:P:K ratio (typically 4:2:1 for cereals) ensures vigorous vegetative growth, root development, and pest resistance.\n"
        resp += "\n💡 **Tip:** Combine chemical fertilizers with 5-10 tonnes/hectare of compost to improve soil organic carbon."
        suggs = ["How do I test soil pH?", "What crops suit this soil?", "How much fertilizer per acre?"]
        return resp, suggs

    if intent == "soil_ph":
        ph = ctx.soil_ph if (ctx and ctx.soil_ph is not None) else None
        resp = "🌱 **Soil pH & Soil Health**\n\n"
        if ph is not None:
            resp += f"Your current soil pH is **{ph}**.\n\n"
            if ph < 6.0:
                resp += "• **Acidic Soil (pH < 6.0):** Nutrient availability (P, K, Ca) is reduced. Apply agricultural lime (calcium carbonate) or dolomite at 200-500 kg/acre.\n"
            elif ph > 7.8:
                resp += "• **Alkaline Soil (pH > 7.8):** Micronutrients (Fe, Zn) may be locked. Apply agricultural gypsum or green manure (Dhaincha/Sunnhemp) to reclaim soil.\n"
            else:
                resp += "• **Optimal Neutral Soil (pH 6.0 - 7.5):** Excellent condition! Most crops, including Wheat, Soyabean, and vegetables, thrive in this range.\n"
        else:
            resp += "Ideal soil pH for most Indian crops is between 6.2 and 7.5. Acidic soils require lime, while alkaline soils benefit from gypsum and organic matter."
        suggs = ["How to improve soil moisture?", "What crops tolerate this pH?", "Check NPK nutrients"]
        return resp, suggs

    if intent == "soil_moisture":
        moist = ctx.moisture if (ctx and ctx.moisture is not None) else None
        resp = "💧 **Soil Moisture & Irrigation Advisory**\n\n"
        if moist is not None:
            resp += f"Current soil moisture level: **{moist}%**.\n\n"
            if moist < 30:
                resp += "⚠️ **Low Moisture Alert:** Immediate irrigation recommended. For water efficiency, adopt drip or micro-sprinkler irrigation.\n"
            elif moist > 70:
                resp += "⚠️ **High Moisture:** Avoid over-irrigation. Ensure field drainage channels are clear to prevent root rot and damping off.\n"
            else:
                resp += "✅ **Optimum Moisture:** Soil has good water holding capacity. Maintain mulching with crop residues to conserve water.\n"
        else:
            resp += "Maintain soil moisture at 40-60% during critical growth phases (germination, flowering, grain development). Mulching reduces evaporation by up to 35%."
        suggs = ["What is the weather forecast?", "How does this affect my crop?", "Best irrigation methods"]
        return resp, suggs

    if intent == "weather":
        resp = "☀️ **Weather & Farm Operations Advisory**\n\n"
        if has_weather:
            temp = ctx.temperature if ctx.temperature is not None else "--"
            cond = ctx.weather_condition or "Clear"
            rain = ctx.rainfall if ctx.rainfall is not None else 0
            hum = ctx.humidity if ctx.humidity is not None else "--"
            resp += f"**Current Local Weather:** {temp}°C, {cond} (Humidity: {hum}%, Rainfall: {rain} mm).\n\n"
            if rain and rain > 5:
                resp += "• **Rainfall Notice:** Postpone chemical spraying and fertilizer top-dressing to prevent runoff.\n"
            if isinstance(temp, (int, float)) and temp > 35:
                resp += "• **High Heat Warning:** Provide light evening irrigation to reduce crop heat stress.\n"
            resp += "• **Farming Action:** Schedule harvesting and pesticide application during dry, sunny windows.\n"
        else:
            resp += "Always track local 7-day weather forecasts before sowing, spraying, or harvesting to protect crop yields."
        suggs = ["Will it rain tomorrow?", "Is it safe to spray pesticide?", "How does weather affect mandi prices?"]
        return resp, suggs

    if intent == "msp":
        resp = "⚖️ **Government MSP (Minimum Support Price) Benchmark**\n\n"
        if ctx and ctx.msp_price is not None and ctx.mandi_price is not None:
            diff = round(ctx.mandi_price - ctx.msp_price, 2)
            crop_name = ctx.selected_crop or "Wheat"
            resp += f"• **Crop:** {crop_name}\n• **Government MSP:** ₹{ctx.msp_price:,.2f} / quintal\n• **Current Mandi Price:** ₹{ctx.mandi_price:,.2f} / quintal\n"
            if diff >= 0:
                resp += f"✅ **Trading Above MSP (+₹{diff:,.2f}):** Market conditions are favorable. Consider selling in the open APMC mandi.\n"
            else:
                resp += f"⚠️ **Trading Below MSP (-₹{abs(diff):,.2f}):** Market is depressed. Farmers are advised to sell through government procurement centers (PACS/FCI) at full MSP.\n"
        else:
            resp += "The Government of India notifies MSP for 22 mandated crops (such as Wheat at ₹2,585/quintal for 2026-27). MSP acts as a legal price floor to prevent distress sales."
        suggs = ["Check mandi price forecast", "Which market gives best price?", "MSP for Wheat and Soyabean"]
        return resp, suggs

    if intent == "mandi_price":
        resp = "📈 **Mandi Prices & Marketing Strategy**\n\n"
        if ctx and ctx.mandi_price is not None:
            mkt = ctx.market_name or "Local Mandi"
            resp += f"The latest modal trading price recorded at **{mkt}** is **₹{ctx.mandi_price:,.2f} per quintal**.\n\n"
            resp += "• **Market Timing:** Check price prediction forecasts in the platform to decide whether to sell now or store for next week.\n• **Quality Factor:** Clean, graded produce with moisture < 12% fetches 5-10% higher prices."
        else:
            resp += "Mandi prices fluctuate daily based on arrivals and buyer demand. Use our 'Market Prices' and 'Price Prediction' tools to find the highest-paying APMC mandi near you."
        suggs = ["Compare with MSP floor price", "Predict prices for next 7 days", "Which nearby mandi pays more?"]
        return resp, suggs

    if intent == "pest_disease":
        resp = "🛡️ **Integrated Pest & Disease Management**\n\n"
        resp += "• **Prevention:** Spray 5% Neem Seed Kernel Extract (NSKE) or Neem Oil (1500 ppm at 3-5 ml/L) as an organic deterrent.\n• **Fungal Blight/Rust:** Ensure proper plant spacing and spray copper oxychloride (2.5 g/L) or Mancozeb if spots appear.\n• **Sucking Pests (Aphids/Whiteflies):** Install yellow sticky traps (10-15 traps/acre) to monitor and control pest populations.\n• **Biological Control:** Encourage natural predators like ladybird beetles and Trichogramma cards."
        suggs = ["How to treat yellow leaves?", "Best organic pest spray", "Weather risk for pests"]
        return resp, suggs

    # General fallback
    resp = "🌾 **AgriSmart AI Assistant**\n\nI am here to assist you with every aspect of your farm:\n\n"
    resp += "• **Crop Selection:** Recommended crops based on your soil NPK & climate\n• **Soil Health:** Managing Nitrogen, Phosphorus, Potassium, and pH levels\n• **Weather Insights:** Sowing and irrigation planning based on live weather\n• **Fair Pricing:** Comparing daily mandi prices with Government MSP floors\n\nHow can I help your farm today?"
    suggs = ["What crops should I grow?", "Check soil NPK health", "Compare market price with MSP", "Weather advisory for today"]
    return resp, suggs


def _generate_kn(intent: str, ctx: AssistantContext | None) -> tuple[str, list[str]]:
    has_soil = ctx and (ctx.nitrogen is not None or ctx.soil_ph is not None)
    has_reco = ctx and ctx.recommended_crops

    if intent == "crop_recommendation":
        resp = "🌾 **ಬೆಳೆ ಶಿಫಾರಸು ಸಲಹೆ (Crop Recommendation)**\n\n"
        if has_reco:
            recos = ", ".join(ctx.recommended_crops[:3])
            resp += f"ನಿಮ್ಮ ಜಮೀನಿನ ಮಣ್ಣು ಮತ್ತು ಹವಾಮಾನ ವಿಶ್ಲೇಷಣೆಯ ಪ್ರಕಾರ, ಹೆಚ್ಚು ಸೂಕ್ತವಾದ ಬೆಳೆಗಳು: **{recos}**.\n\n"
        elif has_soil:
            resp += f"ನಿಮ್ಮ ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳು ({ctx.nitrogen or '--'} ಸಾರಜನಕ, {ctx.phosphorus or '--'} ರಂಜಕ, {ctx.potassium or '--'} ಪೊಟ್ಯಾಷ್) ಹಾಗೂ ಪಿಎಚ್ {ctx.soil_ph or '--'} ಪ್ರಕಾರ, ಗೋಧಿ, ಮೆಕ್ಕೆಜೋಳ, ಸೋಯಾಬೀನ್ ಅಥವಾ ಕಡಲೆ ಬೆಳೆಗಳು ಅತ್ಯುತ್ತಮವಾಗಿ ಬೆಳೆಯುತ್ತವೆ.\n\n"
        else:
            resp += "ನಿಮ್ಮ ಹೊಲಕ್ಕೆ ನಿಖರ ಬೆಳೆ ಶಿಫಾರಸು ಪಡೆಯಲು 'ನನ್ನ ಜಮೀನುಗಳು' ವಿಭಾಗದಲ್ಲಿ ಮಣ್ಣಿನ ಪರೀಕ್ಷಾ ವಿವರಗಳನ್ನು (N, P, K, pH, ತೇವಾಂಶ) ನಮೂದಿಸಿ.\n\n"
        resp += "• **ಬಿತ್ತನೆ ಸಲಹೆ:** ಪ್ರಮಾಣೀಕೃತ ಬೀಜಗಳನ್ನು ಬಳಸಿ, ಸರಿಯಾದ ಋತುವಿನಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿ.\n• **ಭೂಮಿ ಸಿದ್ಧತೆ:** ಚೆನ್ನಾಗಿ ಕೊಳೆತ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರವನ್ನು ಬೆರೆಸಿ ಆಳವಾದ ಉಳುಮೆ ಮಾಡಿ.\n• **ಸಾಲುಗಳ ಅಂತರ:** ಉತ್ತಮ ಇಳುವರಿಗಾಗಿ ಶಿಫಾರಸು ಮಾಡಿದ ಅಂತರ ಕಾಪಾಡಿಕೊಳ್ಳಿ."
        suggs = ["ಯಾವ ರಸಗೊಬ್ಬರ ಎಷ್ಟು ಹಾಕಬೇಕು?", "ಈ ಬೆಳೆಗಳ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಎಷ್ಟು?", "ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ ಹೇಗಿದೆ?"]
        return resp, suggs

    if intent == "soil_npk":
        resp = "🧪 **ಮಣ್ಣಿನ ಪೋಷಕಾಂಶಗಳ (NPK) ನಿರ್ವಹಣೆ**\n\n"
        if has_soil:
            n = ctx.nitrogen if ctx.nitrogen is not None else "ಮಾಹಿತಿಯಿಲ್ಲ"
            p = ctx.phosphorus if ctx.phosphorus is not None else "ಮಾಹಿತಿಯಿಲ್ಲ"
            k = ctx.potassium if ctx.potassium is not None else "ಮಾಹಿತಿಯಿಲ್ಲ"
            resp += f"**ನಿಮ್ಮ ಮಣ್ಣಿನ ವಿವರಗಳು:** ಸಾರಜನಕ (N): **{n} kg/ha**, ರಂಜಕ (P): **{p} kg/ha**, ಪೊಟ್ಯಾಷ್ (K): **{k} kg/ha**.\n\n"
            if isinstance(ctx.nitrogen, (int, float)) and ctx.nitrogen < 50:
                resp += "⚠️ **ಸಾರಜನಕ ಕೊರತೆ:** ಯೂರಿಯಾ ಗೊಬ್ಬರವನ್ನು ಬಿತ್ತನೆ ಸಮಯದಲ್ಲಿ ಮತ್ತು ಪೈರು ಬೆಳೆಯುವಾಗ ಎರಡು ಹಂತಗಳಲ್ಲಿ ನೀಡಿ.\n"
            if isinstance(ctx.phosphorus, (int, float)) and ctx.phosphorus < 25:
                resp += "⚠️ **ರಂಜಕದ ಕೊರತೆ:** ಬೇರುಗಳ ಬಲವರ್ಧನೆಗೆ ಡಿಎಪಿ (DAP) ಅಥವಾ ಸಿಂಗಲ್ ಸೂಪರ್ ಫಾಸ್ಫೇಟ್ (SSP) ಗೊಬ್ಬರ ಬಳಸಿ.\n"
            if isinstance(ctx.potassium, (int, float)) and ctx.potassium < 30:
                resp += "⚠️ **ಪೊಟ್ಯಾಷ್ ಕೊರತೆ:** ರೋಗ ನಿರೋಧಕ ಶಕ್ತಿ ಹಾಗೂ ಕಾಳು ತುಂಬಲು ಎಂಒಪಿ (MOP) ಗೊಬ್ಬರ ಹಾಕಿ.\n"
        else:
            resp += "ಧಾನ್ಯ ಬೆಳೆಗಳಿಗೆ ಸಮತೋಲಿತ N:P:K ಅನುಪಾತ (4:2:1) ಅವಶ್ಯಕವಾಗಿದೆ. ರಾಸಾಯನಿಕ ಗೊಬ್ಬರದೊಂದಿಗೆ ಜೈವಿಕ ಗೊಬ್ಬರಗಳನ್ನು ಬಳಸಿ."
        resp += "\n💡 **ಸಲಹೆ:** ಪ್ರತಿ ಎಕರೆಗೆ 5 ಟನ್ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಅಥವಾ ಎರೆಹುಳು ಗೊಬ್ಬರ ಸೇರಿಸುವುದರಿಂದ ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಹೆಚ್ಚುತ್ತದೆ."
        suggs = ["ಮಣ್ಣಿನ ಪಿಎಚ್ (pH) ಪರೀಕ್ಷಿಸುವುದು ಹೇಗೆ?", "ಯಾವ ಬೆಳೆ ಈ ಮಣ್ಣಿಗೆ ಸೂಕ್ತ?", "ತೇವಾಂಶ ನಿರ್ವಹಣೆ ಹೇಗೆ?"]
        return resp, suggs

    if intent == "soil_ph":
        ph = ctx.soil_ph if (ctx and ctx.soil_ph is not None) else None
        resp = "🌱 **ಮಣ್ಣಿನ ಪಿಎಚ್ (pH) ಮತ್ತು ಆರೋಗ್ಯ**\n\n"
        if ph is not None:
            resp += f"ನಿಮ್ಮ ಜಮೀನಿನ ಪ್ರಸ್ತುತ ಮಣ್ಣಿನ ಪಿಎಚ್ ಮಟ್ಟ: **{ph}**.\n\n"
            if ph < 6.0:
                resp += "• **ಆಮ್ಲೀಯ ಮಣ್ಣು (pH < 6.0):** ಕೃಷಿ ಸುಣ್ಣ (Lime) ಅಥವಾ ಡಾಲಮೈಟ್ ಅನ್ನು ಎಕರೆಗೆ 200-400 ಕೆಜಿ ಬೆರೆಸಿ ಆಮ್ಲೀಯತೆ ಕಡಿಮೆ ಮಾಡಿ.\n"
            elif ph > 7.8:
                resp += "• **ಕ್ಷಾರೀಯ ಮಣ್ಣು (pH > 7.8):** ಜಿಪ್ಸಮ್ ಅಥವಾ ಹಸಿರೆಲೆ ಗೊಬ್ಬರ (ಡೈಂಚಾ/ಸೆಣಬು) ಬೆಳೆದು ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ.\n"
            else:
                resp += "• **ಉತ್ತಮ ತಟಸ್ಥ ಮಣ್ಣು (pH 6.0 - 7.5):** ಮಣ್ಣು ಆರೋಗ್ಯಕರವಾಗಿದೆ! ಗೋಧಿ, ಸೋಯಾಬೀನ್, ತರಕಾರಿ ಸೇರಿದಂತೆ ಬಹುತೇಕ ಬೆಳೆಗಳಿಗೆ ಇದು ಸೂಕ್ತ.\n"
        else:
            resp += "ಹೆಚ್ಚಿನ ಬೆಳೆಗಳಿಗೆ ಮಣ್ಣಿನ ಪಿಎಚ್ 6.2 ರಿಂದ 7.5 ರ ನಡುವೆ ಇರಬೇಕು. ಮಣ್ಣಿನ ಆಮ್ಲೀಯತೆ ಸರಿಪಡಿಸಲು ಸುಣ್ಣ ಮತ್ತು ಕ್ಷಾರೀಯತೆಗೆ ಜಿಪ್ಸಮ್ ಬಳಸಿ."
        suggs = ["ತೇವಾಂಶ ಮಟ್ಟ ಪರೀಕ್ಷಿಸಿ", "ಈ ಪಿಎಚ್ ಗೆ ಯಾವ ಬೆಳೆ ಸೂಕ್ತ?", "ಪೋಷಕಾಂಶಗಳ ಕೊರತೆ ಇದೆಯೇ?"]
        return resp, suggs

    if intent == "soil_moisture":
        moist = ctx.moisture if (ctx and ctx.moisture is not None) else None
        resp = "💧 **ಮಣ್ಣಿನ ತೇವಾಂಶ ಮತ್ತು ನೀರಾವರಿ ಸಲಹೆ**\n\n"
        if moist is not None:
            resp += f"ನಿಮ್ಮ ಜಮೀನಿನ ತೇವಾಂಶ: **{moist}%**.\n\n"
            if moist < 30:
                resp += "⚠️ **ಕಡಿಮೆ ತೇವಾಂಶ:** ತಕ್ಷಣ ನೀರಾವರಿ ಅಗತ್ಯವಿದೆ. ನೀರಿನ ಉಳಿತಾಯಕ್ಕಾಗಿ ಹನಿ ನೀರಾವರಿ ಅಥವಾ ತುಂತುರು ನೀರಾವರಿ ಬಳಸಿ.\n"
            elif moist > 70:
                resp += "⚠️ **ಹೆಚ್ಚಿನ ತೇವಾಂಶ:** ನೀರು ನಿಲ್ಲದಂತೆ ಬಸಿಗಾಲುವೆಗಳನ್ನು ಮಾಡಿ. ಇಲ್ಲವಾದರೆ ಬೇರು ಕೊಳೆ ರೋಗ ಬರಬಹುದು.\n"
            else:
                resp += "✅ **ಸರಿಯಾದ ತೇವಾಂಶ:** ಮಣ್ಣಿನಲ್ಲಿ ತೇವಾಂಶ ಸೂಕ್ತವಾಗಿದೆ. ತೇವಾಂಶ ಕಾಪಾಡಲು ಹೊದಿಕೆ (ಮಲ್ಚಿಂಗ್) ಮಾಡಿ.\n"
        else:
            resp += "ಹೂ ಬಿಡುವ ಮತ್ತು ಕಾಳು ಕಟ್ಟುವ ಹಂತದಲ್ಲಿ ಮಣ್ಣಿನಲ್ಲಿ 50% ತೇವಾಂಶ ಇರುವುದು ಬಹಳ ಮುಖ್ಯ."
        suggs = ["ಇಂದಿನ ಹವಾಮಾನ ಹೇಗಿದೆ?", "ಯಾವ ನೀರಾವರಿ ಪದ್ಧತಿ ಉತ್ತಮ?", "ಬೆಳೆ ರಕ್ಷಣೆ ಹೇಗೆ?"]
        return resp, suggs

    if intent == "weather":
        resp = "☀️ **ಹವಾಮಾನ ಮತ್ತು ಕೃಷಿ ಕಾರ್ಯಗಳ ಸಲಹೆ**\n\n"
        if ctx and ctx.temperature is not None:
            temp = ctx.temperature
            cond = ctx.weather_condition or "ಸ್ವಚ್ಛ ಆಕಾಶ"
            rain = ctx.rainfall or 0
            hum = ctx.humidity or "--"
            resp += f"**ಪ್ರಸ್ತುತ ಹವಾಮಾನ:** ತಾಪಮಾನ: {temp}°C, ಸ್ಥಿತಿ: {cond}, ಗಾಳಿಯ ತೇವಾಂಶ: {hum}%, ಮಳೆ: {rain} mm.\n\n"
            if rain and rain > 5:
                resp += "• **ಮಳೆಯ ಮುನ್ಸೂಚನೆ:** ಕೀಟನಾಶಕ ಸಿಂಪಡಣೆ ಮತ್ತು ಗೊಬ್ಬರ ಹಾಕುವುದನ್ನು ಮುಂದೂಡಿ.\n"
            if isinstance(temp, (int, float)) and temp > 35:
                resp += "• **ಹೆಚ್ಚಿನ ಬಿಸಿಲು:** ಸಂಜೆ ವೇಳೆಯಲ್ಲಿ ಲಘು ನೀರಾವರಿ ಮಾಡಿ ಬೆಳೆ ಒಣಗದಂತೆ ನೋಡಿಕೊಳ್ಳಿ.\n"
        else:
            resp += "ಬಿತ್ತನೆ, ಕಟಾವು ಮತ್ತು ಕೀಟನಾಶಕ ಸಿಂಪಡಣೆಗೆ ಮುನ್ನ 7 ದಿನಗಳ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ ಗಮನಿಸಿ."
        suggs = ["ನಾಳೆ ಮಳೆ ಬರುತ್ತದೆಯೇ?", "ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸಬಹುದೇ?", "ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಎಷ್ಟಿದೆ?"]
        return resp, suggs

    if intent == "msp":
        resp = "⚖️ **ಸರ್ಕಾರದ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ (MSP) ಮಾಹಿತಿ**\n\n"
        if ctx and ctx.msp_price is not None and ctx.mandi_price is not None:
            diff = round(ctx.mandi_price - ctx.msp_price, 2)
            crop_name = ctx.selected_crop or "ಗೋಧಿ"
            resp += f"• **ಬೆಳೆ:** {crop_name}\n• **ಸರ್ಕಾರಿ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ (MSP):** ₹{ctx.msp_price:,.2f} / ಕ್ವಿಂಟಾಲ್\n• **ಪ್ರಸ್ತುತ ಮಂಡಿ ಬೆಲೆ:** ₹{ctx.mandi_price:,.2f} / ಕ್ವಿಂಟಾಲ್\n\n"
            if diff >= 0:
                resp += f"✅ **ಬೆಂಬಲ ಬೆಲೆಗಿಂತ ಹೆಚ್ಚು (+₹{diff:,.2f}):** ಮಾರುಕಟ್ಟೆ ಸ್ಥಿತಿ ಉತ್ತಮವಾಗಿದೆ. ಮಂಡಿಯಲ್ಲಿ ಮಾರಾಟ ಮಾಡುವುದು ಲಾಭದಾಯಕ.\n"
            else:
                resp += f"⚠️ **ಬೆಂಬಲ ಬೆಲೆಗಿಂತ ಕಡಿಮೆ (-₹{abs(diff):,.2f}):** ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಬೆಲೆ ಕಡಿಮೆಯಿದೆ. ಸರ್ಕಾರಿ ಖರೀದಿ ಕೇಂದ್ರಗಳಲ್ಲಿ (MSP ದರದಲ್ಲಿ) ಮಾರಾಟ ಮಾಡಿ ನಷ್ಟ ತಪ್ಪಿಸಿ.\n"
        else:
            resp += "ಭಾರತ ಸರ್ಕಾರವು ಪ್ರಮುಖ ಬೆಳೆಗಳಿಗೆ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ (MSP) ನಿಗದಿಪಡಿಸಿದೆ (ಉದಾ: ಗೋಧಿಗೆ ಕ್ವಿಂಟಾಲ್‌ಗೆ ₹2,585). ಇದು ರೈತರಿಗೆ ಕನಿಷ್ಠ ಖಚಿತ ಆದಾಯ ಒದಗಿಸುತ್ತದೆ."
        suggs = ["ಮುಂಬರುವ ದಿನಗಳ ಬೆಲೆ ಮುನ್ಸೂಚನೆ", "ಯಾವ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಹೆಚ್ಚು ಬೆಲೆ ಇದೆ?", "ಗೋಧಿ ಮತ್ತು ಸೋಯಾಬೀನ್ MSP"]
        return resp, suggs

    if intent == "mandi_price":
        resp = "📈 **ಮಂಡಿ ಬೆಲೆಗಳು ಮತ್ತು ಮಾರಾಟ ತಂತ್ರ**\n\n"
        if ctx and ctx.mandi_price is not None:
            mkt = ctx.market_name or "ಸ್ಥಳೀಯ ಮಂಡಿ"
            resp += f"**{mkt}** ಮಂಡಿಯಲ್ಲಿ ಇತ್ತೀಚಿನ ಮಾದರಿ ಬೆಲೆ: **₹{ctx.mandi_price:,.2f} ಪ್ರತಿ ಕ್ವಿಂಟಾಲ್‌ಗೆ**.\n\n"
            resp += "• ಬೆಳೆ ಮಾರಾಟಕ್ಕೆ ಮುನ್ನ 7 ದಿನಗಳ ಬೆಲೆ ಮುನ್ಸೂಚನೆ ಗಮನಿಸಿ.\n• ಧಾನ್ಯಗಳನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸಿ ತೇವಾಂಶ 12% ಕ್ಕಿಂತ ಕಡಿಮೆ ಇಟ್ಟರೆ ಶೇ. 5-10 ರಷ್ಟು ಹೆಚ್ಚಿನ ಬೆಲೆ ಸಿಗುತ್ತದೆ."
        else:
            resp += "ನಮ್ಮ 'ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಳು' ಮತ್ತು 'ಬೆಲೆ ಮುನ್ಸೂಚನೆ' ಟೂಲ್ ಬಳಸಿ ನಿಮ್ಮ ಸಮೀಪದ ಮಂಡಿಗಳ ಇಂದಿನ ದರಗಳನ್ನು ತಿಳಿದುಕೊಳ್ಳಿ."
        suggs = ["ಬೆಂಬಲ ಬೆಲೆಯೊಂದಿಗೆ ಹೋಲಿಸಿ", "ಮುಂದಿನ 7 ದಿನಗಳ ಬೆಲೆ ಅಂದಾಜು", "ಹೆಚ್ಚು ಬೆಲೆ ಕೊಡುವ ಮಂಡಿ ಯಾವುದು?"]
        return resp, suggs

    if intent == "pest_disease":
        resp = "🛡️ **ಸಮಗ್ರ ಕೀಟ ಮತ್ತು ರೋಗ ನಿರ್ವಹಣೆ**\n\n"
        resp += "• **ಮುನ್ನೆಚ್ಚರಿಕೆ:** ಶೇ. 5 ರ ಬೇವಿನ ಬೀಜದ ಕಷಾಯ (NSKE) ಅಥವಾ ಬೇವಿನ ಎಣ್ಣೆಯನ್ನು (3-5 ಮಿಲಿ/ಲೀಟರ್ ನೀರಿಗೆ) ಸಿಂಪಡಿಸಿ.\n• **ಶಿಲೀಂಧ್ರ ರೋಗಗಳು:** ತಾಮ್ರದ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ (2.5 ಗ್ರಾಂ/ಲೀಟರ್) ಅಥವಾ ಮ್ಯಾಂಕೋಜೆಬ್ ಬಳಸಿ.\n• **ರಸಹೀರುವ ಕೀಟಗಳು (ಹೇನು, ನುಸಿ):** ಎಕರೆಗೆ 10-15 ಹಳದಿ ಬಲೆಗಳನ್ನು ಅಳವಡಿಸಿ ಕೀಟಗಳನ್ನು ನಿಯಂತ್ರಿಸಿ.\n• **ಜೈವಿಕ ನಿಯಂತ್ರಣ:** ಟ್ರೈಕೋಡರ್ಮಾ ಬಳಸಿ ಬೀಜೋಪಚಾರ ಮಾಡಿ."
        suggs = ["ಎಲೆ ಹಳದಿಯಾಗಲು ಕಾರಣವೇನು?", "ನೈಸರ್ಗಿಕ ಕೀಟನಾಶಕ ತಯಾರಿಸುವುದು ಹೇಗೆ?", "ಹವಾಮಾನದಿಂದ ಬರುವ ರೋಗಗಳು"]
        return resp, suggs

    # Default Kannada
    resp = "🌾 **ಅಗ್ರಿಸ್ಮಾರ್ಟ್ ಕೃಷಿ AI ಸಹಾಯಕ (AgriSmart AI Assistant)**\n\nನಮಸ್ಕಾರ! ನಿಮ್ಮ ಕೃಷಿ ಸಂಬಂಧಿತ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಲು ನಾನು ಇಲ್ಲಿದ್ದೇನೆ:\n\n"
    resp += "• **ಬೆಳೆ ಶಿಫಾರಸು:** ನಿಮ್ಮ ಮಣ್ಣು ಮತ್ತು ಹವಾಮಾನಕ್ಕೆ ಸೂಕ್ತ ಬೆಳೆಗಳು\n• **ಮಣ್ಣಿನ ಆರೋಗ್ಯ:** ಸಾರಜನಕ, ರಂಜಕ, ಪೊಟ್ಯಾಷ್ (NPK) ಮತ್ತು ಪಿಎಚ್ ನಿರ್ವಹಣೆ\n• **ಹವಾಮಾನ ಮಾಹಿತಿ:** ಬಿತ್ತನೆ ಮತ್ತು ನೀರಾವರಿ ಮುನ್ಸೂಚನೆ\n• **ನ್ಯಾಯಯುತ ಬೆಲೆ:** ಮಂಡಿ ದರ ಮತ್ತು ಸರ್ಕಾರದ ಕನಿಷ್ಠ ಬೆಂಬಲ ಬೆಲೆ (MSP) ಹೋಲಿಕೆ\n\nಇಂದು ನಿಮ್ಮ ಹೊಲದ ಬಗ್ಗೆ ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?"
    suggs = ["ನನ್ನ ಮಣ್ಣಿಗೆ ಯಾವ ಬೆಳೆ ಸೂಕ್ತ?", "ರಸಗೊಬ್ಬರ ಪ್ರಮಾಣ ತಿಳಿಸಿ", "ಇಂದಿನ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಮತ್ತು MSP", "ಹವಾಮಾನ ಸಲಹೆ"]
    return resp, suggs


def _generate_hi(intent: str, ctx: AssistantContext | None) -> tuple[str, list[str]]:
    has_soil = ctx and (ctx.nitrogen is not None or ctx.soil_ph is not None)
    has_reco = ctx and ctx.recommended_crops

    if intent == "crop_recommendation":
        resp = "🌾 **फसल सिफारिश सलाह (Crop Recommendation)**\n\n"
        if has_reco:
            recos = ", ".join(ctx.recommended_crops[:3])
            resp += f"आपके खेत की मिट्टी और स्थानीय मौसम के अनुसार शीर्ष अनुशंसित फसलें हैं: **{recos}**।\n\n"
        elif has_soil:
            resp += f"आपकी मिट्टी के पोषक तत्वों ({ctx.nitrogen or '--'} N, {ctx.phosphorus or '--'} P, {ctx.potassium or '--'} K) और pH {ctx.soil_ph or '--'} के अनुसार गेहूं, मक्का, सोयाबीन या चना की बुवाई अत्यधिक लाभकारी रहेगी।\n\n"
        else:
            resp += "सटीक फसल सिफारिश के लिए 'मेरे खेत' सेक्शन में अपनी मिट्टी की जांच रिपोर्ट (NPK, pH और नमी) अवश्य दर्ज करें।\n\n"
        resp += "• **बुवाई सलाह:** प्रमाणित बीजों का चयन करें और सही मौसम में बुवाई करें।\n• **खेत की तैयारी:** गहरी जुताई करें और 5-10 टन गोबर की सड़ी खाद मिलाएं।\n• **कतार दूरी:** बेहतर पैदावार के लिए अनुशंसित कतार दूरी बनाए रखें।"
        suggs = ["खाद की मात्रा कितनी डालनी चाहिए?", "इन फसलों का मंडी भाव क्या है?", "मौसम का फसल पर क्या प्रभाव पड़ेगा?"]
        return resp, suggs

    if intent == "soil_npk":
        resp = "🧪 **मृदा पोषक तत्व (NPK) प्रबंधन**\n\n"
        if has_soil:
            n = ctx.nitrogen if ctx.nitrogen is not None else "उपलब्ध नहीं"
            p = ctx.phosphorus if ctx.phosphorus is not None else "उपलब्ध नहीं"
            k = ctx.potassium if ctx.potassium is not None else "उपलब्ध नहीं"
            resp += f"**आपके खेत के आंकड़े:** नाइट्रोजन (N): **{n} kg/ha**, फास्फोरस (P): **{p} kg/ha**, पोटाश (K): **{k} kg/ha**।\n\n"
            if isinstance(ctx.nitrogen, (int, float)) and ctx.nitrogen < 50:
                resp += "⚠️ **नाइट्रोजन की कमी:** यूरिया को बुवाई और कल्ले फूटते समय दो से तीन भागों में बांटकर दें।\n"
            if isinstance(ctx.phosphorus, (int, float)) and ctx.phosphorus < 25:
                resp += "⚠️ **फास्फोरस की कमी:** जड़ों के विकास के लिए बुवाई के समय डीएपी (DAP) या सिंगल सुपर फास्फेट (SSP) डालें।\n"
            if isinstance(ctx.potassium, (int, float)) and ctx.potassium < 30:
                resp += "⚠️ **पोटाश की कमी:** दानों के भराव और रोग प्रतिरोधक क्षमता बढ़ाने के लिए एमओपी (MOP) डालें।\n"
        else:
            resp += "अनाज वाली फसलों के लिए संतुलित 4:2:1 (N:P:K) अनुपात सर्वोत्तम है। रासायनिक उर्वरकों के साथ जैविक खाद का प्रयोग करें।"
        resp += "\n💡 **सुझाव:** प्रति एकड़ 5 टन वर्मीकम्पोस्ट या गोबर की खाद मिट्टी में मिलाने से जैविक कार्बन बढ़ता है।"
        suggs = ["मिट्टी का pH कैसे सुधारें?", "इस मिट्टी के लिए कौन सी फसल सही है?", "सिंचाई कब करें?"]
        return resp, suggs

    if intent == "soil_ph":
        ph = ctx.soil_ph if (ctx and ctx.soil_ph is not None) else None
        resp = "🌱 **मिट्टी का pH एवं मृदा स्वास्थ्य**\n\n"
        if ph is not None:
            resp += f"आपके खेत की मिट्टी का वर्तमान pH स्तर: **{ph}**।\n\n"
            if ph < 6.0:
                resp += "• **अम्लीय मिट्टी (pH < 6.0):** कृषि चूना (Lime) 200-400 किग्रा प्रति एकड़ मिलाकर अम्लता कम करें।\n"
            elif ph > 7.8:
                resp += "• **क्षारीय मिट्टी (pH > 7.8):** जिप्सम या हरी खाद (ढैंचा/सनई) का प्रयोग करें।\n"
            else:
                resp += "• **आदर्श उदासीन मिट्टी (pH 6.0 - 7.5):** आपकी मिट्टी बहुत अच्छी स्थिति में है! गेहूं, सोयाबीन और सब्जियां खूब पनपेंगी।\n"
        else:
            resp += "फसलों के लिए 6.2 से 7.5 के बीच का pH सर्वोत्तम होता है। अम्लीय मिट्टी में चूना और क्षारीय में जिप्सम डालें।"
        suggs = ["मिट्टी की नमी कैसे जांचें?", "इस pH में कौन सी फसल उगाएं?", "उर्वरक की सही मात्रा"]
        return resp, suggs

    if intent == "soil_moisture":
        moist = ctx.moisture if (ctx and ctx.moisture is not None) else None
        resp = "💧 **मृदा नमी एवं सिंचाई सलाह**\n\n"
        if moist is not None:
            resp += f"आपके खेत में वर्तमान नमी: **{moist}%**।\n\n"
            if moist < 30:
                resp += "⚠️ **कम नमी की चेतावनी:** तत्काल सिंचाई की आवश्यकता है। पानी की बचत के लिए ड्रिप या फव्वारा सिंचाई अपनाएं।\n"
            elif moist > 70:
                resp += "⚠️ **अधिक नमी:** खेत से पानी की निकासी सुनिश्चित करें ताकि जड़ गलन रोग न फैले।\n"
            else:
                resp += "✅ **संतुलित नमी:** नमी का स्तर अच्छा है। नमी बनाए रखने के लिए पुआल की मल्चिंग करें।\n"
        else:
            resp += "फूल आने और दाना भरते समय खेत में 50% नमी अनिवार्य है। मल्चिंग से 30% पानी की बचत होती है।"
        suggs = ["आज का मौसम कैसा रहेगा?", "ड्रिप सिंचाई के फायदे", "रोग नियंत्रण के उपाय"]
        return resp, suggs

    if intent == "weather":
        resp = "☀️ **मौसम एवं कृषि कार्य सलाह**\n\n"
        if ctx and ctx.temperature is not None:
            temp = ctx.temperature
            cond = ctx.weather_condition or "साफ मौसम"
            rain = ctx.rainfall or 0
            hum = ctx.humidity or "--"
            resp += f"**वर्तमान मौसम:** तापमान: {temp}°C, स्थिति: {cond}, नमी: {hum}%, वर्षा: {rain} मिमी।\n\n"
            if rain and rain > 5:
                resp += "• **बारिश की चेतावनी:** कीटनाशक छिड़काव और यूरिया का बुरकाव रोक दें।\n"
            if isinstance(temp, (int, float)) and temp > 35:
                resp += "• **तेज धूप/गर्मी:** शाम के समय हल्की सिंचाई करें ताकि फसल झुलसे नहीं।\n"
        else:
            resp += "बुवाई, निराई और कीटनाशक छिड़काव से पहले 7 दिनों का मौसम पूर्वानुमान अवश्य देखें।"
        suggs = ["क्या कल बारिश होगी?", "कीटनाशक छिड़कने का सही समय", "मंडी भाव क्या चल रहा है?"]
        return resp, suggs

    if intent == "msp":
        resp = "⚖️ **सरकारी न्यूनतम समर्थन मूल्य (MSP) विश्लेषण**\n\n"
        if ctx and ctx.msp_price is not None and ctx.mandi_price is not None:
            diff = round(ctx.mandi_price - ctx.msp_price, 2)
            crop_name = ctx.selected_crop or "गेहूं"
            resp += f"• **फसल:** {crop_name}\n• **सरकारी MSP:** ₹{ctx.msp_price:,.2f} / क्विंटल\n• **वर्तमान मंडी भाव:** ₹{ctx.mandi_price:,.2f} / क्विंटल\n\n"
            if diff >= 0:
                resp += f"✅ **MSP से अधिक (+₹{diff:,.2f}):** बाजार भाव बहुत अच्छे हैं। खुली मंडी में उपज बेचना फायदेमंद है।\n"
            else:
                resp += f"⚠️ **MSP से कम (-₹{abs(diff):,.2f}):** मंडी में भाव कम हैं। किसान सरकारी खरीद केंद्रों (पैक्स/एफसीआई) पर समर्थन मूल्य पर ही बेचें।\n"
        else:
            resp += "भारत सरकार 22 अनिवार्य फसलों के लिए MSP घोषित करती है (जैसे गेहूं के लिए ₹2,585/क्विंटल वर्ष 2026-27)। MSP किसानों के लिए न्यूनतम मूल्य सुरक्षा कवच है।"
        suggs = ["मंडी भाव का पूर्वानुमान", "कौन सी मंडी में ज्यादा दाम मिलेगा?", "गेहूं और सोयाबीन का समर्थन मूल्य"]
        return resp, suggs

    if intent == "mandi_price":
        resp = "📈 **मंडी भाव एवं उपज विपणन रणनीति**\n\n"
        if ctx and ctx.mandi_price is not None:
            mkt = ctx.market_name or "स्थानीय मंडी"
            resp += f"**{mkt}** में ताजा मॉडल भाव: **₹{ctx.mandi_price:,.2f} प्रति क्विंटल**।\n\n"
            resp += "• बेचने से पहले 7 दिनों का मूल्य पूर्वानुमान चार्ट देखें।\n• साफ, छनी हुई और 12% से कम नमी वाली उपज पर 5-10% अधिक दाम मिलता है।"
        else:
            resp += "मंडी भाव प्रतिदिन आवक के अनुसार बदलते हैं। हमारे 'मंडी भाव' और 'मूल्य पूर्वानुमान' टूल से सही समय पर उपज बेचें।"
        suggs = ["सरकारी MSP से तुलना करें", "अगले 7 दिनों का भाव पूर्वानुमान", "पास की मंडियों के भाव"]
        return resp, suggs

    if intent == "pest_disease":
        resp = "🛡️ **एकीकृत कीट एवं रोग प्रबंधन**\n\n"
        resp += "• **रोकथाम:** 5% नीम बीज अर्क (NSKE) या नीम का तेल (3-5 मिली/लीटर पानी) का छिड़काव करें।\n• **फफूंद रोग (झुलसा/रतुआ):** कॉपर ऑक्सीक्लोराइड (2.5 ग्राम/लीटर) या मैंकोजेब का छिड़काव करें।\n• **रस चूसक कीट (माहू/सफेद मक्खी):** प्रति एकड़ 10-15 पीले चिपचिपे ट्रैप (Yellow Sticky Traps) लगाएं।\n• **जैविक नियंत्रण:** ट्राइकोडर्मा से बीज उपचारित करके ही बोएं।"
        suggs = ["पत्ते पीले पड़ने का कारण क्या है?", "जैविक कीटनाशक कैसे बनाएं?", "मौसम से फैलने वाले रोग"]
        return resp, suggs

    # Default Hindi
    resp = "🌾 **एग्रीस्मार्ट किसान AI सहायक (AgriSmart AI Assistant)**\n\nनमस्ते किसान साथी! मैं आपके कृषि कार्यों में सहायता के लिए उपस्थित हूँ:\n\n"
    resp += "• **फसल चयन:** मिट्टी के NPK और मौसम अनुसार सर्वश्रेष्ठ फसलें\n• **मृदा स्वास्थ्य:** नाइट्रोजन, फास्फोरस, पोटाश और pH सुधार\n• **मौसम पूर्वानुमान:** बुवाई और सिंचाई की सही योजना\n• **उचित मूल्य:** दैनिक मंडी भाव और सरकारी MSP की तुलना\n\nआज मैं आपके खेत के लिए क्या सहायता करूँ?"
    suggs = ["मेरे खेत के लिए कौन सी फसल सही है?", "खाद की सही मात्रा बताएं", "मंडी भाव और MSP की तुलना", "आज का मौसम परामर्श"]
    return resp, suggs


def _generate_te(intent: str, ctx: AssistantContext | None) -> tuple[str, list[str]]:
    has_soil = ctx and (ctx.nitrogen is not None or ctx.soil_ph is not None)
    has_reco = ctx and ctx.recommended_crops

    if intent == "crop_recommendation":
        resp = "🌾 **పంట సిఫార్సు సలహా (Crop Recommendation)**\n\n"
        if has_reco:
            recos = ", ".join(ctx.recommended_crops[:3])
            resp += f"మీ నేల మరియు వాతావరణ విశ్లేషణ ప్రకారం అనుకూలమైన పంటలు: **{recos}**.\n\n"
        elif has_soil:
            resp += f"మీ నేల NPK ({ctx.nitrogen or '--'} N, {ctx.phosphorus or '--'} P, {ctx.potassium or '--'} K) మరియు pH {ctx.soil_ph or '--'} ప్రకారం గోధుమ, మొక్కజొన్న, సోయాబీన్ లేదా శనగ పంటలు మంచి దిగుబడిని ఇస్తాయి.\n\n"
        else:
            resp += "ఖచ్చితమైన పంట సలహా కోసం 'నా పొలాలు' విభాగంలో నేల వివరాలను నమోదు చేయండి.\n\n"
        resp += "• **విత్తన సలహా:** ధృవీకరించిన విత్తనాలను వాడండి.\n• **నేల తయారీ:** బాగా చివికిన పశువుల ఎరువుతో లోతు దుక్కులు చేయండి.\n• **సాళ్ళ దూరం:** సరైన దూరం పాటించి అధిక దిగుబడి సాధించండి."
        suggs = ["ఎరువుల మోతాదు ఎంత ఉండాలి?", "ఈ పంటల మార్కెట్ ధర ఎంత?", "వాతావరణ సూచన ఎలా ఉంది?"]
        return resp, suggs

    if intent == "soil_npk":
        resp = "🧪 **నేల పోషకాల (NPK) యాజమాన్యం**\n\n"
        if has_soil:
            n = ctx.nitrogen if ctx.nitrogen is not None else "--"
            p = ctx.phosphorus if ctx.phosphorus is not None else "--"
            k = ctx.potassium if ctx.potassium is not None else "--"
            resp += f"**మీ పొలం పోషకాలు:** నత్రజని (N): **{n} kg/ha**, భాస్వరం (P): **{p} kg/ha**, పొటాషియం (K): **{k} kg/ha**.\n\n"
            if isinstance(ctx.nitrogen, (int, float)) and ctx.nitrogen < 50:
                resp += "⚠️ **నత్రజని లోపం:** యూరియాను విడతల వారీగా అందించండి.\n"
            if isinstance(ctx.phosphorus, (int, float)) and ctx.phosphorus < 25:
                resp += "⚠️ **భాస్వరం లోపం:** వేర్ల పెరుగుదలకు డీఏపీ (DAP) లేదా ఎస్ఎస్‌పీ (SSP) ఎరువులు వేయండి.\n"
            if isinstance(ctx.potassium, (int, float)) and ctx.potassium < 30:
                resp += "⚠️ **పొటాషియం లోపం:** గింజ నాణ్యతకు మ్యూరేట్ ఆఫ్ పొటాష్ (MOP) వాడండి.\n"
        else:
            resp += "సమతుల్య N:P:K పోషకాలు మరియు సేంద్రీయ ఎరువులు నేల సారాన్ని పెంచుతాయి."
        suggs = ["నేల pH ఎలా మార్చాలి?", "ఏ పంటలు అనుకూలం?", "సిరిధాన్యాల సాగు వివరాలు"]
        return resp, suggs

    if intent == "msp":
        resp = "⚖️ **ప్రభుత్వ కనీస మద్దతు ధర (MSP) సమాచారం**\n\n"
        if ctx and ctx.msp_price is not None and ctx.mandi_price is not None:
            diff = round(ctx.mandi_price - ctx.msp_price, 2)
            resp += f"• **కనీస మద్దతు ధర (MSP):** ₹{ctx.msp_price:,.2f} / క్వింటాల్\n• **ప్రస్తుత మార్కెట్ ధర:** ₹{ctx.mandi_price:,.2f} / క్వింటాల్\n\n"
            if diff >= 0:
                resp += f"✅ **MSP కంటే ఎక్కువ (+₹{diff:,.2f}):** బహిరంగ మార్కెట్లో ధరలు బాగున్నాయి.\n"
            else:
                resp += f"⚠️ **MSP కంటే తక్కువ (-₹{abs(diff):,.2f}):** ప్రభుత్వ కొనుగోలు కేంద్రాల్లో మద్దతు ధరకు అమ్ముకోండి.\n"
        else:
            resp += "రైతులకు గిట్టుబాటు ధర కల్పించడానికి ప్రభుత్వం MSP ని నిర్ణయిస్తుంది."
        suggs = ["మార్కెట్ ధరల అంచనా", "సమీప మండి వివరాలు", "గోధుమ మద్దతు ధర"]
        return resp, suggs

    # Default Telugu
    resp = "🌾 **అగ్రిస్మార్ట్ AI సహాయకుడు (AgriSmart AI Assistant)**\n\nనమస్కారం రైతు సోదరా! మీ వ్యవసాయ సందేహాలను నివృత్తి చేయడానికి నేను సిద్ధంగా ఉన్నాను:\n\n"
    resp += "• **పంట సిఫార్సు:** మీ నేల పోషకాలు మరియు వాతావరణానికి తగిన పంటలు\n• **నేల ఆరోగ్యం:** NPK ఎరువుల సమతుల్యత మరియు pH యాజమాన్యం\n• **వాతావరణం:** వర్షం మరియు ఉష్ణోగ్రత ఆధారిత సలహాలు\n• **మార్కెట్ ధరలు:** మండి రేట్లు మరియు కనీస మద్దతు ధర (MSP) పోలిక\n\nఈరోజు మీ వ్యవసాయానికి ఏ విధంగా సహాయపడగలను?"
    suggs = ["నా నేలకు ఏ పంట మంచిది?", "ఎరువుల సరైన మోతాదు", "నేటి మార్కెట్ ధర మరియు MSP", "వాతావరణ సలహా"]
    return resp, suggs


def _generate_ta(intent: str, ctx: AssistantContext | None) -> tuple[str, list[str]]:
    has_soil = ctx and (ctx.nitrogen is not None or ctx.soil_ph is not None)
    has_reco = ctx and ctx.recommended_crops

    if intent == "crop_recommendation":
        resp = "🌾 **பயிர் பரிந்துரை ஆலோசனை (Crop Recommendation)**\n\n"
        if has_reco:
            recos = ", ".join(ctx.recommended_crops[:3])
            resp += f"உங்கள் நிலத்தின் மண் மற்றும் வானிலை அடிப்படையில் பரிந்துரைக்கப்படும் பயிர்கள்: **{recos}**.\n\n"
        elif has_soil:
            resp += f"உங்கள் மண்ணின் NPK ({ctx.nitrogen or '--'} N, {ctx.phosphorus or '--'} P, {ctx.potassium or '--'} K) மற்றும் pH {ctx.soil_ph or '--'} அளவுக்கு கோதுமை, மக்காச்சோளம், சோயாபீன்ஸ் ஆகியவை சிறந்தவை.\n\n"
        else:
            resp += "துல்லியமான பயிர் பரிந்துரைக்கு 'என் பண்ணைகள்' பக்கத்தில் மண் பரிசோதனை விவரங்களை உள்ளிடவும்.\n\n"
        resp += "• **விதைப்பு முறை:** தரமான சான்றளிக்கப்பட்ட விதைகளைப் பயன்படுத்தவும்.\n• **நில தயாரிப்பு:** நன்கு மக்கிய தொழுவுரமிட்டு ஆழமாக உழவு செய்யவும்."
        suggs = ["எந்த உரம் எவ்வளவு இட வேண்டும்?", "சந்தை விலை நிலவரம் என்ன?", "வானிலை முன்னறிவிப்பு என்ன?"]
        return resp, suggs

    if intent == "soil_npk":
        resp = "🧪 **மண் ஊட்டச்சத்து (NPK) மேலாண்மை**\n\n"
        if has_soil:
            resp += f"**உங்கள் மண் அளவுகள்:** நைட்ரஜன்: **{ctx.nitrogen or '--'} kg/ha**, பாஸ்பரஸ்: **{ctx.phosphorus or '--'} kg/ha**, பொட்டாஷ்: **{ctx.potassium or '--'} kg/ha**.\n\n"
            if isinstance(ctx.nitrogen, (int, float)) and ctx.nitrogen < 50:
                resp += "⚠️ **நைட்ரஜன் குறைபாடு:** யூரியாவை பிரித்து இடவும்.\n"
            if isinstance(ctx.phosphorus, (int, float)) and ctx.phosphorus < 25:
                resp += "⚠️ **பாஸ்பரஸ் குறைபாடு:** டிஏபி (DAP) அல்லது சூப்பர் பாஸ்பேட் இடவும்.\n"
            if isinstance(ctx.potassium, (int, float)) and ctx.potassium < 30:
                resp += "⚠️ **பொட்டாஷ் குறைபாடு:** மணிச்சத்து மற்றும் தானிய வளர்ச்சிக்கு பொட்டாஷ் (MOP) உரம் இடவும்.\n"
        else:
            resp += "சமச்சீர் NPK உரமிடுதல் மற்றும் இயற்கை எரு மண்ணின் வளத்தை உயர்த்தும்."
        suggs = ["மண் pH சீரமைப்பது எப்படி?", "மண் ஈரப்பத மேலாண்மை", "இயற்கை உரம் தயாரிப்பு"]
        return resp, suggs

    if intent == "msp":
        resp = "⚖️ **அரசு குறைந்தபட்ச ஆதரவு விலை (MSP)**\n\n"
        if ctx and ctx.msp_price is not None and ctx.mandi_price is not None:
            diff = round(ctx.mandi_price - ctx.msp_price, 2)
            resp += f"• **குறைந்தபட்ச ஆதரவு விலை (MSP):** ₹{ctx.msp_price:,.2f} / குவிண்டால்\n• **தற்போதைய மண்டி விலை:** ₹{ctx.mandi_price:,.2f} / குவிண்டால்\n\n"
            if diff >= 0:
                resp += f"✅ **MSP விலையை விட அதிகம் (+₹{diff:,.2f}):** சந்தையில் நல்ல விலை கிடைக்கிறது.\n"
            else:
                resp += f"⚠️ **MSP விலையை விட குறைவு (-₹{abs(diff):,.2f}):** நஷ்டத்தை தவிர்க்க அரசு கொள்முதல் மையங்களில் விற்கவும்.\n"
        else:
            resp += "விவசாயிகளுக்கு நியாயமான வருமானம் கிடைக்க அரசு MSP விலையை நிர்ணயிக்கிறது."
        suggs = ["சந்தை விலை முன்னறிவிப்பு", "அருகிலுள்ள ஒழுங்குமுறை விற்பனைக்கூடம்", "கோதுமை ஆதரவு விலை"]
        return resp, suggs

    # Default Tamil
    resp = "🌾 **அக்ரிஸ்மார்ட் AI உதவியாளர் (AgriSmart AI Assistant)**\n\nவணக்கம் விவசாய தோழரே! உங்கள் விவசாய முன்னேற்றத்திற்கு நான் உதவ தயாராக உள்ளேன்:\n\n"
    resp += "• **பயிர் பரிந்துரை:** உங்கள் மண் மற்றும் காலநிலைக்கு ஏற்ற சிறந்த பயிர்கள்\n• **மண் வளம்:** நைட்ரஜன், பாஸ்பரஸ், பொட்டாஷ் (NPK) மற்றும் pH மேலாண்மை\n• **வானிலை அறிவுரை:** விதைப்பு மற்றும் பாசனத்திற்கான வானிலை தகவல்\n• **சந்தை விலை:** மண்டி விலைகள் மற்றும் அரசு ஆதரவு விலை (MSP) ஒப்பீடு\n\nஇன்று உங்கள் பண்ணைக்கு எவ்வாறு உதவ வேண்டும்?"
    suggs = ["என் மண்ணிற்கு எந்த பயிர் ஏற்றது?", "உர அளவு விவரங்கள்", "இன்றைய சந்தை விலை மற்றும் MSP", "வானிலை ஆலோசனை"]
    return resp, suggs


def _generate_ml(intent: str, ctx: AssistantContext | None) -> tuple[str, list[str]]:
    has_soil = ctx and (ctx.nitrogen is not None or ctx.soil_ph is not None)
    has_reco = ctx and ctx.recommended_crops

    if intent == "crop_recommendation":
        resp = "🌾 **വിള ശുപാർശ ഉപദേശം (Crop Recommendation)**\n\n"
        if has_reco:
            recos = ", ".join(ctx.recommended_crops[:3])
            resp += f"നിങ്ങളുടെ കൃഷിയിടത്തിലെ മണ്ണിനും കാലാവസ്ഥയ്ക്കും ഏറ്റവും അനുയോജ്യമായ വിളകൾ: **{recos}**.\n\n"
        elif has_soil:
            resp += f"മണ്ണിലെ NPK അളവ് ({ctx.nitrogen or '--'} N, {ctx.phosphorus or '--'} P, {ctx.potassium or '--'} K) അനുസരിച്ച് ധാന്യവിളകളും പയറുവർഗ്ഗങ്ങളും അനുയോജ്യമാണ്.\n\n"
        else:
            resp += "കൃത്യമായ വിള ശുപാർശ ലഭിക്കാൻ 'എന്റെ ഫാമുകൾ' എന്നതിൽ മണ്ണുപരിശോധനാ ഫലം നൽകുക.\n\n"
        resp += "• ഗുണമേന്മയുള്ള വിത്തുകൾ തിരഞ്ഞെടുക്കുക, ശരിയായ അകലത്തിൽ നടുക."
        suggs = ["ഏത് വളം എത്ര അളവിൽ നൽകണം?", "മാർക്കറ്റ് വില എത്രയാണ്?", "കാലാവസ്ഥ പ്രവചനം"]
        return resp, suggs

    if intent == "soil_npk":
        resp = "🧪 **മണ്ണിലെ പോഷകങ്ങൾ (NPK) പരിപാലനം**\n\n"
        if has_soil:
            resp += f"**മണ്ണിലെ അളവുകൾ:** നൈട്രജൻ: **{ctx.nitrogen or '--'} kg/ha**, ഫോസ്ഫറസ്: **{ctx.phosphorus or '--'} kg/ha**, പൊട്ടാസ്യം: **{ctx.potassium or '--'} kg/ha**.\n\n"
        resp += "• രാസവളങ്ങൾക്കൊപ്പം ജൈവവളവും ചേർത്ത് മണ്ണിന്റെ ഫലഭൂയിഷ്ഠത നിലനിർത്തുക."
        suggs = ["മണ്ണിന്റെ pH എങ്ങനെ ക്രമീകരിക്കാം?", "ഈ മണ്ണിൽ എന്ത് നടാം?", "നനയ്ക്കൽ വിവരങ്ങൾ"]
        return resp, suggs

    if intent == "msp":
        resp = "⚖️ **താങ്ങുവില (MSP) വിവരങ്ങൾ**\n\n"
        if ctx and ctx.msp_price is not None and ctx.mandi_price is not None:
            diff = round(ctx.mandi_price - ctx.msp_price, 2)
            resp += f"• **സർക്കാർ താങ്ങുവില (MSP):** ₹{ctx.msp_price:,.2f} / ക്വിന്റൽ\n• **ഇന്നത്തെ ചന്ത വില:** ₹{ctx.mandi_price:,.2f} / ക്വിന്റൽ\n\n"
            if diff >= 0:
                resp += f"✅ **താങ്ങുവിലയേക്കാൾ കൂടുതൽ (+₹{diff:,.2f}):** ചന്തയിൽ വിൽക്കുന്നത് ലാഭകരമാണ്.\n"
            else:
                resp += f"⚠️ **താങ്ങുവിലയേക്കാൾ കുറവ് (-₹{abs(diff):,.2f}):** സർക്കാർ സംഭരണ കേന്ദ്രങ്ങളിൽ വിൽക്കാൻ ശ്രദ്ധിക്കുക.\n"
        else:
            resp += "കർഷകർക്ക് ന്യായവില ഉറപ്പാക്കാൻ കേന്ദ്ര സർക്കാർ താങ്ങുവില (MSP) നിശ്ചയിക്കുന്നു."
        suggs = ["വില പ്രവചനം", "ഏറ്റവും നല്ല മാർക്കറ്റ്", "താങ്ങുവില പട്ടിക"]
        return resp, suggs

    # Default Malayalam
    resp = "🌾 **അഗ്രിസ്മാർട്ട് AI സഹായി (AgriSmart AI Assistant)**\n\nനമസ്കാരം കർഷക സുഹൃത്തേ! നിങ്ങളുടെ കൃഷി സംബന്ധമായ ചോദ്യങ്ങൾക്ക് മറുപടി നൽകാൻ ഞാൻ ഇവിടെയുണ്ട്:\n\n"
    resp += "• **വിള ശുപാർശ:** മണ്ണിനും കാലാവസ്ഥയ്ക്കും യോജിച്ച വിളകൾ\n• **മണ്ണുപരിപാലനം:** NPK വളപ്രയോഗവും pH ക്രമീകരണവും\n• **കാലാവസ്ഥ:** കൃഷിപ്പണികൾക്കുള്ള മഴ, വെയിൽ വിവരങ്ങൾ\n• **മാർക്കറ്റ് നിരക്ക്:** താങ്ങുവിലയും (MSP) ചന്തവിലയും താരതമ്യം ചെയ്യുക\n\nഎങ്ങനെ സഹായിക്കണം?"
    suggs = ["ഏത് വിളയാണ് അനുയോജ്യം?", "വളപ്രയോഗം എങ്ങനെ?", "ഇന്നത്തെ ചന്തവിലയും താങ്ങുവിലയും", "കാലാവസ്ഥ മുന്നറിയിപ്പ്"]
    return resp, suggs


def _generate_mr(intent: str, ctx: AssistantContext | None) -> tuple[str, list[str]]:
    has_soil = ctx and (ctx.nitrogen is not None or ctx.soil_ph is not None)
    has_reco = ctx and ctx.recommended_crops

    if intent == "crop_recommendation":
        resp = "🌾 **पीक शिफारस सल्ला (Crop Recommendation)**\n\n"
        if has_reco:
            recos = ", ".join(ctx.recommended_crops[:3])
            resp += f"तुमच्या जमिनीच्या माती व स्थानिक हवामानानुसार सर्वात योग्य पिके: **{recos}**.\n\n"
        elif has_soil:
            resp += f"मातीतील पोषक द्रव्ये ({ctx.nitrogen or '--'} N, {ctx.phosphorus or '--'} P, {ctx.potassium or '--'} K) आणि pH {ctx.soil_ph or '--'} नुसार गहू, सोयाबीन, मका किंवा हरभरा लागवड अत्यंत फायदेशीर ठरेल.\n\n"
        else:
            resp += "अचूक पीक शिफारसीसाठी 'माझी शेती' टॅबमध्ये माती परीक्षण माहिती भरा.\n\n"
        resp += "• **पेरणी सल्ला:** प्रमाणित बियाणे वापरा आणि शिफारशीत अंतरावर पेरणी करा.\n• **मशागत:** शेतात चांगले कुजलेले शेणखत मिसळा."
        suggs = ["खतांची मात्रा किती असावी?", "या पिकांचे बाजारभाव काय आहेत?", "हवामान अंदाज काय आहे?"]
        return resp, suggs

    if intent == "soil_npk":
        resp = "🧪 **मातीतील पोषकद्रव्ये (NPK) व्यवस्थापन**\n\n"
        if has_soil:
            resp += f"**तुमच्या मातीचे प्रमाण:** नायट्रोजन: **{ctx.nitrogen or '--'} kg/ha**, फॉस्फरस: **{ctx.phosphorus or '--'} kg/ha**, पोटॅश: **{ctx.potassium or '--'} kg/ha**.\n\n"
            if isinstance(ctx.nitrogen, (int, float)) and ctx.nitrogen < 50:
                resp += "⚠️ **नायट्रोजन कमतरता:** युरिया खताचा हप्त्यांमध्ये वापर करा.\n"
            if isinstance(ctx.phosphorus, (int, float)) and ctx.phosphorus < 25:
                resp += "⚠️ **फॉस्फरस कमतरता:** डीएपी (DAP) किंवा सिंगल सुपर फॉस्फेट (SSP) वापरा.\n"
            if isinstance(ctx.potassium, (int, float)) and ctx.potassium < 30:
                resp += "⚠️ **पोटॅश कमतरता:** दाणे भरण्यासाठी आणि रोगप्रतिकारशक्तीसाठी एमओपी (MOP) द्या.\n"
        else:
            resp += "संतुलित खतांचा वापर आणि सेंद्रिय खतांचा समन्वय जमिनीची सुपीकता टिकवून ठेवतो."
        suggs = ["मातीचा pH कसा सुधारावा?", "कोणते पीक योग्य ठरेल?", "पाणी व्यवस्थापन कसे करावे?"]
        return resp, suggs

    if intent == "msp":
        resp = "⚖️ **शासकीय किमान आधारभूत किंमत (हमीभाव - MSP)**\n\n"
        if ctx and ctx.msp_price is not None and ctx.mandi_price is not None:
            diff = round(ctx.mandi_price - ctx.msp_price, 2)
            resp += f"• **हमीभाव (MSP):** ₹{ctx.msp_price:,.2f} / क्विंटल\n• **सध्याचा बाजारभाव:** ₹{ctx.mandi_price:,.2f} / क्विंटल\n\n"
            if diff >= 0:
                resp += f"✅ **हमीभावापेक्षा जास्त (+₹{diff:,.2f}):** बाजारातील स्थिती चांगली आहे. खुल्या बाजारात विक्री फायदेशीर आहे.\n"
            else:
                resp += f"⚠️ **हमीभावापेक्षा कमी (-₹{abs(diff):,.2f}):** खुल्या बाजारात भाव कमी आहेत. सरकारी खरेदी केंद्रांवर हमीभावाने विका.\n"
        else:
            resp += "शेतकऱ्यांना तोट्यापासून वाचवण्यासाठी शासन हमीभाव (MSP) जाहीर करते."
        suggs = ["बाजारभाव अंदाज", "जवळची कृषी उत्पन्न बाजार समिती", "गहू व सोयाबीन हमीभाव"]
        return resp, suggs

    # Default Marathi
    resp = "🌾 **अ‍ॅग्रीस्मार्ट शेतकरी AI सहाय्यक (AgriSmart AI Assistant)**\n\nनमस्कार शेतकरी बंधूंनो! आपल्या शेतीविषयक प्रश्नांची उत्तरे देण्यासाठी मी सज्ज आहे:\n\n"
    resp += "• **पीक शिफारस:** माती व हवामानानुसार फायदेशीर पिके\n• **माती आरोग्य:** NPK खत व्यवस्थापन व जमिनीचा सामू (pH)\n• **हवामान सल्ला:** पाऊस व तापमानानुसार शेतीची कामे\n• **बाजारभाव:** कृषी उत्पन्न बाजार समिती भाव आणि शासकीय हमीभाव (MSP) तुलना\n\nआज मी आपल्या शेतीसाठी काय मदत करू शकतो?"
    suggs = ["माझ्या शेतीसाठी कोणते पीक योग्य आहे?", "खतांचे प्रमाण सांगा", "आजचा बाजारभाव व हमीभाव", "हवामान अंदाज"]
    return resp, suggs


def _generate_bn(intent: str, ctx: AssistantContext | None) -> tuple[str, list[str]]:
    has_soil = ctx and (ctx.nitrogen is not None or ctx.soil_ph is not None)
    has_reco = ctx and ctx.recommended_crops

    if intent == "crop_recommendation":
        resp = "🌾 **ফসল সুপারিশ পরামর্শ (Crop Recommendation)**\n\n"
        if has_reco:
            recos = ", ".join(ctx.recommended_crops[:3])
            resp += f"আপনার জমির মাটি এবং আবহাওয়া বিশ্লেষণ অনুযায়ী সেরা ফসল: **{recos}**।\n\n"
        elif has_soil:
            resp += f"আপনার মাটির NPK ({ctx.nitrogen or '--'} N, {ctx.phosphorus or '--'} P, {ctx.potassium or '--'} K) এবং pH {ctx.soil_ph or '--'} অনুযায়ী গম, ভুট্টা, সয়াবিন বা ডাল শস্যের ফলন খুব ভালো হবে।\n\n"
        else:
            resp += "সঠিক ফসল পরামর্শের জন্য 'আমার খামার' ট্যাবে মাটির পরীক্ষার বিবরণ প্রদান করুন।\n\n"
        resp += "• উন্নত জাতের প্রত্যয়িত বীজ ব্যবহার করুন এবং সঠিক দূরত্বে রোপণ করুন।"
        suggs = ["কত সার প্রয়োগ করতে হবে?", "বাজার দর কেমন চলছে?", "আবহাওয়ার পূর্বাভাস কি?"]
        return resp, suggs

    if intent == "soil_npk":
        resp = "🧪 **মাটির পুষ্টি উপাদান (NPK) ব্যবস্থাপনা**\n\n"
        if has_soil:
            resp += f"**আপনার মাটির পরিমাণ:** নাইট্রোজেন: **{ctx.nitrogen or '--'} kg/ha**, ফসফরাস: **{ctx.phosphorus or '--'} kg/ha**, পটাশিয়াম: **{ctx.potassium or '--'} kg/ha**।\n\n"
            if isinstance(ctx.nitrogen, (int, float)) and ctx.nitrogen < 50:
                resp += "⚠️ **নাইট্রোজেনের ঘাটতি:** ইউরিয়া সার কিস্তিতে প্রয়োগ করুন।\n"
            if isinstance(ctx.phosphorus, (int, float)) and ctx.phosphorus < 25:
                resp += "⚠️ **ফসফরাসের ঘাটতি:** শিকড় মজবুত করতে ডিএপি (DAP) বা এসএসপি (SSP) সার দিন।\n"
            if isinstance(ctx.potassium, (int, float)) and ctx.potassium < 30:
                resp += "⚠️ **পটাশিয়ামের ঘাটতি:** দানার পুষ্টি ও রোগ প্রতিরোধে এমওপি (MOP) সার প্রয়োগ করুন।\n"
        else:
            resp += "রাসায়নিক সারের সাথে পর্যাপ্ত জৈব সার মিশিয়ে জমির উর্বরতা বৃদ্ধি করুন।"
        suggs = ["মাটির pH কিভাবে উন্নত করবেন?", "কোন ফসল লাগানো উচিত?", "সেচ ব্যবস্থাপনা"]
        return resp, suggs

    if intent == "msp":
        resp = "⚖️ **সরকারি ন্যূনতম সহায়ক মূল্য (MSP) তথ্য**\n\n"
        if ctx and ctx.msp_price is not None and ctx.mandi_price is not None:
            diff = round(ctx.mandi_price - ctx.msp_price, 2)
            resp += f"• **ন্যূনতম সহায়ক মূল্য (MSP):** ₹{ctx.msp_price:,.2f} / কুইন্টাল\n• **বর্তমান বাজার দর:** ₹{ctx.mandi_price:,.2f} / কুইন্টাল\n\n"
            if diff >= 0:
                resp += f"✅ **MSP এর চেয়ে বেশি (+₹{diff:,.2f}):** বাজার দর ভালো রয়েছে। খোলা বাজারে বিক্রি লাভজনক।\n"
            else:
                resp += f"⚠️ **MSP এর চেয়ে কম (-₹{abs(diff):,.2f}):** লোকসান এড়াতে সরকারি সংগ্রহ কেন্দ্রে MSP দরে বিক্রি করুন।\n"
        else:
            resp += "কৃষকদের ক্ষতি থেকে রক্ষা করতে সরকার ন্যূনতম সহায়ক মূল্য (MSP) ঘোষণা করে।"
        suggs = ["বাজার দর পূর্বাভাস", "নিকটবর্তী মন্ডি দর", "গমের সহায়ক মূল্য"]
        return resp, suggs

    # Default Bengali
    resp = "🌾 **এগ্রিস্মার্ট কৃষক AI সহকারী (AgriSmart AI Assistant)**\n\nনমস্কার কৃষক বন্ধু! আপনার কৃষিকাজের সহায়তায় আমি প্রস্তুত:\n\n"
    resp += "• **ফসল সুপারিশ:** আপনার মাটি ও আবহাওয়ার জন্য সবচেয়ে উপযুক্ত ফসল\n• **মাটির স্বাস্থ্য:** নাইট্রোজেন, ফসফরাস, পটাশিয়াম (NPK) ও pH ব্যবস্থাপনা\n• **আবহাওয়া পূর্বাভাস:** সঠিক সময়ে সেচ ও সার দেওয়ার পরামর্শ\n• **বাজার দর:** মন্ডি দর ও সরকারি সহায়ক মূল্য (MSP) তুলনা\n\nআজ আমি আপনার খামারের জন্য কীভাবে সাহায্য করতে পারি?"
    suggs = ["আমার জমির জন্য কোন ফসল উপযুক্ত?", "সারের সঠিক পরিমাণ জানান", "আজকের বাজার দর ও MSP", "আবহাওয়া পরামর্শ"]
    return resp, suggs


GENERATORS = {
    "en": _generate_en,
    "kn": _generate_kn,
    "hi": _generate_hi,
    "te": _generate_te,
    "ta": _generate_ta,
    "ml": _generate_ml,
    "mr": _generate_mr,
    "bn": _generate_bn,
}


def process_assistant_chat(
    message: str,
    language: str = "en",
    context: AssistantContext | None = None,
) -> tuple[str, str, list[str], dict[str, Any]]:
    """
    Process farmer's chat message, detect intent, and generate response
    in the requested language incorporating farm context.
    """
    lang = language.lower().strip()
    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"

    intent = _detect_intent(message)
    generator = GENERATORS.get(lang, _generate_en)
    response_text, suggestions = generator(intent, context)
    context_used = _format_context_summary(context)

    return response_text, lang, suggestions, context_used
