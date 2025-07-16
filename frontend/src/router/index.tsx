import { CHAT, MAIN } from "./appPaths";
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";

import ChatWindow from "../../components/molecules/chatWindow/chatWindow";
import { ModelSelector } from "../components/ModelSelector";

export const AppRouter = () => (
  <Router>
    <Routes>
      <Route
        path={MAIN}
        element={<ModelSelector onModelChanged={() => {}} />}
      />
      <Route
        path={CHAT}
        element={
          <div className="card">
            <ChatWindow />
          </div>
        }
      />
    </Routes>
  </Router>
);
