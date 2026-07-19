import { Search } from 'lucide-react';

export default function SearchBar({ value, onChange, placeholder = 'Search…', className = '' }) {
  return (
    <div className={`search-bar ${className}`}>
      <Search size={16} className="search-bar-icon" />
      <input
        className="form-input"
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
      />
    </div>
  );
}
