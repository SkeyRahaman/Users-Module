import { useNavigate } from 'react-router-dom';
import { HelpCircle, ArrowLeft } from 'lucide-react';
import Button from '../components/ui/Button.jsx';

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="unauthorized-page animate-fade-in">
      <div className="unauthorized-code" style={{ background: 'linear-gradient(135deg, var(--accent), var(--info))', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
        404
      </div>
      <div className="confirm-icon info" style={{ width: 64, height: 64, marginBottom: 0 }}>
        <HelpCircle size={32} />
      </div>
      <h1 className="unauthorized-title">Page Not Found</h1>
      <p className="unauthorized-desc">
        The console dashboard link you requested is invalid or has been relocated to another path directory.
      </p>
      <Button onClick={() => navigate('/dashboard')} style={{ gap: '0.4rem', marginTop: '1rem' }}>
        <ArrowLeft size={16} /> Return to Dashboard
      </Button>
    </div>
  );
}
