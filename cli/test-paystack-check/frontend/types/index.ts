/**
 * Core TypeScript types for the application.
 */

export interface User {
  id: string;
  email: string;
  fullName: string;
  createdAt: string;
  lastLogin: string | null;
}

export interface CompleteUserProfile extends User {
  bio: string | null;
  phone: string | null;
  location: string | null;
  avatarUrl: string | null;
  avatarVersion: number;
  websiteUrl: string | null;
  linkedinUrl: string | null;
  githubUrl: string | null;
  currentPosition: string | null;
  company: string | null;
  theme: string;
}

export interface ProfileUpdate {
  fullName?: string;
  phone?: string;
  location?: string;
  websiteUrl?: string;
  linkedinUrl?: string;
  githubUrl?: string;
  bio?: string;
  currentPosition?: string;
  company?: string;
  theme?: string;
}

export interface APIError {
  detail: string;
  errors?: Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
}
