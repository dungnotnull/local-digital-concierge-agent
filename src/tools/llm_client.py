import os
import base64
from typing import Optional, Dict, Any
import anthropic
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    async def extract_bill_data(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Extract structured data from a bill image using Claude Vision.
        Returns a dictionary with bill fields.
        """
        # Encode image to base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        prompt = """
        Extract structured data from this Vietnamese utility/household bill image.
        
        Find and return ONLY the following fields (return null if not found):
        - bill_type: "electricity" | "water" | "internet" | "phone" | "rent" | "loan" | "gas" | "other"
        - issuer: Name of the company/organization issuing the bill
        - account_number: Customer account or meter number (if visible)
        - amount_due: Total amount to pay (numbers only, VND)
        - due_date: Payment deadline (ISO format YYYY-MM-DD)
        - billing_period_from: Start of billing period (YYYY-MM-DD or null)
        - billing_period_to: End of billing period (YYYY-MM-DD or null)
        - payment_methods: List of payment methods shown (e.g., ["bank transfer", "cash"])
        
        Return as JSON only. Do not include any other text.
        If this is not a bill, return {"error": "not_a_bill"}.
        """
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ],
                    }
                ],
            )
            # Extract JSON from response
            import json
            response_text = message.content[0].text.strip()
            # Find JSON in the response (assuming it's the only JSON)
            # Simple extraction: look for first { and last }
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return {"error": "no_json_found", "raw": response_text}
        except Exception as e:
            return {"error": str(e)}

    async def draft_message(self, context: Dict[str, Any]) -> str:
        """
        Draft a message using Claude Text based on context.
        Context should include: issue_description, provider_name, time_slots
        """
        prompt = f"""
        Write a polite Vietnamese SMS/Zalo message to book a service appointment.
        
        Context:
        - Service needed: {context.get('issue_description', '')}
        - Provider name: {context.get('provider_name', '')}  
        - Preferred times: {context.get('time_slots', [])}
        
        Rules:
        - Vietnamese only, warm and polite tone
        - Under 160 characters if possible (SMS length)
        - Include: what service is needed, preferred time options
        - Do NOT include: home address (will be given if they reply), full name unless required
        - End with a question: "Qu?½ vá»‹ c?³ thá»ƒ s?¡p xá»¿p kh?´ng áº¡?"
        
        Draft only the message text, nothing else.
        """
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=200,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            return message.content[0].text.strip()
        except Exception as e:
            # Fallback to template
            return self._template_fallback(context)

    def _template_fallback(self, context: Dict[str, Any]) -> str:
        """Fallback message template when Claude API is unavailable."""
        issue = context.get('issue_description', '')
        provider = context.get('provider_name', '')
        times = context.get('time_slots', [])
        time_str = ', '.join(times) if times else 'cac thu'
        return f"Xin chào {provider}, tôi c?n {issue}. Th?i gian thu?n ti?n: {time_str}. Mong ph?n h?i s?m. C?m õn!"

# Global instance
llm_client = LLMClient()
