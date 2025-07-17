import { CHAT, MAIN } from "./appPaths";
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";

import { Chat } from "../pages/Chat";
import { Home } from "../pages/Home";
import { Navigation } from "../components/molecules/Navigation";

export const AppRouter = () => (
  <Router>
    <Navigation />
    <Routes>
      <Route path={MAIN} element={<Home />} />
      <Route
        path={CHAT}
        element={
          <div className="card">
            <Chat />
          </div>
        }
      />
    </Routes>
  </Router>
);
