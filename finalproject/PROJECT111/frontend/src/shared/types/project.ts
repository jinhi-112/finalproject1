export interface Project {
  project_id: number;
  creator: {
    user_id: number;
    name: string;
    email: string;
    specialty?: string;
    introduction?: string;
  };
  title: string;
  description: string;
  goal: string;
  tech_stack: string;
  recruitment_count: number;
  start_date: string;
  end_date: string;
  application_deadline: string | null;
  applicant_count: number;
  user_matching_rate: number | null;
  user_match_explanation?: {
      for_recommendation_page: {
          primary_reason: string;
          additional_reasons: string[];
      };
      for_detail_page: {
          positive_points: string[];
          negative_points: string[];
      };
  };
  user_match_scores?: {
    tech: number;
    personality: number;
    experience: number;
  };
  is_open: boolean;
  created_at: string;
}
