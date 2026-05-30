import os
import sys
import inspect
from typing import List, Optional, Union, get_args, get_origin
from pydantic import BaseModel

# Add the parent directory to sys.path so we can import models
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from datetime import datetime
import models.schemas as schemas

TYPE_MAPPING = {
    str: "string",
    int: "number",
    float: "number",
    bool: "boolean",
    datetime: "string",
    None: "null",
    type(None): "null",
}

def get_ts_type(py_type) -> str:
    origin = get_origin(py_type)
    args = get_args(py_type)

    if py_type in TYPE_MAPPING:
        return TYPE_MAPPING[py_type]
    
    if origin is list or origin is List:
        return f"{get_ts_type(args[0])}[]"
    
    if origin is Union:
        # Handle Optional[T] which is Union[T, None]
        filtered_args = [a for a in args if a is not type(None)]
        ts_types = [get_ts_type(a) for a in filtered_args]
        joined = " | ".join(ts_types)
        if type(None) in args:
            # It's optional, but in TS interfaces we often use '?'
            return joined
        return joined

    if origin is Optional:
        return get_ts_type(args[0])

    if hasattr(py_type, "__name__"):
        return py_type.__name__
    
    return "any"

def generate_interface(model: type[BaseModel]) -> str:
    lines = [f"export interface {model.__name__} {{"]
    
    # Get all fields including inherited ones
    for name, field in model.model_fields.items():
        ts_type = get_ts_type(field.annotation)
        is_optional = get_origin(field.annotation) is Union and type(None) in get_args(field.annotation)
        
        # Special case for session_id in ListingMetadata which is Optional but not in Union format sometimes
        if name == "session_id" and "Optional" in str(field.annotation):
             is_optional = True

        # Pydantic v2 metadata check for optionality if annotation didn't catch it
        if not field.is_required():
            is_optional = True

        opt_char = "?" if is_optional else ""
        lines.append(f"  {name}{opt_char}: {ts_type};")
    
    lines.append("}")
    return "\n".join(lines)

def generate_typescript():
    # Collect all classes in schemas.py that inherit from BaseModel
    models_to_generate = []
    for name, obj in inspect.getmembers(schemas):
        if inspect.isclass(obj) and issubclass(obj, BaseModel) and obj is not BaseModel:
            # We want to maintain a specific order if possible, or just alphabetical
            models_to_generate.append(obj)

    # Simple topological sort or just manual ordering for cleaner output
    # For this project, alphabetical is fine, but let's put core ones first
    priority = ["Message", "ItemExtraction", "ListingMetadata", "AnalyticalData", "SupervisorSynthesis", "ChatResponse", "NegotiationState"]
    models_to_generate.sort(key=lambda x: priority.index(x.__name__) if x.__name__ in priority else 100)

    ts_content = "// AUTO-GENERATED - DO NOT EDIT MANUALLY\n\n"
    for model in models_to_generate:
        ts_content += generate_interface(model) + "\n\n"
    
    # Correct path relative to root: backend/scripts -> ../../mobile
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "mobile", "constants", "Types.ts"))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(ts_content.strip() + "\n")
    
    print(f"Generated TypeScript types at {output_path} from {len(models_to_generate)} Pydantic models.")

if __name__ == "__main__":
    generate_typescript()
