import { createRouter, createWebHistory } from "vue-router";

import { useAuthStore } from "../stores/auth";
import AppLayout from "../views/AppLayout.vue";
import DashboardView from "../views/DashboardView.vue";
import FormulasView from "../views/FormulasView.vue";
import HerbsView from "../views/HerbsView.vue";
import InventoryView from "../views/InventoryView.vue";
import LoginView from "../views/LoginView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "login",
      component: LoginView,
      meta: { guest: true },
    },
    {
      path: "/",
      redirect: "/app/dashboard",
    },
    {
      path: "/app",
      component: AppLayout,
      meta: { auth: true },
      children: [
        {
          path: "dashboard",
          name: "dashboard",
          component: DashboardView,
          meta: { auth: true, permission: "dashboard.view" },
        },
        {
          path: "herbs",
          name: "herbs",
          component: HerbsView,
          meta: { auth: true, permission: "herb.view" },
        },
        {
          path: "formulas",
          name: "formulas",
          component: FormulasView,
          meta: { auth: true, permission: "formula.view" },
        },
        {
          path: "inventory",
          name: "inventory",
          component: InventoryView,
          meta: { auth: true, permission: "inventory.view" },
        },
      ],
    },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();

  if (auth.isAuthenticated && !auth.user) {
    try {
      await auth.safeBootstrap();
    } catch {
      if (to.name !== "login") return { name: "login" };
      return true;
    }
  }

  if (to.meta.auth && !auth.isAuthenticated) {
    return { name: "login" };
  }
  if (to.meta.guest && auth.isAuthenticated) {
    return { name: "dashboard" };
  }
  if (to.meta.permission && !auth.hasPermission(to.meta.permission)) {
    const firstMenuPath = auth.menu[0]?.path || "/app/dashboard";
    return firstMenuPath;
  }
  return true;
});

export default router;
