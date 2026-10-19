import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { LayoutGrid, Settings2 } from 'lucide-react';
import { hapticImpact } from '@/lib/telegram';
import './BottomNav.css';

const NAV_ITEMS = [
  { to: '/', label: 'Channels', icon: LayoutGrid, exactMatch: true },
  { to: '/settings', label: 'Settings', icon: Settings2, exactMatch: false },
] as const;

export function BottomNav() {
  const location = useLocation();

  return (
    <nav className="bottom-nav" aria-label="Main navigation">
      <div className="bottom-nav__pill">
        {NAV_ITEMS.map(({ to, label, icon: Icon, exactMatch }) => {
          const isActive = exactMatch
            ? location.pathname === to
            : location.pathname.startsWith(to);

          return (
            <NavLink
              key={to}
              to={to}
              className={['bottom-nav__item', isActive ? 'bottom-nav__item--active' : ''].join(' ')}
              onClick={() => hapticImpact('light')}
              aria-current={isActive ? 'page' : undefined}
            >
              <span className="bottom-nav__icon">
                <Icon size={20} strokeWidth={isActive ? 2.2 : 1.7} />
              </span>
              <span className="bottom-nav__label">{label}</span>
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
}
