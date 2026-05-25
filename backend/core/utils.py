import re
from typing import Dict, Any, List, Union

def strip_json_markdown(text: str) -> str:
    """
    Safely removes markdown code blocks from a string to extract raw JSON.
    Handles variants like ```json, ```, and stray text around the blocks.
    """
    # Use regex to find content between triple backticks
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text.strip()

def clean_schema(schema: Union[Dict[str, Any], List[Any]]) -> Union[Dict[str, Any], List[Any]]:
    """
    Recursively removes unsupported metadata keys for Gemini's response_schema.
    Preserves 'type', 'properties', 'items', 'required', and 'description' for context.
    """
    if isinstance(schema, list):
        return [clean_schema(i) for i in schema]
        
    if not isinstance(schema, dict):
        return schema

    # 1. Handle anyOf (Optional fields in Pydantic)
    if "anyOf" in schema:
        types = [x for x in schema["anyOf"] if x.get("type") != "null"]
        return clean_schema(types[0]) if types else {}

    # 2. Supported keys in Gemini's response_schema
    # Gemini 1.5+ supports 'description' inside properties for better context.
    allowed_keys = ["type", "properties", "items", "required", "enum", "format", "description"]
    
    cleaned: Dict[str, Any] = {}
    for k, v in schema.items():
        if k in allowed_keys:
            if k == "properties":
                # For the properties dict, we must preserve all keys (property names)
                cleaned[k] = {prop_name: clean_schema(prop_def) for prop_name, prop_def in v.items()}
            elif k == "items":
                cleaned[k] = clean_schema(v)
            else:
                cleaned[k] = v
                
    return cleaned
