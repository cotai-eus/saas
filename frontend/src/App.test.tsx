import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import HomePage from "./pages/HomePage";

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  const router = createBrowserRouter([
    { path: "/", element: ui },
  ]);
  return render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  );
}

describe("App", () => {
  it("renders the home page", () => {
    renderWithProviders(<HomePage />);
    expect(screen.getByText("Comunicação em escala")).toBeDefined();
  });

  it("renders feature cards", () => {
    renderWithProviders(<HomePage />);
    expect(screen.getByText("Campanhas em massa")).toBeDefined();
    expect(screen.getByText("Automações inteligentes")).toBeDefined();
    expect(screen.getByText("Relatórios em tempo real")).toBeDefined();
  });
});
