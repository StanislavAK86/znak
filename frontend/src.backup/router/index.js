import { createRouter, createWebHistory } from 'vue-router'
import CircleEditor from '../components/CircleEditor.vue'
import ProfilePage from '../components/ProfilePage.vue'
import { useAuthStore } from '../stores/authStore'

const routes = [
  {
    path: '/',
    redirect: '/editor'
  },
  {
    path: '/editor',
    name: 'Editor',
    component: CircleEditor
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfilePage,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Проверяем токен при загрузке
  if (authStore.token && !authStore.user) {
    await authStore.fetchUser()
  }
  
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      next('/editor')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router