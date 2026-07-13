import { Outlet } from "react-router-dom";
import { NavRail } from "./NavRail";

export function AppLayout() {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-canvas font-sans text-ink">
      <NavRail />
      <main className="bg-grid relative flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}
