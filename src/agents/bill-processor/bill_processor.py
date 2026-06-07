import logging
from typing import Dict, Any, Optional
from src.tools.llm_client import llm_client
from .image_preprocessor import ImagePreprocessor

logger = logging.getLogger(__name__)

class BillProcessor:
    def __init__(self):
        self.preprocessor = ImagePreprocessor()
    
    async def process_bill_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Process a bill image: preprocess, extract data using LLM, validate.
        Returns a dictionary with extracted bill data or error.
        """
        # Step 1: Check image quality
        quality = self.preprocessor.check_image_quality(image_bytes)
        if not quality["usable"]:
            logger.warning(f"Poor image quality: {quality['reason']}")
            # We can still try to process, but note the quality
        
        # Step 2: Preprocess image
        try:
            processed_bytes = self.preprocessor.preprocess_image(image_bytes)
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            # Fallback to original bytes
            processed_bytes = image_bytes
        
        # Step 3: Extract data using LLM (Claude Vision)
        extraction_result = await llm_client.extract_bill_data(processed_bytes)
        
        # Step 4: Validate and normalize the extracted data
        if "error" in extraction_result:
            logger.error(f"Bill extraction failed: {extraction_result['error']}")
            return extraction_result
        
        validated_data = self._validate_and_normalize(extraction_result)
        return validated_data
    
    def _validate_and_normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize extracted bill data.
        Ensures required fields are present and in correct format.
        """
        # Make a copy to avoid modifying original
        normalized = data.copy()
        
        # Ensure bill_type is valid
        bill_type = normalized.get("bill_type")
        valid_types = ["electricity", "water", "internet", "phone", "rent", "loan", "gas", "other"]
        if bill_type not in valid_types:
            logger.warning(f"Invalid bill_type: {bill_type}, defaulting to 'other'")
            normalized["bill_type"] = "other"
        
        # Ensure amount_due is integer and positive
        amount = normalized.get("amount_due")
        if amount is not None:
            try:
                amount_int = int(amount)
                if amount_int < 0:
                    logger.warning(f"Negative amount due: {amount_int}, setting to 0")
                    amount_int = 0
                normalized["amount_due"] = amount_int
            except (ValueError, TypeError):
                logger.warning(f"Invalid amount_due: {amount}, setting to 0")
                normalized["amount_due"] = 0
        else:
            normalized["amount_due"] = 0
        
        # Ensure due_date is in YYYY-MM-DD format or None
        due_date = normalized.get("due_date")
        if due_date is not None:
            # Simple validation: check if it matches YYYY-MM-DD
            if isinstance(due_date, str) and len(due_date) == 10 and due_date[4] == '-' and due_date[7] == '-':
                # Additional check: year, month, day are numbers
                try:
                    year = int(due_date[0:4])
                    month = int(due_date[5:7])
                    day = int(due_date[8:10])
                    if not (1 <= month <= 12 and 1 <= day <= 31):
                        logger.warning(f"Invalid date components: {due_date}")
                        normalized["due_date"] = None
                except ValueError:
                    logger.warning(f"Invalid date format: {due_date}")
                    normalized["due_date"] = None
            else:
                logger.warning(f"Due date not in YYYY-MM-DD format: {due_date}")
                normalized["due_date"] = None
        else:
            normalized["due_date"] = None
        
        # Ensure issuer is string or None
        issuer = normalized.get("issuer")
        if issuer is not None and not isinstance(issuer, str):
            normalized["issuer"] = str(issuer)
        
        # Ensure account_number is string or None
        account = normalized.get("account_number")
        if account is not None and not isinstance(account, str):
            normalized["account_number"] = str(account)
        
        # Ensure billing_period_from and billing_period_to are valid dates or None
        for field in ["billing_period_from", "billing_period_to"]:
            date_val = normalized.get(field)
            if date_val is not None:
                if isinstance(date_val, str) and len(date_val) == 10 and date_val[4] == '-' and date_val[7] == '-':
                    try:
                        year = int(date_val[0:4])
                        month = int(date_val[5:7])
                        day = int(date_val[8:10])
                        if not (1 <= month <= 12 and 1 <= day <= 31):
                            logger.warning(f"Invalid {field} components: {date_val}")
                            normalized[field] = None
                    except ValueError:
                        logger.warning(f"Invalid {field} format: {date_val}")
                        normalized[field] = None
                else:
                    logger.warning(f"{field} not in YYYY-MM-DD format: {date_val}")
                    normalized[field] = None
        
        # Ensure payment_methods is a list of strings
        payment_methods = normalized.get("payment_methods")
        if payment_methods is not None:
            if not isinstance(payment_methods, list):
                logger.warning(f"payment_methods is not a list: {payment_methods}")
                normalized["payment_methods"] = []
            else:
                # Ensure each item is a string
                normalized["payment_methods"] = [str(m) for m in payment_methods]
        else:
            normalized["payment_methods"] = []
        
        return normalized
