import logging
from typing import Dict, Any, Optional, List
from src.tools.llm_client import llm_client

logger = logging.getLogger(__name__)

class MessageDrafter:
    def __init__(self):
        # Template fallbacks for each category
        self.templates = {
            'plumbing': "Xin chào {provider}, nhà tôi có {issue}. Th?i gian thu?n ti?n: {times}. Mong ph?n h?i s?m. C?m õn!",
            'electrical': "Xin chào {provider}, nhà tôi có s? c? ði?n: {issue}. Th?i gian thu?n ti?n: {times}. Mong ph?n h?i s?m. C?m õn!",
            'hvac': "Xin chào {provider}, máy ði?u h?a nhà tôi c?n {issue}. Th?i gian thu?n ti?n: {times}. Mong ph?n h?i s?m. C?m õn!",
            'appliance': "Xin chào {provider}, thi?t b? gia d?ng {issue}. Th?i gian thu?n ti?n: {times}. Mong ph?n h?i s?m. C?m õn!",
            'structural': "Xin chào {provider}, nhà tôi có v?n ð???: {issue}. Th?i gian thu?n ti?n: {times}. Mong ph?n h?i s?m. C?m õn!",
            'pest_control': "Xin chào {provider}, nhà tôi có v?n ð? sâu b?nh: {issue}. Th?i gian thu?n ti?n: {times}. Mong ph?n h?i s?m. C?m õn!",
            'cleaning': "Xin chào {provider}, nhà tôi c?n d?ch v? v? sinh: {issue}. Th?i gian thu?n ti?n: {times}. Mong ph?n h?i s?m. C?m õn!",
            'default': "Xin chào {provider}, tôi c?n {issue}. Th?i gian thu?n ti?n: {times}. Mong ph?n h?i s?m. C?m õn!"
        }
    
    async def draft_service_request(self, issue_description: str, provider_name: str, time_slots: List[str]) -> str:
        """
        Draft a service request message using LLM or template fallback.
        """
        # First, classify the issue to get category (we could reuse the classifier, but for simplicity we'll do a simple version)
        category = self._classify_issue_category(issue_description)
        
        # Prepare context for LLM
        context = {
            "issue_description": issue_description,
            "provider_name": provider_name,
            "time_slots": time_slots
        }
        
        # Try to draft using LLM
        try:
            draft = await llm_client.draft_message(context)
            # If the draft is too long, we can truncate or use template
            if len(draft) > 160:
                logger.warning(f"LLM draft too long ({len(draft)} chars), using template")
                return self._template_fallback(category, issue_description, provider_name, time_slots)
            return draft
        except Exception as e:
            logger.error(f"LLM drafting failed: {e}, using template")
            return self._template_fallback(category, issue_description, provider_name, time_slots)
    
    def _classify_issue_category(self, issue_description: str) -> str:
        """Simple keyword-based category classification for template selection."""
        issue_lower = issue_description.lower()
        if any(word in issue_lower for word in ['vÃ²i', 'nÆ°á»›c', 'rÃ²', 'rÃ³', 'rÃ¡nh', 'cÃ¡p', 'bÃ¡y']):
            return 'plumbing'
        elif any(word in issue_lower for word in ['Ä‘iá»‡n', 'bÃ t', 'cÃ´ng', 't?', 'Ä‘iá»‡n thoáº¡i', 'má»‡y']):
            return 'electrical'
        elif any(word in issue_lower for word in ['mÃ¡y Ä‘iá»u hÃ²a', 'lÃ m', 'giá»', 'kh?³ng lÃ m']):
            return 'hvac'
        elif any(word in issue_lower for word in ['tá»‹nh', 'má»ƒy', 'bÄƒng', 'chÄ»nh']):
            return 'appliance'
        elif any(word in issue_lower for word in ['cá»§a', 'cá»§a', 'b? ng', 'l?²']):
            return 'structural'
        elif any(word in issue_lower for word in ['cÃ´n trÆ°ng', 'chuá»™t', 'chuot']):
            return 'pest_control'
        elif any(word in issue_lower for word in ['v? sinh', 'dÆ°á»£c', 'quÄƒt']):
            return 'cleaning'
        else:
            return 'default'
    
    def _template_fallback(self, category: str, issue_description: str, provider_name: str, time_slots: List[str]) -> str:
        """Generate a message from template."""
        template = self.templates.get(category, self.templates['default'])
        times = ', '.join(time_slots) if time_slots else 'các th?i gian'
        return template.format(provider=provider_name, issue=issue_description, times=times)
