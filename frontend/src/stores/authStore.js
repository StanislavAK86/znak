import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || import.meta.env.VUE_APP_API_URL || 'https://test.zastava-86.ru/api/'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token'),
    loading: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user
  },

  actions: {
    setAuthHeader() {
      if (this.token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      }
    },

    async login(username, password) {
      this.loading = true
      try {
        const response = await axios.post(`${API_URL}/token/`, {
          username,
          password
        })
        this.token = response.data.access
        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)
        this.setAuthHeader()
        await this.fetchUser()
        return { success: true }
      } catch (error) {
        console.error('Login error:', error)
        return { 
          success: false, 
          error: error.response?.data?.detail || 'Ошибка входа' 
        }
      } finally {
        this.loading = false
      }
    },

    async register(username, email, password) {
      this.loading = true
      try {
        const response = await axios.post(`${API_URL}/register/`, {
          username,
          email,
          password
        })
        this.token = response.data.access
        this.user = response.data.user
        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)
        this.setAuthHeader()
        return { success: true }
      } catch (error) {
        console.error('Register error:', error)
        return { 
          success: false, 
          error: error.response?.data?.error || 'Ошибка регистрации' 
        }
      } finally {
        this.loading = false
      }
    },

    async fetchUser() {
      if (!this.token) return
      this.setAuthHeader()
      try {
        const response = await axios.get(`${API_URL}/profile/`)
        this.user = response.data
      } catch (error) {
        console.error('Fetch user error:', error)
        this.logout()
      }
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      delete axios.defaults.headers.common['Authorization']
    }
  }
})
