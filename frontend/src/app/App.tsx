import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./AppLayout";
import { GraphExplorerPage } from "../features/graph-explorer/GraphExplorerPage";
import { ImportPage } from "../features/import/ImportPage";
import { ChatPage } from "../features/ai-chat/ChatPage";

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<GraphExplorerPage />} />
          <Route path="import" element={<ImportPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
