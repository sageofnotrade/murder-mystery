export interface Clue {
  id: string
  description: string
  type: 'physical' | 'testimony' | 'observation' | 'document'
  location: string
  discovered_at: string
  discovery_method: string
  discovery_location: string
  relevance_score: number
  is_red_herring: boolean
  notes: string | null
  connections: ClueConnection[]
}

export interface ClueConnection {
  id: string
  connected_clue_id: string
  connection_type: string
  details: {
    reason: string
  }
  created_at: string
}

export interface ClueAnalysis {
  clue_details: Clue
  related_clues: ClueConnection[]
  related_suspects: string[]
  analysis_context: string
  focus_areas: string[]
  timestamp: string
}

export interface ApiResponse<T> {
  data: T
  error?: string
} 