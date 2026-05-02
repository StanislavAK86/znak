<template>
  <div class="editor-container">
    <div class="header">
      <h1>Редактор шаблонов значки {{ currentDiameter }} мм · A4 {{ currentOrientation === 'landscape' ? 'Горизонт.' : 'Вертик.' }}</h1>
      
      <div class="diameter-selector">
        <!-- 25 мм -->
        <div class="size-group">
          <label>25 мм:</label>
          <button 
            :class="['orient-btn', { active: currentDiameter === 25 && currentOrientation === 'portrait' }]"
            @click="changeConfig(25, 'portrait')"
          >
            Вертик.
          </button>
          <button 
            :class="['orient-btn', { active: currentDiameter === 25 && currentOrientation === 'landscape' }]"
            @click="changeConfig(25, 'landscape')"
          >
            Горизонт.
          </button>
        </div>
        
        <!-- 32 мм -->
        <div class="size-group">
          <label>32 мм:</label>
          <button 
            :class="['orient-btn', { active: currentDiameter === 32 && currentOrientation === 'portrait' }]"
            @click="changeConfig(32, 'portrait')"
          >
            Вертик.
          </button>
          <button 
            :class="['orient-btn', { active: currentDiameter === 32 && currentOrientation === 'landscape' }]"
            @click="changeConfig(32, 'landscape')"
          >
            Горизонт.
          </button>
        </div>
        
        <!-- 34 мм -->
        <div class="size-group">
          <label>34 мм:</label>
          <button 
            :class="['orient-btn', { active: currentDiameter === 34 && currentOrientation === 'portrait' }]"
            @click="changeConfig(34, 'portrait')"
          >
            Вертик.
          </button>
          <button 
            :class="['orient-btn', { active: currentDiameter === 34 && currentOrientation === 'landscape' }]"
            @click="changeConfig(34, 'landscape')"
          >
            Горизонт.
          </button>
        </div>
        
        <!-- 37 мм -->
        <div class="size-group">
          <label>37 мм:</label>
          <button 
            :class="['orient-btn', { active: currentDiameter === 37 && currentOrientation === 'portrait' }]"
            @click="changeConfig(37, 'portrait')"
          >
            Вертик.
          </button>
          <button 
            :class="['orient-btn', { active: currentDiameter === 37 && currentOrientation === 'landscape' }]"
            @click="changeConfig(37, 'landscape')"
          >
            Горизонт.
          </button>
        </div>
        
        <!-- 44 мм -->
        <div class="size-group">
          <label>44 мм:</label>
          <button 
            :class="['orient-btn', { active: currentDiameter === 44 && currentOrientation === 'portrait' }]"
            @click="changeConfig(44, 'portrait')"
          >
            Вертик.
          </button>
          <button 
            :class="['orient-btn', { active: currentDiameter === 44 && currentOrientation === 'landscape' }]"
            @click="changeConfig(44, 'landscape')"
          >
            Горизонт.
          </button>
        </div>
        
        <!-- 50 мм -->
        <div class="size-group">
          <label>50 мм:</label>
          <button 
            :class="['orient-btn', { active: currentDiameter === 50 && currentOrientation === 'portrait' }]"
            @click="changeConfig(50, 'portrait')"
          >
            Вертик.
          </button>
          <button 
            :class="['orient-btn', { active: currentDiameter === 50 && currentOrientation === 'landscape' }]"
            @click="changeConfig(50, 'landscape')"
          >
            Горизонт.
          </button>
        </div>
        
        <!-- 58 мм -->
        <div class="size-group">
          <label>58 мм:</label>
          <button 
            :class="['orient-btn', { active: currentDiameter === 58 && currentOrientation === 'portrait' }]"
            @click="changeConfig(58, 'portrait')"
          >
            Вертик.
          </button>
          <button 
            :class="['orient-btn', { active: currentDiameter === 58 && currentOrientation === 'landscape' }]"
            @click="changeConfig(58, 'landscape')"
          >
            Горизонт.
          </button>
        </div>
        
        <!-- 75 мм -->
        <div class="size-group">
          <label>75 мм:</label>
          <button 
            :class="['orient-btn', { active: currentDiameter === 75 && currentOrientation === 'portrait' }]"
            @click="changeConfig(75, 'portrait')"
          >
            Вертик.
          </button>
          <button 
            :class="['orient-btn', { active: currentDiameter === 75 && currentOrientation === 'landscape' }]"
            @click="changeConfig(75, 'landscape')"
          >
            Горизонт.
          </button>
        </div>
      </div>
      
      <div class="actions">
        <button class="pdf-btn" @click="exportPDF">Сохранить PDF</button>
        <button class="print-btn" @click="printPage">Печать A4</button>
        <button v-if="isAuthenticated" class="save-btn" @click="saveProjectManually">💾 Сохранить проект</button>
        <button class="clear-btn" @click="clearAll">Очистить всё</button>
        <button class="fill-btn" @click="openFillAllModal">Заполнить все</button>
        <button class="new-btn" @click="createNewProject">➕ Новый проект</button>
        <button class="projects-btn" @click="openProjectsModal">📁 Проекты</button>
        <button class="profile-btn" @click="goToProfile">👤 Профиль</button>
        <button v-if="!isAuthenticated" class="login-btn" @click="openAuthModal">👤 Войти</button>
        <button v-else class="logout-btn" @click="logout">🚪 Выйти</button>
      </div>
      
      <div class="warning">
        ⚠️ Ваши данные не сохраняются при обновлении. Будет чистый лист, обновление страницы приведёт к потере данных. Для сохранения данных зарегистрируйтесь и войдите
      </div>
    </div>

    <div class="a4-page" :class="currentOrientation" ref="a4page">
      <div :style="wrapperStyle">
        <div 
          class="circle-cell"
          :style="cellStyle"
          v-for="(item, idx) in totalCircles"
          :key="idx"
          @click="openEditor(idx)"
        >
          <div class="outer-circle" :style="outerStyle"></div>
          <div class="inner-circle" :style="innerStyle">
            <img 
              v-if="images[idx]" 
              :src="images[idx]" 
              class="circle-image"
              @error="handleImageError(idx)"
            >
            <span v-else class="plus">+</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Отладочная панель -->
    <div class="debug-panel">
      <strong>Отладка:</strong><br>
      Диаметр: {{ currentDiameter }} мм<br>
      Ориентация: {{ currentOrientation === 'landscape' ? 'Альбомная' : 'Портретная' }}<br>
      Размер круга: {{ circleSizePx }} px<br>
      Сетка: {{ gridCols }} x {{ gridRows }}<br>
      Всего кругов: {{ totalCircles }}<br>
      Максимум на А4: {{ gridCols * gridRows }}<br>
      Загружено изображений: {{ Object.keys(images).length }}<br>
      Авторизован: {{ isAuthenticated ? 'Да' : 'Нет' }}
    </div>

    <!-- Модальное окно выбора файла (для одного круга) -->
    <div class="modal" :class="{ show: modalVisible }" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3>Выберите изображение</h3>
        <input 
          type="file" 
          ref="fileInput" 
          accept="image/jpeg,image/png,image/gif,image/webp" 
          @change="onImageSelect"
        >
        <div class="modal-buttons">
          <button @click="closeModal">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно для заполнения всех кругов -->
    <div class="modal" :class="{ show: fillAllModalVisible }" @click="closeFillAllModal">
      <div class="modal-content" @click.stop>
        <h3>Выберите изображение для всех значков</h3>
        <input 
          type="file" 
          ref="fillAllFileInput" 
          accept="image/jpeg,image/png,image/gif,image/webp" 
          @change="onFillAllImageSelect"
        >
        <div class="modal-buttons">
          <button @click="closeFillAllModal">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Редактор изображений -->
    <ImageEditorModal
      :show="showImageEditor"
      :original-image="tempImageData"
      @close="closeImageEditor"
      @apply="applyEditedImage"
    />

    <!-- Модальные окна авторизации и проектов -->
    <AuthModal
      :show="showAuthModal"
      @close="closeAuthModal"
      @success="onAuthSuccess"
    />
    
    <ProjectsModal
      :show="showProjectsModal"
      @close="closeProjectsModal"
      @load-project="onLoadProject"
    />
    <div v-if="notification.show" :class="['notification', notification.type]">
      {{ notification.message }}
    </div>
  </div>
</template>

<script>
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import ImageEditorModal from './ImageEditorModal.vue'
import AuthModal from './AuthModal.vue'
import ProjectsModal from './ProjectsModal.vue'
import { useAuthStore } from '../stores/authStore'
import { useBadgeStore } from '../stores/badgeStore'

export default {
  name: 'CircleEditor',
  components: {
    ImageEditorModal,
    AuthModal,
    ProjectsModal
  },
  data() {
    return {
      currentDiameter: 44,
      currentOrientation: 'landscape',
      images: {},
      currentIndex: null,
      modalVisible: false,
      fillAllModalVisible: false,
      showImageEditor: false,
      tempImageData: null,
      tempImageIndex: null,
      showAuthModal: false,
      showProjectsModal: false,
      circleSizePx: 166,
      notification: {
        show: false,
        message: '',
        type: 'success' // success, error, warning
      },
      configs: {
        // 25 мм - АБСОЛЮТНЫЙ МАКСИМУМ 88 кругов!
        '25_portrait': { cols: 8, rows: 11, total: 88 },
        '25_landscape': { cols: 11, rows: 8, total: 88 },
        // 32 мм - 54 круга
        '32_portrait': { cols: 6, rows: 9, total: 54 },
        '32_landscape': { cols: 9, rows: 6, total: 54 },
        // 34 мм - 48 кругов
        '34_portrait': { cols: 6, rows: 8, total: 48 },
        '34_landscape': { cols: 8, rows: 6, total: 48 },
        // 37 мм - 35 кругов
        '37_portrait': { cols: 5, rows: 7, total: 35 },
        '37_landscape': { cols: 7, rows: 5, total: 35 },
        // 44 мм - 24 круга
        '44_portrait': { cols: 4, rows: 6, total: 24 },
        '44_landscape': { cols: 6, rows: 4, total: 24 },
        // 50 мм - 20 кругов
        '50_portrait': { cols: 4, rows: 5, total: 20 },
        '50_landscape': { cols: 5, rows: 4, total: 20 },
        // 58 мм - 15 кругов
        '58_portrait': { cols: 3, rows: 5, total: 15 },
        '58_landscape': { cols: 5, rows: 3, total: 15 },
        // 75 мм - 6 кругов
        '75_portrait': { cols: 2, rows: 3, total: 6 },
        '75_landscape': { cols: 3, rows: 2, total: 6 }
      }
    }
  },
  computed: {
    configKey() {
      return `${this.currentDiameter}_${this.currentOrientation}`
    },
    
    gridCols() {
      return this.configs[this.configKey]?.cols || 3
    },
    
    gridRows() {
      return this.configs[this.configKey]?.rows || 3
    },
    
    totalCircles() {
      return this.configs[this.configKey]?.total || 12
    },
    
    wrapperStyle() {
      return {
        display: 'grid',
        gridTemplateColumns: `repeat(${this.gridCols}, ${this.circleSizePx}px)`,
        gridTemplateRows: `repeat(${this.gridRows}, ${this.circleSizePx}px)`,
        gap: 'auto',
        justifyContent: 'space-evenly',
        alignItems: 'center',
        justifyItems: 'center',
        alignContent: 'space-evenly',
        width: '100%',
        height: '100%',
        minHeight: this.currentOrientation === 'landscape' ? '180mm' : '257mm'
      }
    },
    
    cellStyle() {
      return {
        width: `${this.circleSizePx}px`,
        height: `${this.circleSizePx}px`,
        cursor: 'pointer',
        position: 'relative',
        margin: '5px'
      }
    },
    
    outerStyle() {
      return {
        width: '100%',
        height: '100%',
        borderRadius: '50%',
        border: '2px dashed #ff0000',
        boxSizing: 'border-box'
      }
    },
    
    innerStyle() {
      const innerSize = this.circleSizePx * 0.76
      const offset = this.circleSizePx * 0.12
      return {
        width: `${innerSize}px`,
        height: `${innerSize}px`,
        position: 'absolute',
        top: `${offset}px`,
        left: `${offset}px`,
        borderRadius: '50%',
        background: '#f5f5f5',
        border: '2px solid #333',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden'
      }
    },
    
    isAuthenticated() {
      const authStore = useAuthStore()
      return authStore.isAuthenticated
    }
  },
  mounted() {
    const badgeStore = useBadgeStore()
    
    // Если есть текущий проект в store - загружаем его
    if (badgeStore.currentProject && Object.keys(badgeStore.images).length > 0) {
      this.images = badgeStore.images
      this.currentDiameter = badgeStore.currentDiameter
      this.currentOrientation = badgeStore.currentOrientation
      this.updateCircleSize()
      console.log('Загружен проект из store:', badgeStore.currentProject.name)
    } else {
      this.images = {}
      this.currentDiameter = 44
      this.currentOrientation = 'landscape'
      this.updateCircleSize()
      console.log('Создан новый проект')
    }
    
    this.checkAuth()
    
    // Следим за изменениями в store
    this.$watch(() => badgeStore.currentProject, (newVal) => {
      if (newVal) {
        this.images = badgeStore.images
        this.currentDiameter = badgeStore.currentDiameter
        this.currentOrientation = badgeStore.currentOrientation
        this.updateCircleSize()
        this.$forceUpdate()
      }
    }, { deep: true })
  },
  methods: {

    showNotification(message, type = 'success') {
      this.notification = {
        show: true,
        message: message,
        type: type
      }
      setTimeout(() => {
        this.notification.show = false
      }, 3000)
    },

    updateCircleSize() {
      // 1 мм ≈ 3.78 px при 96 DPI
      this.circleSizePx = Math.round(this.currentDiameter * 3.78)
      console.log('Размер круга:', this.circleSizePx, 'px для', this.currentDiameter, 'мм')
    },
    
    async checkAuth() {
      const authStore = useAuthStore()
      if (authStore.token) {
        await authStore.fetchUser()
        await this.loadProjectsFromServer()
      }
    },
    
    async loadProjectsFromServer() {
      const badgeStore = useBadgeStore()
      await badgeStore.loadProjects()
    },
    
    changeConfig(diameter, orientation) {
      if (this.currentDiameter === diameter && this.currentOrientation === orientation) return
      console.log('Смена:', diameter, 'мм,', orientation)
      this.currentDiameter = diameter
      this.currentOrientation = orientation
      this.updateCircleSize()
      this.images = {}
      //this.saveToBackend()
    },
    
    openEditor(index) {
      console.log('Открыт редактор для индекса:', index)
      this.currentIndex = index
      this.modalVisible = true
    },
    
    closeModal() {
      this.modalVisible = false
    },
    
    openFillAllModal() {
      this.fillAllModalVisible = true
    },
    
    closeFillAllModal() {
      this.fillAllModalVisible = false
    },
    
    openAuthModal() {
      this.showAuthModal = true
    },
    
    closeAuthModal() {
      this.showAuthModal = false
    },
    
    openProjectsModal() {
      this.showProjectsModal = true
    },
    
    closeProjectsModal() {
      this.showProjectsModal = false
    },
    
    goToProfile() {
      this.$router.push('/profile')
    },
    
    createNewProject() {
      const badgeStore = useBadgeStore()
      badgeStore.createNewProject()
      this.images = {}
      this.currentDiameter = 44
      this.currentOrientation = 'landscape'
      this.updateCircleSize()
      this.$forceUpdate()
      console.log('Создан новый проект')
    },
    
    async logout() {
      const authStore = useAuthStore()
      authStore.logout()
      this.showAuthModal = false
      this.showProjectsModal = false
    },
    
    onImageSelect(e) {
      const file = e.target.files[0]
      const savedIndex = this.currentIndex
      
      console.log('Выбран файл для индекса:', savedIndex)
      
      if (!file) {
        this.modalVisible = false
        this.currentIndex = null
        return
      }
      
      if (!file.type.startsWith('image/')) {
        alert('Пожалуйста, выберите изображение (JPG, PNG, GIF)')
        this.modalVisible = false
        this.currentIndex = null
        return
      }
      
      const reader = new FileReader()
      
      reader.onload = (event) => {
        this.tempImageData = event.target.result
        this.tempImageIndex = savedIndex
        this.modalVisible = false
        this.showImageEditor = true
      }
      
      reader.onerror = (err) => {
        console.error('Ошибка чтения файла:', err)
        alert('Ошибка при чтении файла')
      }
      
      reader.readAsDataURL(file)
      this.currentIndex = null
    },
    
    closeImageEditor() {
      this.showImageEditor = false
      this.tempImageIndex = null
      this.tempImageData = null
    },
    
    applyEditedImage(data) {
      if (this.tempImageIndex !== null) {
        if (data.fillMode === 'all') {
          const newImages = {}
          for (let i = 0; i < this.totalCircles; i++) {
            newImages[i] = data.imageData
          }
          this.images = newImages
        } else {
          const newImages = { ...this.images }
          newImages[this.tempImageIndex] = data.imageData
          this.images = newImages
        }
        console.log('Изображение применено для индекса:', this.tempImageIndex, 'режим:', data.fillMode)
        //this.saveToBackend()
        this.$forceUpdate()
        console.log('Изображение добавлено. Нажмите "Сохранить" для сохранения проекта.')
      }
      this.closeImageEditor()
      
    },
    
    onFillAllImageSelect(e) {
      const file = e.target.files[0]
      
      console.log('Выбран файл для заполнения всех кругов:', file?.name)
      
      if (!file) {
        this.closeFillAllModal()
        return
      }
      
      if (!file.type.startsWith('image/')) {
        alert('Пожалуйста, выберите изображение (JPG, PNG, GIF)')
        this.closeFillAllModal()
        return
      }
      
      const reader = new FileReader()
      
      reader.onload = (event) => {
        this.tempImageData = event.target.result
        this.tempImageIndex = 0
        this.closeFillAllModal()
        this.showImageEditor = true
      }
      
      reader.onerror = (err) => {
        console.error('Ошибка чтения файла:', err)
        alert('Ошибка при чтении файла')
      }
      
      reader.readAsDataURL(file)
    },
    
    handleImageError(index) {
      console.error('Ошибка загрузки изображения для индекса:', index)
      const newImages = { ...this.images }
      delete newImages[index]
      this.images = newImages
      //this.saveToBackend()
    },

    async saveProjectManually() {
      // Проверка авторизации
      if (!this.isAuthenticated) {
        this.showNotification('⚠️ Для сохранения проекта необходимо войти в аккаунт!', 'warning')
        this.openAuthModal()
        return
      }
      
      const saveBtn = document.querySelector('.save-btn')
      if (saveBtn) {
        const originalText = saveBtn.textContent
        saveBtn.textContent = '💾 Сохранение...'
        saveBtn.disabled = true
        
        try {
          const result = await this.saveToBackend()
          if (result && result.success) {
            this.showNotification('✅ Проект успешно сохранён!', 'success')
          } else {
            this.showNotification('⚠️ Ошибка при сохранении проекта', 'error')
          }
        } catch (error) {
          console.error('Ошибка сохранения:', error)
          this.showNotification('❌ Ошибка при сохранении проекта', 'error')
        } finally {
          saveBtn.textContent = originalText
          saveBtn.disabled = false
        }
      }
    },
    
    async exportPDF() {
      const element = this.$refs.a4page
      if (!element) {
        alert('Не найден элемент для печати')
        return
      }
      
      try {
        const canvas = await html2canvas(element, {
          scale: 3,
          backgroundColor: '#ffffff',
          logging: false,
          useCORS: true
        })
        
        const imgData = canvas.toDataURL('image/png')
        
        let pdfOrientation = 'portrait'
        let pdfWidth = 210
        let pdfHeight = 297
        
        if (this.currentOrientation === 'landscape') {
          pdfOrientation = 'landscape'
          pdfWidth = 297
          pdfHeight = 210
        }
        
        console.log('Создание PDF с ориентацией:', pdfOrientation, 'размер:', pdfWidth, 'x', pdfHeight)
        
        const pdf = new jsPDF({
          unit: 'mm',
          format: 'a4',
          orientation: pdfOrientation
        })
        
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight)
        pdf.save(`badge_${this.currentDiameter}mm_${this.currentOrientation}.pdf`)
        console.log('PDF сохранён, ориентация:', pdfOrientation)
      } catch (err) {
        console.error('PDF error:', err)
        alert('Ошибка создания PDF: ' + err.message)
      }
    },
    
    printPage() {
      window.print()
    },
    
    clearAll() {
      if (confirm('Очистить все изображения?')) {
        this.images = {}
        this.saveToBackend()
        this.$forceUpdate()
        console.log('Все изображения очищены')
      }
    },
    
    async saveToBackend() {
      // Проверка авторизации
      if (!this.isAuthenticated) {
        console.log('Сохранение доступно только авторизованным пользователям')
        return { success: false, local: false, error: 'Not authenticated' }
      }
      
      const badgeStore = useBadgeStore()
      badgeStore.images = this.images
      badgeStore.currentDiameter = this.currentDiameter
      badgeStore.currentOrientation = this.currentOrientation
      
      const result = await badgeStore.saveProject({
        name: `Проект от ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}`,
        diameter: this.currentDiameter,
        orientation: this.currentOrientation,
        images: this.images
      })
      
      if (result.success && !result.local) {
        console.log('Проект сохранён на сервере')
        await badgeStore.loadProjects()
        return { success: true, local: false }
      } else if (result.local) {
        console.log('Проект сохранён локально (не авторизован)')
        return { success: false, local: true, error: 'Not authenticated' }
      }
      return { success: false, local: false }
    },
    
    onAuthSuccess() {
      this.showAuthModal = false
      //this.saveToBackend()
      this.loadProjectsFromServer()
    },
    
    onLoadProject(project) {
      console.log('Загрузка проекта из модалки:', project.name)
      
      // Загружаем данные проекта
      this.images = project.shapes_data || {}
      this.currentDiameter = project.diameter_mm
      this.currentOrientation = project.orientation
      this.updateCircleSize()
      
      // Сохраняем в store
      const badgeStore = useBadgeStore()
      badgeStore.currentProject = project
      badgeStore.images = this.images
      badgeStore.currentDiameter = this.currentDiameter
      badgeStore.currentOrientation = this.currentOrientation
      
      this.$forceUpdate()
      console.log('Проект загружен, изображений:', Object.keys(this.images).length)
    }
  }
}
</script>

<style scoped>
.editor-container {
  min-height: 100vh;
  background: #e0e0e0;
  padding: 20px;
}

.header {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header h1 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #333;
}

.diameter-selector {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.size-group {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f5f5f5;
  padding: 5px 10px;
  border-radius: 8px;
}

.size-group label {
  font-weight: bold;
  min-width: 45px;
}

.orient-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.orient-btn.active {
  background: #4CAF50;
  border-color: #4CAF50;
  color: white;
}

.actions {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.pdf-btn, .print-btn, .clear-btn, .fill-btn, .new-btn, .projects-btn, .profile-btn, .login-btn, .logout-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.pdf-btn {
  background: #4CAF50;
  color: white;
}

.pdf-btn:hover {
  background: #45a049;
}

.print-btn {
  background: #2196F3;
  color: white;
}

.print-btn:hover {
  background: #0b7dda;
}

.clear-btn {
  background: #f44336;
  color: white;
}

.clear-btn:hover {
  background: #da190b;
}

.fill-btn {
  background: #ff9800;
  color: white;
}

.fill-btn:hover {
  background: #e68900;
}

.new-btn {
  background: #00BCD4;
  color: white;
}

.new-btn:hover {
  background: #0097A7;
}

.projects-btn {
  background: #607D8B;
  color: white;
}

.projects-btn:hover {
  background: #546E7A;
}

.profile-btn {
  background: #9C27B0;
  color: white;
}

.profile-btn:hover {
  background: #7B1FA2;
}

.login-btn {
  background: #9C27B0;
  color: white;
}

.login-btn:hover {
  background: #7B1FA2;
}

.logout-btn {
  background: #757575;
  color: white;
}

.logout-btn:hover {
  background: #616161;
}

.warning {
  background: #fff3cd;
  color: #856404;
  padding: 10px;
  border-radius: 4px;
  font-size: 13px;
}

.a4-page {
  background: white;
  margin: 0 auto;
  padding: 20px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  border-radius: 4px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.a4-page.landscape {
  width: 297mm;
  min-height: 210mm;
}

.a4-page.portrait {
  width: 210mm;
  min-height: 297mm;
}

.circle-cell {
  transition: transform 0.2s;
}

.circle-cell:hover {
  transform: scale(1.02);
}

.plus {
  font-size: 40px;
  color: #ccc;
  font-weight: bold;
}

.circle-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.debug-panel {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: rgba(0,0,0,0.85);
  color: #0f0;
  padding: 12px;
  border-radius: 8px;
  font-family: monospace;
  font-size: 12px;
  z-index: 999;
  border: 1px solid #0f0;
  min-width: 280px;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal.show {
  display: flex;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 12px;
  text-align: center;
  min-width: 320px;
}

.modal-content h3 {
  margin: 0 0 20px 0;
  font-size: 20px;
}

.modal-content input {
  margin-bottom: 20px;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  width: 100%;
  box-sizing: border-box;
  font-size: 14px;
}

.modal-content input:hover {
  border-color: #4CAF50;
}

.modal-buttons button {
  padding: 10px 24px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.modal-buttons button:hover {
  background: #da190b;
}

@media print {
  .header, .modal, .debug-panel {
    display: none !important;
  }
  
  .a4-page {
    padding: 0;
    margin: 0;
    box-shadow: none;
  }
}

.save-btn {
  background: #28a745;
  color: white;
}

.save-btn:hover {
  background: #218838;
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Уведомления */
.notification {
  position: fixed;
  top: 80px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  z-index: 9999;
  animation: slideIn 0.3s ease;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.notification.success {
  background-color: #28a745;
}

.notification.error {
  background-color: #dc3545;
}

.notification.warning {
  background-color: #ffc107;
  color: #333;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

</style>