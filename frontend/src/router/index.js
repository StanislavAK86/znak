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
    component: CircleEditor,
    meta: {
      title: 'Конструктор значков онлайн | Создать макет для печати от 25 до 75 мм',
      description: 'Бесплатный онлайн-конструктор значков. Выбирайте размер от 25 до 75 мм, добавляйте изображения, скачивайте PDF для типографии. Без регистрации.'
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfilePage,
    meta: { 
      requiresAuth: true,
      title: 'Мои проекты значков | Личный кабинет',
      description: 'Сохранённые проекты значков. Продолжите редактирование или скачайте готовые макеты в PDF.'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// ========== НОВЫЙ ХУК ДЛЯ SEO (ДОБАВЛЯЕМ) ==========
// Функция для обновления мета-тегов
function updateMetaTags(title, description) {
  // Обновляем заголовок страницы
  if (title) {
    document.title = title
  }
  
  // Обновляем или создаём meta description
  let metaDescription = document.querySelector('meta[name="description"]')
  if (description) {
    if (metaDescription) {
      metaDescription.setAttribute('content', description)
    } else {
      const meta = document.createElement('meta')
      meta.name = 'description'
      meta.content = description
      document.head.appendChild(meta)
    }
  }
}

// Глобальный хук для смены заголовков при переходе
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Проверяем токен при загрузке
  if (authStore.token && !authStore.user) {
    await authStore.fetchUser()
  }
  
  // ========== SEO: Устанавливаем заголовки ДО проверки авторизации ==========
  if (to.meta.title) {
    updateMetaTags(to.meta.title, to.meta.description)
  } else {
    // Заголовок по умолчанию, если для маршрута не указан
    updateMetaTags('Конструктор значков онлайн', 'Создайте макет значков для печати. Бесплатно, без регистрации.')
  }
  
  // ========== ВАША СУЩЕСТВУЮЩАЯ ЛОГИКА АВТОРИЗАЦИИ (НЕ ТРОГАЕМ) ==========
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