export type User = {
  id: string;
  email: string;
  full_name: string;
  role: string;
  country: string;
  institution: string;
  bio: string;
  verified: boolean;
  onboarded: boolean;
  created_at: string;
};
export type Session = {
  id: string;
  created_at: string;
  expires_at: string;
  user_agent: string;
  current: boolean;
};
