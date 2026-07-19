import { useEffect, useRef, useState } from 'react';

export default function Dropdown({ trigger, children, align = 'right' }) {
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div className="dropdown-wrapper" ref={wrapperRef}>
      <div onClick={() => setIsOpen((o) => !o)}>{trigger}</div>
      {isOpen && (
        <div
          className="dropdown-menu"
          style={align === 'left' ? { right: 'auto', left: 0 } : {}}
          onClick={() => setIsOpen(false)}
        >
          {children}
        </div>
      )}
    </div>
  );
}

export function DropdownItem({ children, onClick, danger = false, icon }) {
  return (
    <div className={`dropdown-item${danger ? ' danger' : ''}`} onClick={onClick}>
      {icon && icon}
      {children}
    </div>
  );
}
