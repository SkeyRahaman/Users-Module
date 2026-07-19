import { useState } from 'react';

export default function Tabs({ tabs, defaultTab, className = '' }) {
  const [active, setActive] = useState(defaultTab ?? tabs[0]?.id);

  const currentTab = tabs.find((t) => t.id === active);

  return (
    <div className={className}>
      <div className="tabs-header">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab-btn ${active === tab.id ? 'active' : ''}`}
            onClick={() => setActive(tab.id)}
          >
            {tab.icon && tab.icon}
            {tab.label}
            {tab.badge != null && (
              <span
                className="badge badge-gray"
                style={{ fontSize: '0.7rem', padding: '0.15rem 0.5rem' }}
              >
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>
      <div className="animate-fade-in">{currentTab?.content}</div>
    </div>
  );
}
