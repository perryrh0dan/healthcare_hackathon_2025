import {
  createRouter,
  createRootRoute,
  createRoute,
} from '@tanstack/react-router';
import App from '../App';
import DailyQuestions from '../views/DailyQuestions';
import FoodPlanner from '../views/FoodPlanner';
import Home from '../views/Home';
import RegisterScreen from '../views/RegisterScreen';
import SetupScreen from '../views/SetupScreen';
import LoginScreen from '@/views/LoginScreen';
import ProtectedRoute from '../components/ProtectedRoute';

const rootRoute = createRootRoute({
  component: App,
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: () => (
    <ProtectedRoute>
      <Home />
    </ProtectedRoute>
  ),
});

const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/home',
  component: () => (
    <ProtectedRoute>
      <Home />
    </ProtectedRoute>
  ),
});

const dailyQuestionsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/daily',
  component: () => (
    <ProtectedRoute route="daily">
      <DailyQuestions />
    </ProtectedRoute>
  ),
});

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/login',
  component: LoginScreen,
});

const registerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/register',
  component: RegisterScreen,
});

const setupRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/setup',
  component: () => (
    <ProtectedRoute route="setup">
      <SetupScreen />
    </ProtectedRoute>
  ),
});

const foodPlannerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/food-planner',
  component: () => (
    <ProtectedRoute>
      <FoodPlanner />
    </ProtectedRoute>
  ),
});

const routeTree = rootRoute.addChildren([
  indexRoute,
  homeRoute,
  dailyQuestionsRoute,
  loginRoute,
  registerRoute,
  setupRoute,
  foodPlannerRoute,
]);

export const router = createRouter({ routeTree });

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
