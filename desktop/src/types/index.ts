// ─── Core domain types (matching backend schemas) ────────────────────────────

export interface User {
  id: string;
  username: string;
  email: string;
  display_name: string;
  avatar_url: string | null;
  created_at: string;
}

export interface Guild {
  id: string;
  name: string;
  owner_id: string;
  icon_url: string | null;
  created_at: string;
}

export interface Channel {
  id: string;
  guild_id: string | null;
  category_id: string | null;
  name: string;
  type: 'text' | 'voice' | 'dm' | 'group_dm';
  position: number;
  topic: string | null;
}

export interface Category {
  id: string;
  guild_id: string;
  name: string;
  position: number;
}

export interface Message {
  id: string;
  channel_id: string;
  author: User;
  content: string;
  is_edited: boolean;
  attachments: Attachment[];
  reactions: Reaction[];
  created_at: string;
  updated_at: string;
}

export interface Attachment {
  id: string;
  filename: string;
  content_type: string;
  size: number;
  url: string;
}

export interface Reaction {
  emoji: string;
  count: number;
  me: boolean;
}

export interface DMThread {
  id: string;
  channel_id: string;
  name: string | null;
  participants: User[];
}

export interface VoiceParticipant {
  user: User;
  is_muted: boolean;
  is_deafened: boolean;
}

export interface Role {
  id: string;
  guild_id: string;
  name: string;
  color: number;
  position: number;
  permissions: number;
  is_default: boolean;
}

export interface Invite {
  code: string;
  guild: Guild;
  channel: Channel;
  creator: User;
  uses: number;
  max_uses: number | null;
  expires_at: string | null;
}

export type PresenceStatus = 'online' | 'idle' | 'offline';

export interface WSEvent {
  event: string;
  data: unknown;
}

// ─── Pagination ───────────────────────────────────────────────────────────────

export interface PaginatedMessages {
  items: Message[];
  total: number;
  page: number;
  page_size: number;
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

// ─── Voice state ──────────────────────────────────────────────────────────────

export interface VoiceState {
  channelId: string | null;
  isMuted: boolean;
  isDeafened: boolean;
  participants: VoiceParticipant[];
}
