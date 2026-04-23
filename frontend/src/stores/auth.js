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

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

const formatValidationError = (detail) => {
  if (Array.isArray(detail)) {
    return detail.map((err) => {
      let msg = err.msg || ''
      if (msg.includes(': ')) {
        msg = msg.split(': ').slice(1).join(': ')
      } else if (msg.startsWith('Value error, ')) {
        msg = msg.replace('Value error, ', '')
      }
      return msg
    }).join('\n')
  }
  return detail || 'An error occurred'
}

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
        return { success: true }
      } catch (err) {
        const msg = formatValidationError(err.response?.data?.detail)
        this.error = msg
        return { success: false, error: msg }
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
        return { success: true }
      } catch (err) {
        const msg = formatValidationError(err.response?.data?.detail)
        this.error = msg
        return { success: false, error: msg }
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
        return { success: true }
      } catch (err) {
        const msg = formatValidationError(err.response?.data?.detail)
        this.error = msg
        return { success: false, error: msg }
      } finally {
        this.loading = false
      }
    },

    async resetPassword(token, password) {
      this.loading = true
      this.error = null
      try {
        await api.post('/auth/reset-password', { token, password })
        return { success: true }
      } catch (err) {
        const msg = formatValidationError(err.response?.data?.detail)
        this.error = msg
        return { success: false, error: msg }
      } finally {
        this.loading = false
      }
    },
  },
})

export { api }