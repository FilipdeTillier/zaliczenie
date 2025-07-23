import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { AppRouter } from "./router";
import { Provider } from "react-redux";
import { store } from "./store";

const queryClient = new QueryClient();

function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <AppRouter />
      </QueryClientProvider>
    </Provider>
  );
}

export default App;
