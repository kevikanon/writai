import { defineStore } from 'pinia'
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token') || null,
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    async login(email, password) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.post('/auth/login', { email, password })
        this.token = data.access_token
        this.user = data.user
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        return true
      } catch (err) {
        this.error = err.response?.data?.detail || 'Login failed'
        return false
      } finally {
        this.loading = false
      }
    },

    async register(name, email, password) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.post('/auth/register', { name, email, password })
        this.token = data.access_token
        this.user = data.user
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('user', JSON.stringify(data.user))
        return true
      } catch (err) {
        this.error = err.response?.data?.detail || 'Registration failed'
        return false
      } finally {
        this.loading = false
      }
    },

    async logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },

    async forgotPassword(email) {
      this.loading = true
      this.error = null
      try {
        await api.post('/auth/forgot-password', { email })
        return true
      } catch (err) {
        this.error = err.response?.data?.detail || 'Request failed'
        return false
      } finally {
        this.loading = false
      }
    },

    async resetPassword(token, password) {
      this.loading = true
      this.error = null
      try {
        await api.post('/auth/reset-password', { token, password })
        return true
      } catch (err) {
        this.error = err.response?.data?.detail || 'Reset failed'
        return false
      } finally {
        this.loading = false
      }
    },
  },
})

export { api }