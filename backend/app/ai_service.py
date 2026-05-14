import json
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from loguru import logger
from app.config import settings

# Initialise Async OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = f"""You are an expert business enquiry analyst for a professional services firm.

Your task is to analyse incoming client enquiries and classify them accurately.

You MUST return valid JSON with the following fields:
- "category": One of these exact categories: {', '.join(f'"{c}"' for c in settings.CATEGORIES)}
- "confidence": A float between 0.0 and 1.0 representing your certainty of the classification
- "sentiment": One of "positive", "neutral", or "negative"
- "priority": One of "low", "medium", "high", or "urgent"
- "suggested_response": A professional, helpful draft reply the staff member can send to the client (2-4 sentences)
- "recommended_actions": A list of 2-4 concrete next steps for the staff member to take
- "reasoning": A brief explanation (1-2 sentences) of why this classification was chosen

## Classification Guidelines with Examples:

### "New Client Enquiry"
Messages from potential clients asking about services, pricing, or availability.
Example: "Hi, I'm looking for accounting services for my small business. Could you tell me about your packages and pricing?"

### "Support Request"
Existing clients needing help with current services or accounts.
Example: "I can't access my client portal and I need to download my tax documents before Friday."

### "Complaint"
Expressions of dissatisfaction about service quality, delays, or errors.
Example: "I'm very unhappy with the delay in processing my application. It's been three weeks and no one has contacted me."

### "General Question"
Non-urgent informational queries that don't fit other categories.
Example: "What are your office hours during the Christmas period?"

### "Urgent/Escalation"
Time-sensitive matters requiring immediate attention, legal deadlines, or escalated issues.
Example: "We have a regulatory deadline tomorrow and the documents you were preparing haven't arrived. This needs immediate attention."

## Priority Assignment Rules:
- "urgent": Regulatory deadlines, legal matters, system outages affecting clients
- "high": Complaints, time-sensitive requests (within 48 hours)
- "medium": New client enquiries, standard support requests
- "low": General questions, informational queries

## Important:
If the input is vague, nonsensical, or not a genuine client enquiry, still classify it to the best of your ability but set confidence below 0.4.
"""

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
    before_sleep=lambda retry_state: logger.warning(f"Retrying OpenAI API call: attempt {retry_state.attempt_number}")
)
async def call_openai_api(text: str) -> dict:
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        temperature=settings.OPENAI_TEMPERATURE,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyse the following client enquiry:\n\n{text}"},
        ],
    )
    return json.loads(response.choices[0].message.content)

async def analyse_enquiry(text: str) -> dict:
    """
    Analyse a client enquiry using OpenAI's GPT model.
    """
    logger.info(f"Starting analysis for enquiry of length {len(text)}")
    
    try:
        result = await call_openai_api(text)
        
        expected_fields = [
            "category", "confidence", "sentiment",
            "priority", "suggested_response", "recommended_actions", "reasoning",
        ]
        
        for field in expected_fields:
            if field not in result:
                logger.error(f"Missing field in AI response: {field}")
                return {
                    "success": False,
                    "error": f"AI response missing expected field: '{field}'.",
                }
                
        result["is_vague"] = result.get("confidence", 0) < 0.4
        
        logger.info(f"Analysis completed successfully. Category: {result.get('category')}")
        return {
            "success": True,
            "data": result,
        }

    except AuthenticationError:
        logger.error("OpenAI authentication failed.")
        return {"success": False, "error": "OpenAI authentication failed. Please check your API key."}
    except RateLimitError:
        logger.error("OpenAI rate limit exceeded after retries.")
        return {"success": False, "error": "OpenAI rate limit exceeded. Please try again in a moment."}
    except APIConnectionError:
        logger.error("OpenAI connection error after retries.")
        return {"success": False, "error": "Could not connect to OpenAI API. Please check your network connection."}
    except APIError as e:
        logger.error(f"OpenAI API error: {e}")
        return {"success": False, "error": f"OpenAI API error: {str(e)}"}
    except json.JSONDecodeError:
        logger.error("Failed to parse AI response as valid JSON.")
        return {"success": False, "error": "Failed to parse AI response as valid JSON."}
    except Exception as e:
        logger.exception("Unexpected error during AI analysis.")
        return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}
