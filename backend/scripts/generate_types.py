import os

def generate_typescript():
    # Simplified type generator for our core models
    # In a real project, use 'pydantic2ts' or 'datamodel-code-generator'
    
    ts_content = """// AUTO-GENERATED - DO NOT EDIT MANUALLY
export interface Message {
  role: 'user' | 'seller' | 'ai';
  content: string;
  timestamp: string;
}

export interface ListingMetadata {
  item_name: string;
  suggested_low_price: number;
  suggested_high_price: number;
  condition: string;
  description: string;
}

export interface UnifiedResponse {
  aggressive_thought: string;
  sympathetic_thought: string;
  analytical_thought: string;
  final_response: string;
  rationale: string;
  suggested_next_price: number;
}

export interface NegotiationState {
  session_id: string;
  item_metadata: ListingMetadata;
  history: Message[];
  current_lowball_price: number;
}
"""
    
    output_path = os.path.join("..", "mobile", "constants", "Types.ts")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(ts_content)
    print(f"Generated TypeScript types at {output_path}")

if __name__ == "__main__":
    generate_typescript()
