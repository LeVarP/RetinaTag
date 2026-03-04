/**
 * TypeScript type definitions for OCT B-Scan Labeler.
 * Matches backend Pydantic schemas.
 */

/**
 * Label type enum.
 * 0 = unset, 1 = healthy, 2 = not healthy
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
  [Label.Unlabeled]: 'Not necessarily healthy',
  [Label.Healthy]: 'Healthy',
  [Label.Unhealthy]: 'Not healthy',
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
  not_necessary_healthy: number;
  cyst_positive: number;
  hard_exudate_positive: number;
  srf_positive: number;
  ped_positive: number;
  cyst_negative: number;
  hard_exudate_negative: number;
  srf_negative: number;
  ped_negative: number;
  cyst_empty: number;
  hard_exudate_empty: number;
  srf_empty: number;
  ped_empty: number;
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
  bscan_key: string | null;
  cyst: number | null;
  hard_exudate: number | null;
  srf: number | null;
  ped: number | null;
  healthy: number | null;
  is_labeled: boolean;
  label: Label;
  updated_at: string;
  preview_url: string | null;
  prev_index: number | null;
  next_index: number | null;
  next_unlabeled_index: number | null;
}

export interface BScanListItem {
  id: number;
  scan_id: string;
  bscan_index: number;
  bscan_key: string | null;
  path: string;
  cyst: number | null;
  hard_exudate: number | null;
  srf: number | null;
  ped: number | null;
  healthy: number | null;
  is_labeled: boolean;
  label: Label;
  updated_at: string;
}

/**
 * Request body for updating a B-scan label.
 */
export interface BScanHealthUpdate {
  healthy: 0 | 1;
}

export interface BScanPathologyUpdate {
  cyst?: 0 | 1;
  hard_exudate?: 0 | 1;
  srf?: 0 | 1;
  ped?: 0 | 1;
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
  total_not_necessary_healthy: number;
  total_cyst_positive: number;
  total_hard_exudate_positive: number;
  total_srf_positive: number;
  total_ped_positive: number;
  percent_complete: number;
}

/**
 * Keyboard hotkey configuration.
 */
export interface KeyboardHotkeys {
  nextFrame: string;
  prevFrame: string;
  labelHealthy: string;
  labelUnhealthy: string;
  toggleCyst: string;
  toggleHardExudate: string;
  toggleSrf: string;
  togglePed: string;
}

/**
 * Default keyboard hotkeys.
 */
export const DEFAULT_HOTKEYS: KeyboardHotkeys = {
  nextFrame: 'ArrowRight',
  prevFrame: 'ArrowLeft',
  labelHealthy: 'a',
  labelUnhealthy: 's',
  toggleCyst: '1',
  toggleHardExudate: '2',
  toggleSrf: '3',
  togglePed: '4',
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
  hotkey_healthy: string;
  hotkey_unhealthy: string;
  hotkey_cyst: string;
  hotkey_hard_exudate: string;
  hotkey_srf: string;
  hotkey_ped: string;
  hotkey_next: string;
  hotkey_prev: string;
}

export interface UserSettingsUpdate {
  hotkey_healthy?: string;
  hotkey_unhealthy?: string;
  hotkey_cyst?: string;
  hotkey_hard_exudate?: string;
  hotkey_srf?: string;
  hotkey_ped?: string;
  hotkey_next?: string;
  hotkey_prev?: string;
}
