import json
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)


SYSTEM_PROMPT = """You are an expert sales copywriter who personalizes direct message sequences.

Given:
- A lead's name and company name
- Research about their company (from their website and LinkedIn)
- Draft DM templates (DM 1, DM 2, DM 3)

Your job:
1. Analyze the company research to identify their likely pain points, goals, and challenges.
2. Personalize each DM template by weaving in specific details about the company.
3. Keep the core message and CTA of each template intact.
4. Make the personalization feel natural and insightful, not generic.
5. Use the lead's first name where appropriate.

Return ONLY valid JSON with this exact structure:
{
  "pain_points": "Brief summary of identified pain points",
  "dm_1": "Personalized DM 1 text",
  "dm_2": "Personalized DM 2 text",
  "dm_3": "Personalized DM 3 text"
}"""


def personalize_dms(
    lead_name: str,
    company_name: str,
    research: str,
    dm_templates: dict[str, str],
) -> dict[str, str]:
    """Use Gemini to personalize DM templates based on company research."""
    model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=SYSTEM_PROMPT)

    user_prompt = f"""## Lead Info
- Name: {lead_name}
- Company: {company_name}

## Company Research
{research}

## DM Templates to Personalize

### DM 1 (Initial outreach)
{dm_templates['dm_1']}

### DM 2 (Follow-up)
{dm_templates['dm_2']}

### DM 3 (Final follow-up)
{dm_templates['dm_3']}

Personalize all 3 DMs based on the company research. Return valid JSON only."""

    response = model.generate_content(user_prompt)
    text = response.text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        print(f"  ⚠ Failed to parse Gemini response as JSON. Raw response:\n{text[:500]}")
        return {"dm_1": "", "dm_2": "", "dm_3": ""}

    return {
        "dm_1": result.get("dm_1", ""),
        "dm_2": result.get("dm_2", ""),
        "dm_3": result.get("dm_3", ""),
    }
