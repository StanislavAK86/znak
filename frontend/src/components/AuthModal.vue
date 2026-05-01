<template>
  <div v-if="show" class="modal-overlay" @click="close">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h3>{{ isLogin ? 'Вход' : 'Регистрация' }}</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      
      <div class="modal-body-auth">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>Имя пользователя</label>
            <input 
              type="text" 
              v-model="username" 
              required 
              placeholder="Введите имя пользователя"
            >
          </div>
          
          <div v-if="!isLogin" class="form-group">
            <label>Email</label>
            <input 
              type="email" 
              v-model="email" 
              placeholder="example@mail.com"
            >
          </div>
          
          <div class="form-group">
            <label>Пароль</label>
            <input 
              type="password" 
              v-model="password" 
              required 
              placeholder="Введите пароль"
            >
          </div>
          
          <div v-if="error" class="error-message">{{ error }}</div>
          
          <button type="submit" class="submit-btn" :disabled="loading">
            {{ loading ? 'Загрузка...' : (isLogin ? 'Войти' : 'Зарегистрироваться') }}
          </button>
        </form>
        
        <div class="switch-mode">
          <button type="button" @click="toggleMode">
            {{ isLogin ? 'Нет аккаунта? Зарегистрироваться' : 'Уже есть аккаунт? Войти' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '../stores/authStore'

export default {
  name: 'AuthModal',
  props: {
    show: Boolean
  },
  emits: ['close', 'success'],
  data() {
    return {
      isLogin: true,
      username: '',
      email: '',
      password: '',
      error: '',
      loading: false
    }
  },
  methods: {
    async handleSubmit() {
      this.error = ''
      this.loading = true
      
      const authStore = useAuthStore()
      let result
      
      if (this.isLogin) {
        result = await authStore.login(this.username, this.password)
      } else {
        result = await authStore.register(this.username, this.email, this.password)
      }
      
      this.loading = false
      
      if (result.success) {
        this.$emit('success')
        this.close()
        // Перенаправляем на профиль после входа
        if (this.$router) {
          this.$router.push('/profile')
        }
      } else {
        this.error = result.error || 'Произошла ошибка'
      }
    },
    
    toggleMode() {
      this.isLogin = !this.isLogin
      this.error = ''
      this.username = ''
      this.email = ''
      this.password = ''
    },
    
    close() {
      this.$emit('close')
      this.resetForm()
    },
    
    resetForm() {
      this.isLogin = true
      this.username = ''
      this.email = ''
      this.password = ''
      this.error = ''
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
  max-width: 400px;
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

.modal-body-auth {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #4CAF50;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 14px;
}

.submit-btn {
  width: 100%;
  padding: 12px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #45a049;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.switch-mode {
  margin-top: 20px;
  text-align: center;
}

.switch-mode button {
  background: none;
  border: none;
  color: #4CAF50;
  cursor: pointer;
  font-size: 14px;
}

.switch-mode button:hover {
  text-decoration: underline;
}
</style>