/**
 * TypeScript type definitions for OCT B-Scan Labeler.
 * Matches backend Pydantic schemas.
 */

/**
 * Label type enum.
 * 0 = unlabeled, 1 = healthy, 2 = unhealthy
 */
export enum Label {
  Unlabeled = 0,
  Healthy = 1,
  Unhealthy = 2,
}

/**
 * Label names for display.
 */
export const LabelNames: Record<Label, string> = {
  [Label.Unlabeled]: 'Unlabeled',
  [Label.Healthy]: 'Healthy',
  [Label.Unhealthy]: 'Unhealthy',
};

/**
 * B-scan statistics for a scan.
 * Field names match backend ScanStats schema.
 */
export interface ScanStats {
  total_bscans: number;
  labeled: number;
  unlabeled: number;
  healthy: number;
  unhealthy: number;
  percent_complete: number;
}

/**
 * Scan with embedded statistics.
 */
export interface Scan {
  scan_id: string;
  created_at: string;
  updated_at: string;
  stats: ScanStats;
}

/**
 * B-scan metadata with navigation info.
 */
export interface BScan {
  id: number;
  scan_id: string;
  bscan_index: number;
  path: string;
  label: Label;
  updated_at: string;
  preview_url: string | null;
  prev_index: number | null;
  next_index: number | null;
  next_unlabeled_index: number | null;
}

/**
 * Request body for updating a B-scan label.
 */
export interface BScanLabelUpdate {
  label: Label.Healthy | Label.Unhealthy;
}

/**
 * Global statistics across all scans.
 * Field names match backend GlobalStats schema.
 */
export interface GlobalStats {
  total_scans: number;
  total_bscans: number;
  total_labeled: number;
  total_unlabeled: number;
  total_healthy: number;
  total_unhealthy: number;
  percent_complete: number;
}

/**
 * Navigation mode for labeling UI.
 */
export enum NavigationMode {
  Sequential = 'sequential',
  UnlabeledOnly = 'unlabeled-only',
}

/**
 * Keyboard hotkey configuration.
 */
export interface KeyboardHotkeys {
  nextFrame: string;
  prevFrame: string;
  labelHealthy: string;
  labelUnhealthy: string;
}

/**
 * Default keyboard hotkeys.
 */
export const DEFAULT_HOTKEYS: KeyboardHotkeys = {
  nextFrame: 'ArrowRight',
  prevFrame: 'ArrowLeft',
  labelHealthy: 'a',
  labelUnhealthy: 's',
};

// ===== AUTH TYPES =====

export interface User {
  id: number;
  username: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

export interface AuthStatus {
  authenticated: boolean;
  user: User | null;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  username: string;
  password: string;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}

// ===== USER SETTINGS TYPES =====

export interface UserSettings {
  auto_advance: boolean;
  hotkey_healthy: string;
  hotkey_unhealthy: string;
  hotkey_next: string;
  hotkey_prev: string;
}

export interface UserSettingsUpdate {
  auto_advance?: boolean;
  hotkey_healthy?: string;
  hotkey_unhealthy?: string;
  hotkey_next?: string;
  hotkey_prev?: string;
}
