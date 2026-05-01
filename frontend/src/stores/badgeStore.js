import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'https://test.zastava-86.ru/api'

export const useBadgeStore = defineStore('badge', {
  state: () => ({
    projects: [],
    currentProject: null,
    loading: false,
    images: {},
    currentDiameter: 44,
    currentOrientation: 'landscape'
  }),

  getters: {
    isAuthenticated: () => !!localStorage.getItem('access_token')
  },

  actions: {
    setAuthHeader() {
      const token = localStorage.getItem('access_token')
      if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        console.log('Токен установлен:', token.substring(0, 20) + '...')
      } else {
        console.log('Токен не найден')
      }
    },

    async loadProjects() {
      if (!this.isAuthenticated) {
        console.log('Не авторизован, пропускаем загрузку проектов')
        return
      }
      
      this.loading = true
      this.setAuthHeader()
      try {
        const response = await axios.get(`${API_URL}/badge-projects/`)
        this.projects = response.data
        console.log('Загружено проектов:', this.projects.length)
        return { success: true, data: response.data }
      } catch (error) {
        console.error('Ошибка загрузки проектов:', error.response?.status, error.response?.data)
        if (error.response?.status === 401) {
          console.log('Требуется авторизация')
        }
        return { success: false, error: error.response?.data }
      } finally {
        this.loading = false
      }
    },

    async saveProject(projectData) {
      // Проверяем авторизацию
      if (!this.isAuthenticated) {
        console.log('Не авторизован, сохраняем в localStorage')
        this.saveToLocalStorage()
        return { success: true, local: true }
      }
      
      this.setAuthHeader()
      const data = {
        name: projectData.name || `Проект от ${new Date().toLocaleDateString()}`,
        shape_type: 'circle',
        diameter_mm: projectData.diameter || this.currentDiameter,
        orientation: projectData.orientation || this.currentOrientation,
        shapes_data: projectData.images || this.images
      }
      
      try {
        let response
        if (this.currentProject?.id) {
          response = await axios.put(`${API_URL}/badge-projects/${this.currentProject.id}/`, data)
          const index = this.projects.findIndex(p => p.id === response.data.id)
          if (index !== -1) {
            this.projects[index] = response.data
          }
        } else {
          response = await axios.post(`${API_URL}/badge-projects/`, data)
          this.projects.unshift(response.data)
        }
        
        this.currentProject = response.data
        console.log('Проект сохранён на сервере:', response.data.name)
        return { success: true, data: response.data }
      } catch (error) {
        console.error('Ошибка сохранения:', error.response?.status, error.response?.data)
        if (error.response?.status === 401) {
          console.log('Требуется авторизация - сохраняем локально')
          this.saveToLocalStorage()
          return { success: true, local: true }
        }
        return { success: false, error: error.response?.data }
      }
    },

    async loadProject(project) {
      this.currentProject = project
      this.currentDiameter = project.diameter_mm
      this.currentOrientation = project.orientation
      this.images = project.shapes_data || {}
      console.log('Загружен проект:', project.name)
    },

    async deleteProject(projectId) {
      if (!this.isAuthenticated) return { success: false }
      
      this.setAuthHeader()
      try {
        await axios.delete(`${API_URL}/badge-projects/${projectId}/`)
        this.projects = this.projects.filter(p => p.id !== projectId)
        if (this.currentProject?.id === projectId) {
          this.currentProject = null
          this.images = {}
          this.currentDiameter = 44
          this.currentOrientation = 'landscape'
        }
        console.log('Проект удалён')
        return { success: true }
      } catch (error) {
        console.error('Ошибка удаления:', error)
        return { success: false }
      }
    },

    async generatePDF(projectId) {
      if (!this.isAuthenticated) return { success: false }
      
      this.setAuthHeader()
      try {
        const response = await axios.post(`${API_URL}/badge-projects/${projectId}/generate-pdf/`)
        
        const link = document.createElement('a')
        link.href = `data:application/pdf;base64,${response.data.pdf}`
        link.download = response.data.filename
        link.click()
        
        return { success: true }
      } catch (error) {
        console.error('Ошибка генерации PDF:', error)
        return { success: false, error: error.response?.data }
      }
    },

    createNewProject() {
      this.currentProject = null
      this.images = {}
      this.currentDiameter = 44
      this.currentOrientation = 'landscape'
      console.log('Создан новый проект')
    },

    setImage(index, imageData) {
      this.images[index] = imageData
    },

    clearImage(index) {
      delete this.images[index]
    },

    clearAllImages() {
      this.images = {}
    },

    saveToLocalStorage() {
      const data = {
        images: this.images,
        diameter: this.currentDiameter,
        orientation: this.currentOrientation
      }
      localStorage.setItem('badge_editor_data', JSON.stringify(data))
      console.log('Сохранено в localStorage')
    },

    loadFromLocalStorage() {
      const saved = localStorage.getItem('badge_editor_data')
      if (saved) {
        try {
          const data = JSON.parse(saved)
          this.images = data.images || {}
          this.currentDiameter = data.diameter || 44
          this.currentOrientation = data.orientation || 'landscape'
        } catch(e) {
          console.error('Ошибка загрузки из localStorage:', e)
        }
      }
    },

    reset() {
      this.currentProject = null
      this.images = {}
      this.currentDiameter = 44
      this.currentOrientation = 'landscape'
    }
  }
})