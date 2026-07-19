import { Settings2 } from 'lucide-react';
import '../../styles/auth.css'; // Just in case, though it's usually globally loaded or loaded by page

export default function MobileAuthHeader() {
  return (
    <div className="mobile-auth-header">
      <div className="auth-logo">
        <div className="auth-logo-mark">
          <Settings2 size={24} />
        </div>
        <span className="auth-logo-text">Users_Module</span>
      </div>
      <h2 className="mobile-auth-subtitle">Identity & Access Management</h2>
    </div>
  );
}
