'Extract structured data from this Vietnamese utility/household bill image.

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
'
