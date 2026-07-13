import React from "react";
import { createRoot } from "react-dom/client";
import "./index.css";

// Minimal mount point. The real app shell (nav rail, dark theme tokens) is
// built in GRAPH-D0.4.
function App(): React.JSX.Element {
  return <div>Graphene</div>;
}

const rootEl = document.getElementById("root");
if (rootEl) {
  createRoot(rootEl).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>,
  );
}
