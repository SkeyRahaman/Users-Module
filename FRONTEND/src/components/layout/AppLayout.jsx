import { useState, useEffect, useRef } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar.jsx';
import Topbar from './Topbar.jsx';
import { healthApi } from '../../api/permissions.js';
import { AlertCircle, RefreshCw, Sparkles, X, Copy, Check } from 'lucide-react';

/** Demo mode banner — survives the auto-login redirect for 15 s */
function DemoBanner({ onDismiss }) {
  const [visible, setVisible] = useState(true);
  const [copied, setCopied] = useState(null);
  const timerRef = useRef(null);

  useEffect(() => {
    timerRef.current = setTimeout(() => {
      setVisible(false);
      onDismiss?.();
    }, 15000);
    return () => clearTimeout(timerRef.current);
  }, [onDismiss]);

  const handleDismiss = () => {
    clearTimeout(timerRef.current);
    setVisible(false);
    onDismiss?.();
  };

  const copyToClipboard = async (text, type) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(type);
      setTimeout(() => setCopied(null), 1500);
    } catch { /* ignore */ }
  };

  if (!visible) return null;

  return (
    <div className="demo-banner animate-slide-down">
      <div className="demo-banner-icon"><Sparkles size={16} /></div>
      <div className="demo-banner-body">
        <p className="demo-banner-title">Demo Mode — You're automatically signed in</p>
        <p className="demo-banner-text">
          This is a portfolio demo. No account needed — we've logged you in as{' '}
          <strong>admin</strong> so you can explore everything right away.
        </p>
        <div className="demo-banner-creds">
          <span className="demo-cred-chip">
            <span className="demo-cred-label">user</span>
            <code>admin</code>
            <button className="demo-cred-copy" onClick={() => copyToClipboard('admin', 'user')} title="Copy username">
              {copied === 'user' ? <Check size={11} /> : <Copy size={11} />}
            </button>
          </span>
          <span className="demo-cred-chip">
            <span className="demo-cred-label">pass</span>
            <code>adminpassword</code>
            <button className="demo-cred-copy" onClick={() => copyToClipboard('adminpassword', 'pass')} title="Copy password">
              {copied === 'pass' ? <Check size={11} /> : <Copy size={11} />}
            </button>
          </span>
        </div>
      </div>
      <button className="demo-banner-close" onClick={handleDismiss} title="Dismiss">
        <X size={14} />
      </button>
    </div>
  );
}

export default function AppLayout() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isBackendWarmingUp, setIsBackendWarmingUp] = useState(false);
  const [warmingProgress, setWarmingProgress] = useState(0);
  const [warningError, setWarningError] = useState(false);
  const [showDemoBanner, setShowDemoBanner] = useState(false);

  useEffect(() => {
    if (sessionStorage.getItem('show_demo_banner') === 'true') {
      setShowDemoBanner(true);
    }
  }, []);

  // Close mobile sidebar on resize to desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 768) {
        setIsMobileOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    let checkInterval;
    let progressInterval;
    let hasResponded = false;

    const pingBackend = async () => {
      try {
        const res = await healthApi.check();
        if (res && (res.status === 'ok' || res.status === 'HEALTHY')) {
          hasResponded = true;
          setIsBackendWarmingUp(false);
          clearInterval(checkInterval);
          clearInterval(progressInterval);
        }
      } catch (err) {
        // Backend didn't respond or is spinning up
        if (!hasResponded) {
          setIsBackendWarmingUp(true);
        }
      }
    };

    // Initial ping
    pingBackend();

    // Start checking every 3 seconds
    checkInterval = setInterval(() => {
      if (!hasResponded) {
        pingBackend();
      }
    }, 3000);

    // Timeout fallback after 50 seconds to stop loading/progress
    const timeoutId = setTimeout(() => {
      if (!hasResponded) {
        clearInterval(checkInterval);
        clearInterval(progressInterval);
        setWarningError(true);
      }
    }, 50000);

    // Progress bar animation simulation
    progressInterval = setInterval(() => {
      setWarmingProgress((prev) => {
        if (prev >= 98) return prev;
        return prev + 1;
      });
    }, 450);

    return () => {
      clearInterval(checkInterval);
      clearInterval(progressInterval);
      clearTimeout(timeoutId);
    };
  }, []);

  return (
    <div className={`app-container ${isCollapsed ? 'sidebar-collapsed' : ''}`}>
      {/* Mobile sidebar backdrop */}
      {isMobileOpen && (
        <div
          className="sidebar-mobile-backdrop"
          onClick={() => setIsMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      <Sidebar
        isCollapsed={isCollapsed}
        onToggle={() => setIsCollapsed(!isCollapsed)}
        isMobileOpen={isMobileOpen}
        onMobileClose={() => setIsMobileOpen(false)}
      />
      <Topbar onMobileMenuToggle={() => setIsMobileOpen(!isMobileOpen)} />
      <main className="main-content">
        {showDemoBanner && (
          <div style={{ marginBottom: '1.25rem' }}>
            <DemoBanner
              onDismiss={() => {
                sessionStorage.removeItem('show_demo_banner');
                setShowDemoBanner(false);
              }}
            />
          </div>
        )}
        <Outlet />
      </main>

      {/* Cold Start Overlay Modal */}
      {isBackendWarmingUp && (
        <div className="cold-start-overlay">
          <div className="cold-start-card">
            <div className="cold-start-icon">
              <RefreshCw className="animate-spin" size={32} style={{ color: 'var(--accent)' }} />
            </div>
            <h3 className="cold-start-title">Warming Up Backend Server</h3>
            <p className="cold-start-desc">
              We host our backend on a free Render tier. It goes to sleep due to inactivity, and cold starts can take up to 50 seconds. Thanks for your patience!
            </p>
            <div className="cold-start-progress-bg">
              <div className="cold-start-progress-bar" style={{ width: `${warmingProgress}%` }} />
            </div>
            <span className="cold-start-percentage">{warmingProgress}%</span>

            {warningError && (
              <div className="cold-start-warning">
                <AlertCircle size={16} />
                <span>The backend is taking longer than expected to respond. Please refresh the page.</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
