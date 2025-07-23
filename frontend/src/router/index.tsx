import { Route, BrowserRouter as Router, Routes } from "react-router-dom";

import { AppLayout } from "../components/Layout/AppLayout";
import { MAIN } from "./appPaths";

export const AppRouter = () => (
  <Router>
    <Routes>
      <Route path={MAIN} element={<AppLayout />} />
    </Routes>
  </Router>
);
