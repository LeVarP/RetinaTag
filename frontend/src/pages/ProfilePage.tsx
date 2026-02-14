import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useSettings } from '@/context/SettingsContext';
import { api } from '@/services/api';
import { DEFAULT_HOTKEYS } from '@/types';
import styles from './ProfilePage.module.css';

function HotkeyInput({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (key: string) => void;
}) {
  const [isRecording, setIsRecording] = useState(false);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onChange(e.key);
    setIsRecording(false);
  };

  return (
    <div className={styles.hotkeyField}>
      <label>{label}</label>
      <input
        readOnly
        value={isRecording ? 'Press a key...' : value}
        onFocus={() => setIsRecording(true)}
        onBlur={() => setIsRecording(false)}
        onKeyDown={isRecording ? handleKeyDown : undefined}
        className={`${styles.hotkeyInput} ${isRecording ? styles.recording : ''}`}
      />
    </div>
  );
}

function ProfilePage() {
  const { user } = useAuth();
  const { settings, updateSettings } = useSettings();

  // Local state for settings form
  const [localSettings, setLocalSettings] = useState(settings);
  const [settingsSaved, setSettingsSaved] = useState(false);
  const [settingsError, setSettingsError] = useState('');

  // Password change state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordMsg, setPasswordMsg] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  // Admin: create user state
  const [newUsername, setNewUsername] = useState('');
  const [newUserPassword, setNewUserPassword] = useState('');
  const [createUserMsg, setCreateUserMsg] = useState('');
  const [createUserError, setCreateUserError] = useState('');
  const [isCreatingUser, setIsCreatingUser] = useState(false);

  // Sync local settings when context changes
  const handleSaveSettings = async () => {
    setSettingsSaved(false);
    setSettingsError('');
    try {
      await updateSettings(localSettings);
      setSettingsSaved(true);
      setTimeout(() => setSettingsSaved(false), 3000);
    } catch {
      setSettingsError('Failed to save settings');
    }
  };

  const handleResetDefaults = () => {
    setLocalSettings({
      auto_advance: true,
      hotkey_healthy: DEFAULT_HOTKEYS.labelHealthy,
      hotkey_unhealthy: DEFAULT_HOTKEYS.labelUnhealthy,
      hotkey_next: DEFAULT_HOTKEYS.nextFrame,
      hotkey_prev: DEFAULT_HOTKEYS.prevFrame,
    });
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordMsg('');
    setPasswordError('');
    if (newPassword !== confirmPassword) {
      setPasswordError('Passwords do not match');
      return;
    }
    setIsChangingPassword(true);
    try {
      await api.changePassword({ current_password: currentPassword, new_password: newPassword });
      setPasswordMsg('Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch {
      setPasswordError('Current password is incorrect');
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateUserMsg('');
    setCreateUserError('');
    setIsCreatingUser(true);
    try {
      await api.register({ username: newUsername, password: newUserPassword });
      setCreateUserMsg(`User "${newUsername}" created`);
      setNewUsername('');
      setNewUserPassword('');
    } catch (err: any) {
      setCreateUserError(err.response?.data?.detail || 'Failed to create user');
    } finally {
      setIsCreatingUser(false);
    }
  };

  return (
    <div className="container">
      <h2 className={styles.pageTitle}>Profile</h2>

      {/* Account Info */}
      <section className={styles.section}>
        <h3>Account</h3>
        <div className={styles.infoRow}>
          <span className={styles.infoLabel}>Username:</span>
          <span>{user?.username}</span>
        </div>
        <div className={styles.infoRow}>
          <span className={styles.infoLabel}>Role:</span>
          <span>{user?.is_admin ? 'Admin' : 'User'}</span>
        </div>
        <div className={styles.infoRow}>
          <span className={styles.infoLabel}>Created:</span>
          <span>{user?.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}</span>
        </div>
      </section>

      {/* Labeling Preferences */}
      <section className={styles.section}>
        <h3>Labeling Preferences</h3>

        <div className={styles.toggleRow}>
          <label htmlFor="autoAdvance">Auto-advance after labeling</label>
          <input
            id="autoAdvance"
            type="checkbox"
            checked={localSettings.auto_advance}
            onChange={(e) =>
              setLocalSettings((s) => ({ ...s, auto_advance: e.target.checked }))
            }
          />
        </div>

        <div className={styles.hotkeysGrid}>
          <HotkeyInput
            label="Healthy"
            value={localSettings.hotkey_healthy}
            onChange={(key) => setLocalSettings((s) => ({ ...s, hotkey_healthy: key }))}
          />
          <HotkeyInput
            label="Unhealthy"
            value={localSettings.hotkey_unhealthy}
            onChange={(key) => setLocalSettings((s) => ({ ...s, hotkey_unhealthy: key }))}
          />
          <HotkeyInput
            label="Next frame"
            value={localSettings.hotkey_next}
            onChange={(key) => setLocalSettings((s) => ({ ...s, hotkey_next: key }))}
          />
          <HotkeyInput
            label="Previous frame"
            value={localSettings.hotkey_prev}
            onChange={(key) => setLocalSettings((s) => ({ ...s, hotkey_prev: key }))}
          />
        </div>

        <div className={styles.buttonRow}>
          <button className={styles.primaryButton} onClick={handleSaveSettings}>
            Save Changes
          </button>
          <button className={styles.secondaryButton} onClick={handleResetDefaults}>
            Reset to Defaults
          </button>
        </div>

        {settingsSaved && <div className={styles.success}>Settings saved</div>}
        {settingsError && <div className={styles.errorMsg}>{settingsError}</div>}
      </section>

      {/* Change Password */}
      <section className={styles.section}>
        <h3>Change Password</h3>
        <form onSubmit={handleChangePassword} className={styles.formColumn}>
          <div className={styles.field}>
            <label htmlFor="currentPassword">Current password</label>
            <input
              id="currentPassword"
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>
          <div className={styles.field}>
            <label htmlFor="newPassword">New password</label>
            <input
              id="newPassword"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              autoComplete="new-password"
              minLength={4}
              required
            />
          </div>
          <div className={styles.field}>
            <label htmlFor="confirmPassword">Confirm new password</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              autoComplete="new-password"
              required
            />
          </div>
          <button type="submit" className={styles.primaryButton} disabled={isChangingPassword}>
            {isChangingPassword ? 'Changing...' : 'Change Password'}
          </button>
          {passwordMsg && <div className={styles.success}>{passwordMsg}</div>}
          {passwordError && <div className={styles.errorMsg}>{passwordError}</div>}
        </form>
      </section>

      {/* Admin: Create User */}
      {user?.is_admin && (
        <section className={styles.section}>
          <h3>Create User</h3>
          <form onSubmit={handleCreateUser} className={styles.formColumn}>
            <div className={styles.field}>
              <label htmlFor="newUsername">Username</label>
              <input
                id="newUsername"
                type="text"
                value={newUsername}
                onChange={(e) => setNewUsername(e.target.value)}
                minLength={3}
                required
              />
            </div>
            <div className={styles.field}>
              <label htmlFor="newUserPassword">Password</label>
              <input
                id="newUserPassword"
                type="password"
                value={newUserPassword}
                onChange={(e) => setNewUserPassword(e.target.value)}
                minLength={4}
                required
              />
            </div>
            <button type="submit" className={styles.primaryButton} disabled={isCreatingUser}>
              {isCreatingUser ? 'Creating...' : 'Create User'}
            </button>
            {createUserMsg && <div className={styles.success}>{createUserMsg}</div>}
            {createUserError && <div className={styles.errorMsg}>{createUserError}</div>}
          </form>
        </section>
      )}
    </div>
  );
}

export default ProfilePage;
