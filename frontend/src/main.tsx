import { StrictMode, lazy, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { FullPageSpinner } from "./shared/components/ui/Spinner";
import { AuthGuard } from "./shared/components/ui/AuthGuard";
import { ErrorBoundary } from "./App";
import { ToastContainer } from "./shared/components/ui";
import "./styles/global.css";

const AuthLayout = lazy(() => import("./layouts/AuthLayout"));
const AppLayout = lazy(() => import("./layouts/AppLayout/AppLayout"));
const HomePage = lazy(() => import("./pages/HomePage"));
const LoginPage = lazy(() => import("./pages/auth/LoginPage"));
const RegisterPage = lazy(() => import("./pages/auth/RegisterPage"));
const ForgotPasswordPage = lazy(() => import("./pages/auth/ForgotPasswordPage"));
const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const CampaignsPage = lazy(() => import("./pages/CampaignsPage"));
const CampaignNewPage = lazy(() => import("./pages/CampaignNewPage"));
const CampaignDetailPage = lazy(() => import("./pages/CampaignDetailPage"));
const ContactsPage = lazy(() => import("./pages/ContactsPage"));
const ContactDetailPage = lazy(() => import("./pages/ContactDetailPage"));
const AutomationsPage = lazy(() => import("./pages/AutomationsPage"));
const SchedulesPage = lazy(() => import("./pages/SchedulesPage"));
const ReportsPage = lazy(() => import("./pages/ReportsPage"));
const SettingsPage = lazy(() => import("./pages/SettingsPage"));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const router = createBrowserRouter([
  {
    path: "/",
    element: <HomePage />,
  },
  {
    path: "/auth",
    element: <Suspense fallback={<FullPageSpinner />}><AuthLayout /></Suspense>,
    children: [
      { index: true, element: <Navigate to="login" replace /> },
      { path: "login", element: <Suspense fallback={<FullPageSpinner />}><LoginPage /></Suspense> },
      { path: "register", element: <Suspense fallback={<FullPageSpinner />}><RegisterPage /></Suspense> },
      { path: "forgot-password", element: <Suspense fallback={<FullPageSpinner />}><ForgotPasswordPage /></Suspense> },
    ],
  },
  {
    element: (
      <AuthGuard>
        <Suspense fallback={<FullPageSpinner />}>
          <AppLayout />
        </Suspense>
      </AuthGuard>
    ),
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: "dashboard", element: <Suspense fallback={<FullPageSpinner />}><DashboardPage /></Suspense> },
      { path: "campaigns", element: <Suspense fallback={<FullPageSpinner />}><CampaignsPage /></Suspense> },
      { path: "campaigns/new", element: <Suspense fallback={<FullPageSpinner />}><CampaignNewPage /></Suspense> },
      { path: "campaigns/:id", element: <Suspense fallback={<FullPageSpinner />}><CampaignDetailPage /></Suspense> },
      { path: "contacts", element: <Suspense fallback={<FullPageSpinner />}><ContactsPage /></Suspense> },
      { path: "contacts/:id", element: <Suspense fallback={<FullPageSpinner />}><ContactDetailPage /></Suspense> },
      { path: "automations", element: <Suspense fallback={<FullPageSpinner />}><AutomationsPage /></Suspense> },
      { path: "schedules", element: <Suspense fallback={<FullPageSpinner />}><SchedulesPage /></Suspense> },
      { path: "reports", element: <Suspense fallback={<FullPageSpinner />}><ReportsPage /></Suspense> },
      { path: "settings", element: <Suspense fallback={<FullPageSpinner />}><SettingsPage /></Suspense> },
    ],
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
        <ToastContainer />
      </QueryClientProvider>
    </ErrorBoundary>
  </StrictMode>,
);
