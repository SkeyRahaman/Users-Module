import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import Button from '../components/ui/Button.jsx';

export default function UnauthorizedPage() {
  const navigate = useNavigate();

  return (
    <div className="unauthorized-page animate-fade-in">
      <div className="unauthorized-code">403</div>
      <div className="confirm-icon danger" style={{ width: 64, height: 64, marginBottom: 0 }}>
        <ShieldAlert size={32} />
      </div>
      <h1 className="unauthorized-title">Access Restricted</h1>
      <p className="unauthorized-desc">
        Your security clearance lacks the specific permission scopes required to access this dashboard console resource.
      </p>
      <Button onClick={() => navigate('/dashboard')} style={{ gap: '0.4rem', marginTop: '1rem' }}>
        <ArrowLeft size={16} /> Return to Dashboard
      </Button>
    </div>
  );
}
