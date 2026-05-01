<template>
  <div class="badge-editor">
    <div class="toolbar">
      <h2>Редактор значков</h2>
      
      <div class="size-selector">
        <label>Диаметр:</label>
        <button 
          :class="['size-btn', { active: diameter === 37 }]"
          @click="setDiameter(37)"
        >
          37 мм (вертикальный)
        </button>
        <button 
          :class="['size-btn', { active: diameter === 44 }]"
          @click="setDiameter(44)"
        >
          44 мм (горизонтальный)
        </button>
        <button 
          :class="['size-btn', { active: diameter === 58 }]"
          @click="setDiameter(58)"
        >
          58 мм
        </button>
      </div>
      
      <div class="buttons">
        <button class="btn btn-primary" @click="savePDF">Сохранить PDF</button>
        <button class="btn btn-secondary" @click="print">Печать</button>
        <button class="btn btn-danger" @click="clearAll">Очистить всё</button>
      </div>
    </div>

    <div class="a4-sheet" :class="orientationClass">
      <div class="grid" :style="gridStyle">
        <div 
          v-for="index in totalShapes" 
          :key="index"
          class="shape-slot"
          @click="openImageEditor(index - 1)"
        >
          <div class="cut-line"></div>
          <div class="inner-circle">
            <img 
              v-if="images[index - 1]" 
              :src="images[index - 1].imageData" 
              class="shape-image"
              :style="getImageStyle(images[index - 1])"
            >
            <div v-else class="plus">+</div>
          </div>
        </div>
      </div>
    </div>

    <ImageEditorModal
      :show="showEditor"
      :original-image="tempImage"
      @close="showEditor = false"
      @apply="applyImage"
    />
  </div>
</template>

<script>
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import ImageEditorModal from './ImageEditorModal.vue'

export default {
  name: 'BadgeEditor',
  components: {
    ImageEditorModal
  },
  data() {
    return {
      images: {},
      diameter: 44,
      showEditor: false,
      currentIndex: null,
      tempImage: null
    }
  },
  computed: {
    orientationClass() {
      return this.diameter === 44 ? 'landscape' : 'portrait'
    },
    totalShapes() {
      if (this.diameter === 44) {
        return 12
      } else if (this.diameter === 37) {
        return 12
      } else {
        return 6
      }
    },
    gridStyle() {
      let cols
      if (this.diameter === 44) {
        cols = 4
      } else if (this.diameter === 37) {
        cols = 3
      } else {
        cols = 3
      }
      
      return {
        display: 'grid',
        gridTemplateColumns: `repeat(${cols}, 1fr)`,
        gap: '20px',
        justifyItems: 'center',
        alignItems: 'center'
      }
    }
  },
  methods: {
    setDiameter(mm) {
      this.diameter = mm
      this.saveToLocalStorage()
    },
    getImageStyle(imgData) {
      if (!imgData) return {}
      return {
        transform: `scale(${imgData.scale || 1}) rotate(${imgData.rotation || 0}deg)`,
        transition: 'transform 0.2s ease'
      }
    },
    openImageEditor(index) {
      this.currentIndex = index
      const existing = this.images[index]
      this.tempImage = existing ? existing.imageData : null
      this.showEditor = true
    },
    applyImage(data) {
      if (this.currentIndex !== null) {
        if (data.fillMode === 'all') {
          const newImages = {}
          for (let i = 0; i < this.totalShapes; i++) {
            newImages[i] = {
              imageData: data.imageData,
              scale: data.scale,
              rotation: data.rotation
            }
          }
          this.images = newImages
        } else {
          this.images = {
            ...this.images,
            [this.currentIndex]: {
              imageData: data.imageData,
              scale: data.scale,
              rotation: data.rotation
            }
          }
        }
        this.saveToLocalStorage()
        this.$forceUpdate()
      }
      this.showEditor = false
      this.currentIndex = null
    },
    async savePDF() {
      const element = document.querySelector('.a4-sheet')
      if (!element) {
        alert('Не найден элемент для печати')
        return
      }
      
      try {
        const canvas = await html2canvas(element, {
          scale: 3,
          backgroundColor: '#ffffff',
          logging: false
        })
        
        const imgData = canvas.toDataURL('image/png')
        const pdf = new jsPDF({
          unit: 'mm',
          format: 'a4',
          orientation: this.diameter === 44 ? 'landscape' : 'portrait'
        })
        
        const pdfWidth = pdf.internal.pageSize.getWidth()
        const pdfHeight = pdf.internal.pageSize.getHeight()
        
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight)
        pdf.save(`badges_${this.diameter}mm.pdf`)
      } catch (error) {
        console.error('Ошибка PDF:', error)
        alert('Ошибка при создании PDF')
      }
    },
    print() {
      window.print()
    },
    clearAll() {
      if (confirm('Очистить все изображения?')) {
        this.images = {}
        this.saveToLocalStorage()
        this.$forceUpdate()
      }
    },
    saveToLocalStorage() {
      localStorage.setItem('badge_images', JSON.stringify(this.images))
      localStorage.setItem('badge_diameter', this.diameter)
    },
    loadFromLocalStorage() {
      const savedImages = localStorage.getItem('badge_images')
      if (savedImages) {
        try {
          this.images = JSON.parse(savedImages)
        } catch (e) {
          console.error('Ошибка загрузки:', e)
        }
      }
      
      const savedDiameter = localStorage.getItem('badge_diameter')
      if (savedDiameter) {
        this.diameter = parseInt(savedDiameter)
      }
    }
  },
  mounted() {
    this.loadFromLocalStorage()
  }
}
</script>

<style scoped>
.badge-editor {
  min-height: 100vh;
  background: #f0f0f0;
  padding: 20px;
}

.toolbar {
  background: white;
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.toolbar h2 {
  margin: 0;
  font-size: 20px;
}

.size-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.size-selector label {
  font-weight: 500;
}

.size-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.size-btn.active {
  background: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover {
  background: #45a049;
}

.btn-secondary {
  background: #2196F3;
  color: white;
}

.btn-secondary:hover {
  background: #0b7dda;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-danger:hover {
  background: #da190b;
}

.a4-sheet {
  background: white;
  margin: 0 auto;
  padding: 15mm;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  border-radius: 4px;
}

.a4-sheet.landscape {
  width: 297mm;
  min-height: 210mm;
}

.a4-sheet.portrait {
  width: 210mm;
  min-height: 297mm;
}

.grid {
  display: grid;
  width: 100%;
  height: 100%;
}

.shape-slot {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;
  cursor: pointer;
  transition: transform 0.2s;
}

.shape-slot:hover {
  transform: scale(1.02);
}

.cut-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px dashed #ff0000;
  z-index: 2;
  pointer-events: none;
}

.inner-circle {
  position: absolute;
  top: 10%;
  left: 10%;
  width: 80%;
  height: 80%;
  border-radius: 50%;
  background: #f5f5f5;
  border: 2px solid #333;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.plus {
  font-size: 40px;
  color: #ccc;
  font-weight: bold;
}

.shape-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

@media print {
  .toolbar {
    display: none !important;
  }
  
  .a4-sheet {
    box-shadow: none;
    padding: 0;
    margin: 0;
  }
  
  .cut-line {
    border: 1px dashed #000 !important;
  }
}
</style>