<template>
  <div v-if="show" class="modal-overlay" @click="close">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h3>Редактирование изображения</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="preview-area">
          <div class="circle-preview">
            <div class="cut-line-guide"></div>
            <div class="inner-circle-guide" ref="captureArea">
              <div class="image-container">
                <img 
                  ref="movableImage"
                  :src="previewImage" 
                  class="editable-image"
                  :style="imageStyle"
                  @mousedown="startDrag"
                  @wheel.prevent="handleWheel"
                  @dragstart.prevent
                >
              </div>
            </div>
          </div>
          <div class="hint-text">Колесо мыши - масштаб, перетаскивание - перемещение</div>
        </div>
        
        <div class="controls-area">
          <div class="control-group">
            <label>Масштаб: {{ Math.round(scale * 100) }}%</label>
            <input 
              type="range" 
              v-model.number="scale" 
              min="0.2" 
              max="5" 
              step="0.01"
              @input="onScaleChange"
            >
            <div class="button-row">
              <button @click="scale = Math.max(0.2, scale - 0.1)">−10%</button>
              <button @click="scale = Math.min(5, scale + 0.1)">+10%</button>
              <button @click="resetAll">Сброс</button>
            </div>
          </div>
          
          <div class="control-group">
            <label>Поворот: {{ rotation }}°</label>
            <input 
              type="range" 
              v-model.number="rotation" 
              min="0" 
              max="360" 
              step="1"
            >
            <div class="button-row">
              <button @click="rotation = (rotation - 90 + 360) % 360">↺ 90°</button>
              <button @click="rotation = (rotation + 90) % 360">↻ 90°</button>
              <button @click="rotation = 0">Сброс</button>
            </div>
          </div>
          
          <div class="control-group">
            <label>Режим заполнения</label>
            <div class="radio-group">
              <label class="radio-option">
                <input type="radio" v-model="fillMode" value="single">
                <span>Только один значок</span>
              </label>
              <label class="radio-option">
                <input type="radio" v-model="fillMode" value="all">
                <span>Заполнить страницу</span>
              </label>
            </div>
          </div>
          
          <div class="action-buttons">
            <button class="btn-cancel" @click="close">Отмена</button>
            <button class="btn-apply" @click="apply">Применить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import html2canvas from 'html2canvas'

export default {
  name: 'ImageEditorModal',
  props: {
    show: Boolean,
    originalImage: String
  },
  emits: ['close', 'apply'],
  data() {
    return {
      scale: 1.0,
      rotation: 0,
      fillMode: 'single',
      previewImage: null,
      translateX: 0,
      translateY: 0,
      isDragging: false,
      dragStartX: 0,
      dragStartY: 0,
      startTranslateX: 0,
      startTranslateY: 0
    }
  },
  computed: {
    imageStyle() {
      return {
        transform: `translate(${this.translateX}px, ${this.translateY}px) scale(${this.scale}) rotate(${this.rotation}deg)`,
        transition: this.isDragging ? 'none' : 'transform 0.1s ease',
        cursor: this.isDragging ? 'grabbing' : 'grab',
        transformOrigin: 'center center'
      }
    }
  },
  watch: {
    originalImage: {
      immediate: true,
      handler(val) {
        if (val) {
          this.previewImage = val
          this.resetAll()
        }
      }
    },
    show(val) {
      if (val) {
        this.resetAll()
      }
    }
  },
  methods: {
    resetAll() {
      this.scale = 1.0
      this.rotation = 0
      this.translateX = 0
      this.translateY = 0
      this.fillMode = 'single'
    },
    
    onScaleChange() {
      this.translateX = 0
      this.translateY = 0
    },
    
    handleWheel(event) {
      const delta = event.deltaY > 0 ? -0.1 : 0.1
      const newScale = Math.min(5, Math.max(0.2, this.scale + delta))
      if (newScale !== this.scale) {
        this.scale = newScale
        this.translateX = 0
        this.translateY = 0
      }
      event.preventDefault()
    },
    
    startDrag(event) {
      this.isDragging = true
      this.dragStartX = event.clientX
      this.dragStartY = event.clientY
      this.startTranslateX = this.translateX
      this.startTranslateY = this.translateY
      
      const onMouseMove = (moveEvent) => {
        if (this.isDragging) {
          this.translateX = this.startTranslateX + (moveEvent.clientX - this.dragStartX)
          this.translateY = this.startTranslateY + (moveEvent.clientY - this.dragStartY)
          // Без ограничений!
        }
      }
      
      const onMouseUp = () => {
        this.isDragging = false
        document.removeEventListener('mousemove', onMouseMove)
        document.removeEventListener('mouseup', onMouseUp)
      }
      
      document.addEventListener('mousemove', onMouseMove)
      document.addEventListener('mouseup', onMouseUp)
    },
    
    close() {
      this.$emit('close')
    },
    
    async apply() {
      const captureElement = this.$refs.captureArea
      if (!captureElement) return
      
      try {
        // Делаем снимок внутреннего круга
        const canvas = await html2canvas(captureElement, {
          scale: 4,
          backgroundColor: '#ffffff',
          useCORS: true,
          logging: false
        })
        
        // Создаём финальный канвас 500x500
        const finalCanvas = document.createElement('canvas')
        const finalCtx = finalCanvas.getContext('2d')
        finalCanvas.width = 500
        finalCanvas.height = 500
        
        finalCtx.fillStyle = '#ffffff'
        finalCtx.fillRect(0, 0, 500, 500)
        
        finalCtx.save()
        finalCtx.beginPath()
        finalCtx.arc(250, 250, 250, 0, Math.PI * 2)
        finalCtx.clip()
        
        // Рисуем захваченное изображение
        finalCtx.drawImage(canvas, 0, 0, 500, 500)
        finalCtx.restore()
        
        const finalImage = finalCanvas.toDataURL('image/png')
        
        this.$emit('apply', {
          imageData: finalImage,
          scale: this.scale,
          rotation: this.rotation,
          fillMode: this.fillMode
        })
      } catch (error) {
        console.error('Ошибка при сохранении:', error)
        alert('Ошибка при сохранении изображения')
      }
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
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-container {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 950px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
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

.modal-body {
  padding: 24px;
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
  overflow-y: auto;
  flex: 1;
}

.preview-area {
  flex: 1.4;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.circle-preview {
  position: relative;
  width: 280px;
  height: 280px;
  background: #f5f5f5;
  border-radius: 50%;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.cut-line-guide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 3px dashed #ff4444;
  z-index: 2;
  pointer-events: none;
}

.inner-circle-guide {
  position: absolute;
  top: 12%;
  left: 12%;
  width: 76%;
  height: 76%;
  border-radius: 50%;
  overflow: hidden;
  background: white;
  box-shadow: inset 0 0 0 2px #333;
}

.image-container {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #fff;
}

.editable-image {
  min-width: 100%;
  min-height: 100%;
  object-fit: cover;
  user-select: none;
  pointer-events: auto;
}

.hint-text {
  font-size: 12px;
  color: #888;
  text-align: center;
}

.controls-area {
  flex: 1;
  min-width: 240px;
}

.control-group {
  margin-bottom: 24px;
}

.control-group label {
  display: block;
  margin-bottom: 10px;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.control-group input[type="range"] {
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: #ddd;
  -webkit-appearance: none;
}

.control-group input[type="range"]:focus {
  outline: none;
}

.control-group input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #4CAF50;
  cursor: pointer;
}

.button-row {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.button-row button {
  padding: 6px 12px;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.button-row button:hover {
  background: #e0e0e0;
}

.radio-group {
  display: flex;
  gap: 24px;
  margin-bottom: 10px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
}

.radio-option input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 30px;
}

.btn-cancel, .btn-apply {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-cancel {
  background: #f0f0f0;
  color: #666;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.btn-apply {
  background: #4CAF50;
  color: white;
}

.btn-apply:hover {
  background: #45a049;
}
</style>