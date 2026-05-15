export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      enquiry_analyses: {
        Row: {
          id: number
          enquiry_text: string
          category: string
          confidence: number
          sentiment: string
          priority: string
          suggested_response: string
          recommended_actions: string
          reasoning: string
          is_vague: boolean
          created_at: string
        }
        Insert: {
          id?: number
          enquiry_text: string
          category: string
          confidence: number
          sentiment: string
          priority: string
          suggested_response: string
          recommended_actions: string
          reasoning: string
          is_vague?: boolean
          created_at?: string
        }
        Update: {
          id?: number
          enquiry_text?: string
          category?: string
          confidence?: number
          sentiment?: string
          priority?: string
          suggested_response?: string
          recommended_actions?: string
          reasoning?: string
          is_vague?: boolean
          created_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}