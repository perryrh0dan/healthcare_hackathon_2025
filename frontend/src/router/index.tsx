import {
  createRouter,
  createRootRoute,
  createRoute,
} from '@tanstack/react-router';
import App from '../App';
import DailyQuestions from '../views/DailyQuestions';
import LoginScreen from '../views/LoginScreen';
import RegisterScreen from '../views/RegisterScreen';

const rootRoute = createRootRoute({
  component: App,
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: () => (
    <div style={{ padding: '2rem' }}>
      <h1>Willkommen bei der Healthcare App</h1>
      <p>Wählen Sie eine Option aus der Navigation</p>
    </div>
  ),
});

const dailyQuestionsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/daily',
  component: DailyQuestions,
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

const routeTree = rootRoute.addChildren([
  indexRoute,
  dailyQuestionsRoute,
  loginRoute,
  registerRoute,
]);

export const router = createRouter({ routeTree });

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
