type ConfidenceToggleProps = {
  checked: boolean;
  onChange: (checked: boolean) => void;
  /** Shift left when the node drawer is open so it stays on the visible canvas. */
  drawerOpen?: boolean;
};

export function ConfidenceToggle({ checked, onChange, drawerOpen = false }: ConfidenceToggleProps) {
  return (
    <div
      className={[
        "absolute top-4 z-10 flex items-center gap-2.5 rounded-lg border border-hairline bg-surface px-3 py-2 transition-all duration-300",
        drawerOpen ? "right-[376px]" : "right-4",
      ].join(" ")}
    >
      <span className="text-xs font-medium text-ink">Show inferred relationships</span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        aria-label="Show inferred relationships"
        onClick={() => onChange(!checked)}
        className={[
          "relative h-5 w-9 shrink-0 rounded-full transition-colors",
          checked ? "bg-accent" : "border border-hairline bg-surface-raised",
        ].join(" ")}
      >
        <span
          className={[
            "absolute top-0.5 h-4 w-4 rounded-full bg-ink transition-transform",
            checked ? "translate-x-4" : "translate-x-0.5",
          ].join(" ")}
        />
      </button>
    </div>
  );
}
