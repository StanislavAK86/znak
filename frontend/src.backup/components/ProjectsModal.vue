<template>
  <div v-if="show" class="modal-overlay" @click="close">
    <div class="modal-container modal-large" @click.stop>
      <div class="modal-header">
        <h3>Мои проекты</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      
      <div class="modal-body-projects">
        <div v-if="loading" class="loading">
          Загрузка...
        </div>
        
        <div v-else-if="projects.length === 0" class="empty">
          <p>У вас пока нет сохранённых проектов</p>
          <button class="btn-create" @click="createNewProject">Создать новый</button>
        </div>
        
        <div v-else class="projects-list">
          <div 
            v-for="project in projects" 
            :key="project.id"
            class="project-item"
          >
            <div class="project-icon">
              <span class="icon">🎨</span>
            </div>
            <div class="project-info" @click="loadProject(project)">
              <h4>{{ project.name }}</h4>
              <p>{{ project.diameter_mm }} мм · {{ project.orientation === 'landscape' ? 'Альбомная' : 'Портретная' }}</p>
              <p class="date">{{ formatDate(project.updated_at) }}</p>
            </div>
            <div class="project-actions">
              <button class="action-btn load" @click="loadProject(project)" title="Загрузить">📂</button>
              <button class="action-btn delete" @click="confirmDelete(project)" title="Удалить">🗑️</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useBadgeStore } from '../stores/badgeStore'

export default {
  name: 'ProjectsModal',
  props: {
    show: Boolean
  },
  emits: ['close', 'load-project'],
  data() {
    return {
      loading: false
    }
  },
  computed: {
    projects() {
      const badgeStore = useBadgeStore()
      return badgeStore.projects
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return 'Дата неизвестна'
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return 'Дата неизвестна'
      return date.toLocaleDateString('ru-RU') + ' ' + date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
    },
    
    async loadProject(project) {
      const badgeStore = useBadgeStore()
      
      // Загружаем проект в store
      badgeStore.currentProject = project
      badgeStore.currentDiameter = project.diameter_mm
      badgeStore.currentOrientation = project.orientation
      badgeStore.images = project.shapes_data || {}
      
      this.$emit('load-project', project)
      this.close()
    },
    
    createNewProject() {
      const badgeStore = useBadgeStore()
      badgeStore.createNewProject()
      this.close()
      this.$router.push('/editor')
    },
    
    async confirmDelete(project) {
      if (confirm(`Удалить проект "${project.name}"?`)) {
        const badgeStore = useBadgeStore()
        await badgeStore.deleteProject(project.id)
      }
    },
    
    close() {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-container {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.modal-large {
  max-width: 600px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 24px;
  border-bottom: 1px solid #e5e5e5;
  background: #fafafa;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #222;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #999;
  transition: all 0.2s;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.close-btn:hover {
  color: #333;
  background: #f0f0f0;
}

.modal-body-projects {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #666;
}

.btn-create {
  padding: 8px 20px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 10px;
}

.projects-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.project-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 10px;
  transition: all 0.2s;
}

.project-item:hover {
  background: #f0f0f0;
}

.project-icon .icon {
  font-size: 32px;
}

.project-info {
  flex: 1;
  cursor: pointer;
}

.project-info h4 {
  margin: 0 0 5px 0;
  font-size: 1rem;
  color: #333;
}

.project-info p {
  margin: 2px 0;
  font-size: 12px;
  color: #666;
}

.project-info .date {
  font-size: 11px;
  color: #999;
}

.project-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
}

.action-btn.load:hover {
  background: #e8f5e9;
}

.action-btn.delete:hover {
  background: #ffebee;
}
</style>