'''Создаём Vue-компонент формы обратной связи
Создайте файл src/components/FeedbackModal.vue:'''

<template>
  <div v-if="show" class="modal-overlay" @click="close">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h3>📬 Обратная связь</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>

      <div class="modal-body">
        <p class="intro">
          Есть вопрос, нашли ошибку или хотите что-то предложить?
          Напишите нам — мы обязательно ответим!
        </p>

        <form @submit.prevent="submitForm">
          <div class="form-row">
            <div class="form-group">
              <label>Имя *</label>
              <input v-model="form.name" type="text" required maxlength="100" placeholder="Как к вам обращаться?">
            </div>
            <div class="form-group">
              <label>Email *</label>
              <input v-model="form.email" type="email" required placeholder="example@mail.com">
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Телефон</label>
              <input v-model="form.phone" type="tel" maxlength="20" placeholder="+7 (999) 123-45-67">
            </div>
            <div class="form-group">
              <label>Категория</label>
              <select v-model="form.category">
                <option value="question">Вопрос</option>
                <option value="bug">Ошибка</option>
                <option value="suggestion">Предложение</option>
                <option value="complaint">Жалоба</option>
                <option value="other">Другое</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Тема *</label>
            <input v-model="form.subject" type="text" required maxlength="200" placeholder="Кратко о чём сообщение">
          </div>

          <div class="form-group">
            <label>Сообщение * (минимум 10 символов)</label>
            <textarea v-model="form.message" required rows="5" placeholder="Опишите подробнее..."></textarea>
            <small class="char-counter">{{ form.message.length }} / 2000</small>
          </div>

          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>

          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="close">Отмена</button>
            <button type="submit" class="btn-submit" :disabled="loading">
              {{ loading ? 'Отправка...' : 'Отправить' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'https://test.zastava-86.ru/api'

export default {
  name: 'FeedbackModal',
  props: {
    show: Boolean
  },
  emits: ['close'],
  data() {
    return {
      form: {
        name: '',
        email: '',
        phone: '',
        category: 'question',
        subject: '',
        message: ''
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  methods: {
    async submitForm() {
      this.error = ''
      this.success = ''
      this.loading = true

      try {
        console.log('API_URL =', API_URL)
        console.log('URL запроса =', `${API_URL}/feedback/`)
        await axios.post(`${API_URL}/feedback/`, this.form)
        this.success = '✅ Сообщение отправлено! Мы ответим в ближайшее время.'
        setTimeout(() => {
          this.close()
        }, 2000)
      } catch (err) {
        console.error('Ошибка отправки:', err)
        if (err.response?.data) {
          const errors = Object.values(err.response.data).flat().join(' ')
          this.error = errors || 'Ошибка отправки'
        } else {
          this.error = 'Не удалось отправить сообщение. Попробуйте позже.'
        }
      } finally {
        this.loading = false
      }
    },
    close() {
      this.$emit('close')
      setTimeout(() => {
        this.form = {
          name: '', email: '', phone: '',
          category: 'question', subject: '', message: ''
        }
        this.error = ''
        this.success = ''
      }, 300)
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}
.modal-container {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 24px;
  border-bottom: 1px solid #e5e5e5;
  background: #fafafa;
  position: sticky;
  top: 0;
}
.modal-header h3 { margin: 0; font-size: 1.3rem; }
.close-btn {
  background: none; border: none; font-size: 28px;
  cursor: pointer; color: #999; border-radius: 50%;
  width: 36px; height: 36px;
}
.close-btn:hover { color: #333; background: #f0f0f0; }
.modal-body { padding: 24px; }
.intro { color: #666; margin-top: 0; font-size: 14px; }
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
@media (max-width: 500px) {
  .form-row { grid-template-columns: 1fr; }
}
.form-group { margin-bottom: 16px; }
.form-group label {
  display: block; margin-bottom: 6px;
  font-weight: 500; color: #333; font-size: 14px;
}
.form-group input,
.form-group select,
.form-group textarea {
  width: 100%; padding: 10px 12px;
  border: 1px solid #ddd; border-radius: 8px;
  font-size: 14px; font-family: inherit;
  box-sizing: border-box;
}
.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none; border-color: #4CAF50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}
.char-counter {
  color: #999; font-size: 11px;
  float: right; margin-top: 4px;
}
.error-message {
  background: #ffebee; color: #c62828;
  padding: 10px 14px; border-radius: 8px;
  margin-bottom: 16px; font-size: 14px;
}
.success-message {
  background: #e8f5e9; color: #2e7d32;
  padding: 10px 14px; border-radius: 8px;
  margin-bottom: 16px; font-size: 14px;
}
.form-actions {
  display: flex; gap: 12px; margin-top: 8px;
}
.btn-cancel, .btn-submit {
  flex: 1; padding: 12px 20px; border: none;
  border-radius: 8px; font-size: 15px;
  font-weight: 500; cursor: pointer;
}
.btn-cancel { background: #f0f0f0; color: #666; }
.btn-cancel:hover { background: #e0e0e0; }
.btn-submit { background: #4CAF50; color: white; }
.btn-submit:hover:not(:disabled) { background: #45a049; }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
</style>