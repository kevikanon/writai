import { defineStore } from 'pinia'
import { api } from './auth'

export const useArticleStore = defineStore('articles', {
  state: () => ({
    articles: [],
    currentArticle: null,
    loading: false,
    error: null,
    pagination: {
      page: 1,
      per_page: 10,
      total: 0,
    },
  }),

  actions: {
    async fetchArticles(page = 1, per_page = 10) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.get('/articles', {
          params: { page, per_page },
        })
        this.articles = data.items
        this.pagination = {
          page: data.page,
          per_page: data.per_page,
          total: data.total,
        }
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to fetch articles'
      } finally {
        this.loading = false
      }
    },

    async fetchArticle(id) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.get(`/articles/${id}`)
        this.currentArticle = data
        return data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to fetch article'
        return null
      } finally {
        this.loading = false
      }
    },

    async createArticle(articleData) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.post('/articles', articleData)
        this.articles.unshift(data)
        return data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to create article'
        return null
      } finally {
        this.loading = false
      }
    },

    async updateArticle(id, articleData) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.patch(`/articles/${id}`, articleData)
        const index = this.articles.findIndex((a) => a.id === id)
        if (index !== -1) {
          this.articles[index] = data
        }
        return data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to update article'
        return null
      } finally {
        this.loading = false
      }
    },

    async deleteArticle(id) {
      if (!id || id === 'undefined') {
        console.error('Invalid article ID:', id)
        return false
      }
      this.loading = true
      this.error = null
      try {
        const response = await api.delete(`/articles/${id}`)
        this.articles = this.articles.filter((a) => a.id !== id)
        return true
      } catch (err) {
        console.error('Delete error:', err)
        this.error = err.response?.data?.detail || 'Failed to delete article'
        return false
      } finally {
        this.loading = false
      }
    },

    async generateArticle(id, params) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.post(`/articles/${id}/generate`, params)
        this.currentArticle = data
        return data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Generation failed'
        return null
      } finally {
        this.loading = false
      }
    },
  },
})