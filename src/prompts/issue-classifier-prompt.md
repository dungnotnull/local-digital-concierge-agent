'The user described a household problem: "{user_description}"

Classify into ONE service category:
- "plumbing": water pipes, faucets, toilets, drains
- "electrical": power, switches, outlets, appliances
- "hvac": air conditioning, heating, ventilation
- "appliance": refrigerator, washing machine, oven, other appliances
- "structural": walls, roof, doors, windows, floors
- "pest_control": insects, rodents
- "cleaning": general cleaning services
- "other": anything else

Return JSON: {"category": "...", "urgency": "emergency|normal|low", "keywords": ["..."]}
Emergency = safety risk (gas leak, flood, fire, no power); Normal = daily disruption; Low = aesthetic/minor.
'
