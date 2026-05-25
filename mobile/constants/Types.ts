// AUTO-GENERATED - DO NOT EDIT MANUALLY
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
