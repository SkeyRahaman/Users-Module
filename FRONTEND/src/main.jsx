import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';

// Import CSS Stylesheet cascade in priority order
import './styles/index.css';
import './styles/layout.css';
import './styles/components.css';
import './styles/auth.css';
import './styles/dashboard.css';
import './styles/pages.css';
import './styles/animations.css';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
);
