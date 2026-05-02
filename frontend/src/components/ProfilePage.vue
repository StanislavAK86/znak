<template>
  <div class="profile-page">
    <div class="profile-header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">← Назад</button>
        <h1>Мои проекты</h1>
        <div class="user-info">
          <span class="username">{{ user?.username || 'Гость' }}</span>
          <button class="new-project-btn" @click="createNewProject">➕ Новый проект</button>
          <button class="logout-btn" @click="logout">Выйти</button>
        </div>
      </div>
    </div>

    <div class="projects-container">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Загрузка проектов...</p>
      </div>
      
      <div v-else-if="projects.length === 0" class="empty-projects">
        <div class="empty-icon">📁</div>
        <h3>У вас пока нет проектов</h3>
        <p>Создайте свой первый значок в конструкторе</p>
        <button class="create-btn" @click="goToEditor">Создать проект</button>
      </div>
      
      <div v-else class="projects-grid">
        <div 
          v-for="project in projects" 
          :key="project.id"
          class="project-card"
        >
          <div class="project-preview" @click="openProject(project)">
            <div class="preview-circle" :style="getPreviewStyle(project)">
              <div v-if="!getPreviewImage(project)" class="preview-placeholder">
                {{ getShapeIcon(project.shape_type) }}
              </div>
            </div>
          </div>
          
          <div class="project-details" @click="openProject(project)">
            <h3>{{ project.name }}</h3>
            <div class="project-meta">
              <span class="badge">{{ project.diameter_mm }} мм</span>
              <span class="badge">{{ project.orientation === 'landscape' ? 'Альбомная' : 'Портретная' }}</span>
              <span class="badge">{{ getShapeLabel(project.shape_type) }}</span>
            </div>
            <div class="project-date">
              📅 {{ formatDate(project.updated_at) }}
            </div>
            <div class="project-stats">
              <span>🎨 {{ getImagesCount(project) }} изображений</span>
            </div>
          </div>
          
          <div class="project-actions">
            <button class="action-btn edit" @click="editProject(project)" title="Редактировать">
              ✏️
            </button>
            <!-- <button class="action-btn download" @click="downloadProjectPDF(project)" title="Скачать PDF">
              📄 
            </button>-->
            <button class="action-btn delete" @click="deleteProject(project)" title="Удалить">
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно подтверждения удаления -->
    <div v-if="showDeleteModal" class="modal" @click.self="showDeleteModal = false">
      <div class="modal-content">
        <h3>Удалить проект?</h3>
        <p>Вы уверены, что хотите удалить проект "{{ projectToDelete?.name || '' }}"?</p>
        <p class="warning">Это действие нельзя отменить.</p>
        <div class="modal-buttons">
          <button class="btn-cancel" @click="showDeleteModal = false">Отмена</button>
          <button class="btn-danger" @click="confirmDelete">Удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '../stores/authStore'
import { useBadgeStore } from '../stores/badgeStore'

export default {
  name: 'ProfilePage',
  data() {
    return {
      projects: [],
      loading: true,
      showDeleteModal: false,
      projectToDelete: null
    }
  },
  computed: {
    user() {
      const authStore = useAuthStore()
      return authStore.user
    }
  },
  async mounted() {
    await this.checkAuthAndLoad()
  },
  methods: {
    async checkAuthAndLoad() {
      const authStore = useAuthStore()
      
      if (!authStore.isAuthenticated) {
        this.$router.push('/editor')
        return
      }
      
      await this.loadProjects()
    },
    
    async loadProjects() {
      this.loading = true
      const badgeStore = useBadgeStore()
      await badgeStore.loadProjects()
      this.projects = badgeStore.projects
      console.log('Загружено проектов:', this.projects.length)
      this.loading = false
    },
    
    getPreviewImage(project) {
      const shapesData = project.shapes_data || {}
      const firstKey = Object.keys(shapesData)[0]
      return shapesData[firstKey]
    },
    
    getPreviewStyle(project) {
      const previewImage = this.getPreviewImage(project)
      if (previewImage && typeof previewImage === 'string') {
        return {
          backgroundImage: `url(${previewImage})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }
      }
      return {}
    },
    
    getShapeLabel(shapeType) {
      const shapes = {
        circle: 'Круг',
        square: 'Квадрат',
        star: 'Звезда',
        shield: 'Щит',
        heart: 'Сердце',
        oval: 'Овал',
        hexagon: 'Шестиугольник',
        cross: 'Крест'
      }
      return shapes[shapeType] || 'Круг'
    },
    
    getShapeIcon(shapeType) {
      const icons = {
        circle: '○',
        square: '□',
        star: '★',
        shield: '🛡️',
        heart: '❤️',
        oval: '⬭',
        hexagon: '⬡',
        cross: '✝️'
      }
      return icons[shapeType] || '○'
    },
    
    getImagesCount(project) {
      const count = Object.keys(project.shapes_data || {}).length
      return count
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Дата неизвестна'
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return 'Дата неизвестна'
      return date.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    goBack() {
      this.$router.push('/editor')
    },
    
    goToEditor() {
      this.$router.push('/editor')
    },
    
    createNewProject() {
      const badgeStore = useBadgeStore()
      badgeStore.createNewProject()
      this.$router.push('/editor')
    },
    
    openProject(project) {
      const badgeStore = useBadgeStore()
      
      // Загружаем данные проекта в store
      badgeStore.currentProject = project
      badgeStore.currentDiameter = project.diameter_mm
      badgeStore.currentOrientation = project.orientation
      badgeStore.images = project.shapes_data || {}
      
      console.log('Загружен проект:', project.name, 'с изображениями:', Object.keys(project.shapes_data || {}).length)
      
      this.$router.push('/editor')
    },
    
    editProject(project) {
      this.openProject(project)
    },
    
    async downloadProjectPDF(project) {
      const badgeStore = useBadgeStore()
      const result = await badgeStore.generatePDF(project.id)
      if (!result.success) {
        alert('Ошибка при генерации PDF: ' + (result.error || 'Неизвестная ошибка'))
      }
    },
    
    deleteProject(project) {
      this.projectToDelete = project
      this.showDeleteModal = true
    },
    
    async confirmDelete() {
      if (this.projectToDelete) {
        const badgeStore = useBadgeStore()
        await badgeStore.deleteProject(this.projectToDelete.id)
        await this.loadProjects()
        this.showDeleteModal = false
        this.projectToDelete = null
      }
    },
    
    logout() {
      const authStore = useAuthStore()
      authStore.logout()
      this.$router.push('/editor')
    }
  }
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.profile-header {
  background: white;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.back-btn {
  background: #f0f0f0;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #e0e0e0;
}

.profile-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #333;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.username {
  font-weight: 500;
  color: #4CAF50;
}

.new-project-btn {
  background: #00BCD4;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.new-project-btn:hover {
  background: #0097A7;
}

.logout-btn {
  background: #f44336;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.logout-btn:hover {
  background: #da190b;
}

.projects-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.loading {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 16px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-projects {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 16px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-projects h3 {
  font-size: 1.5rem;
  margin-bottom: 10px;
  color: #333;
}

.empty-projects p {
  color: #666;
  margin-bottom: 24px;
}

.create-btn {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.create-btn:hover {
  background: #45a049;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.project-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

.project-preview {
  height: 180px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

.preview-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.preview-placeholder {
  font-size: 48px;
}

.project-details {
  padding: 16px;
  cursor: pointer;
}

.project-details h3 {
  margin: 0 0 10px 0;
  font-size: 1.1rem;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.badge {
  background: #f0f0f0;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  color: #666;
}

.project-date {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}

.project-stats {
  font-size: 12px;
  color: #666;
}

.project-actions {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #eee;
  background: #fafafa;
}

.action-btn {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}

.action-btn.edit {
  background: #2196F3;
  color: white;
}

.action-btn.edit:hover {
  background: #0b7dda;
}

.action-btn.download {
  background: #4CAF50;
  color: white;
}

.action-btn.download:hover {
  background: #45a049;
}

.action-btn.delete {
  background: #f44336;
  color: white;
}

.action-btn.delete:hover {
  background: #da190b;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 16px;
  max-width: 400px;
  width: 90%;
  text-align: center;
}

.modal-content h3 {
  margin: 0 0 16px 0;
}

.modal-content .warning {
  color: #f44336;
  font-size: 12px;
  margin-top: 8px;
}

.modal-buttons {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel, .btn-danger {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.btn-cancel {
  background: #e0e0e0;
  color: #333;
}

.btn-cancel:hover {
  background: #d0d0d0;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-danger:hover {
  background: #da190b;
}
</style>