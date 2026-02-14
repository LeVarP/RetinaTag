import { useState } from 'react';
import styles from './CookieConsent.module.css';

function CookieConsent() {
  const [visible, setVisible] = useState(
    () => !localStorage.getItem('cookie-consent')
  );

  if (!visible) return null;

  const handleAccept = () => {
    localStorage.setItem('cookie-consent', 'true');
    setVisible(false);
  };

  return (
    <div className={styles.banner}>
      <p className={styles.text}>
        This application uses cookies for authentication purposes only. No tracking or analytics cookies are used.
      </p>
      <button className={styles.acceptButton} onClick={handleAccept}>
        I Understand
      </button>
    </div>
  );
}

export default CookieConsent;
