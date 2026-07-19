import { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar.jsx';
import Topbar from './Topbar.jsx';
import { healthApi } from '../../api/permissions.js';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function AppLayout() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isBackendWarmingUp, setIsBackendWarmingUp] = useState(false);
  const [warmingProgress, setWarmingProgress] = useState(0);
  const [warningError, setWarningError] = useState(false);

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
