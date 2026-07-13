import { NavLink } from "react-router-dom";

type IconProps = { className?: string };

function GraphIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className={className}>
      <circle cx="6" cy="7" r="2.4" />
      <circle cx="18" cy="6" r="2.4" />
      <circle cx="16" cy="18" r="2.4" />
      <path strokeLinecap="round" d="M8.1 8.1l6 8.2M8 7.4l7.6-1M16.5 15.6l1-7" />
    </svg>
  );
}

function ImportIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v11m0 0l-3.5-3.5M12 14l3.5-3.5M5 18.5h14" />
    </svg>
  );
}

function ChatIcon({ className }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 6.5A2.5 2.5 0 016.5 4h11A2.5 2.5 0 0120 6.5v7a2.5 2.5 0 01-2.5 2.5H9l-4 3.5v-3.5H6.5" />
    </svg>
  );
}

const NAV_ITEMS = [
  { to: "/", label: "Explorer", Icon: GraphIcon, end: true },
  { to: "/import", label: "Import", Icon: ImportIcon, end: false },
  { to: "/chat", label: "Chat", Icon: ChatIcon, end: false },
] as const;

export function NavRail() {
  return (
    <nav className="flex h-full w-[76px] shrink-0 flex-col items-center border-r border-hairline bg-surface py-4">
      {/* Wordmark */}
      <div className="mb-6 flex h-10 w-10 items-center justify-center rounded-lg border border-hairline text-accent">
        <span className="text-lg font-semibold tracking-tight">G</span>
      </div>

      <ul className="flex flex-1 flex-col gap-1">
        {NAV_ITEMS.map(({ to, label, Icon, end }) => (
          <li key={to}>
            <NavLink
              to={to}
              end={end}
              className={({ isActive }) =>
                [
                  "group flex w-[60px] flex-col items-center gap-1 rounded-lg py-2.5 transition-colors",
                  isActive
                    ? "bg-surface-raised text-accent"
                    : "text-muted hover:bg-surface-raised hover:text-ink",
                ].join(" ")
              }
            >
              <Icon className="h-5 w-5" />
              <span className="text-[10px] font-medium tracking-wide">{label}</span>
            </NavLink>
          </li>
        ))}
      </ul>

      {/* Connection status marker */}
      <div className="mt-auto flex flex-col items-center gap-1 text-muted">
        <span className="h-1.5 w-1.5 rounded-full bg-risk-low" />
        <span className="text-[9px] tracking-wide">v0.1</span>
      </div>
    </nav>
  );
}
