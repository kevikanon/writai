<template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-4">
      <h1 class="text-h4">Articles</h1>
      <div>
        <v-btn
          color="error"
          :disabled="selectedArticles.length === 0"
          @click="deleteSelected"
        >
          Delete Selected ({{ selectedArticles.length }})
        </v-btn>
        <v-btn color="primary" class="ml-2" @click="goToCraft">Craft New Article</v-btn>
      </div>
    </div>

    <v-alert v-if="articleStore.error" type="error" class="mb-4">
      {{ articleStore.error }}
    </v-alert>

    <v-progress-linear v-if="articleStore.loading" indeterminate />

    <v-card v-if="!articleStore.loading && articleStore.articles.length === 0">
      <v-card-text class="text-center py-8">
        <p class="text-h6 text-grey mb-4">No articles yet</p>
        <v-btn color="primary" @click="goToCraft">Create First Article</v-btn>
      </v-card-text>
    </v-card>

    <v-card v-else>
      <v-data-table
        v-model="selectedArticles"
        :headers="headers"
        :items="articleStore.articles"
        :items-per-page="10"
        show-select
        class="elevation-0"
      >
        <template v-slot:item.title="{ item }">
          <a href="#" class="text-primary font-weight-medium" @click.prevent="viewArticle(item)">
            {{ item.title || 'Untitled' }}
          </a>
        </template>

        <template v-slot:item.target_keyword="{ item }">
          <span v-if="item.target_keyword">{{ item.target_keyword }}</span>
          <span v-else class="text-grey">-</span>
        </template>

        <template v-slot:item.status="{ item }">
          <v-chip :color="getStatusColor(item.status)" size="small">
            {{ item.status }}
          </v-chip>
        </template>

        <template v-slot:item.word_count="{ item }">
          {{ item.word_count }} words
        </template>

        <template v-slot:item.updated_at="{ item }">
          {{ formatDate(item.updated_at) }}
        </template>

        <template v-slot:item.actions="{ item }">
          <div class="d-flex ga-1">
            <v-btn icon size="small" variant="text" @click="viewArticle(item)" title="View">
              <v-icon icon="mdi-eye" size="18" />
            </v-btn>
            <v-btn icon size="small" variant="text" @click="editArticle(item)" title="Edit">
              <v-icon icon="mdi-pencil" size="18" />
            </v-btn>
          </div>
        </template>
      </v-data-table>

      <v-pagination
        v-if="articleStore.pagination.total > articleStore.pagination.per_page"
        v-model="page"
        :length="totalPages"
        @update:model-value="fetchArticles"
        class="mt-4"
      />
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useArticleStore } from '../stores/articles'
import { useToast } from '../composables/useToast'

const router = useRouter()
const articleStore = useArticleStore()
const { success, error } = useToast()

const page = ref(1)
const selectedArticles = ref([])

const headers = [
  { title: 'Title', key: 'title', sortable: true },
  { title: 'Keyword', key: 'target_keyword', sortable: false },
  { title: 'Status', key: 'status', sortable: true, width: '100px' },
  { title: 'Words', key: 'word_count', sortable: true, width: '100px' },
  { title: 'Updated', key: 'updated_at', sortable: true, width: '150px' },
  { title: 'Actions', key: 'actions', sortable: false, width: '100px', align: 'center' },
]

const totalPages = computed(() =>
  Math.ceil(articleStore.pagination.total / articleStore.pagination.per_page)
)

const getStatusColor = (status) => {
  const colors = { draft: 'grey', generated: 'success', published: 'primary' }
  return colors[status] || 'grey'
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric'
  })
}

const goToCraft = () => {
  router.push('/craft')
}

const viewArticle = (article) => {
  router.push(`/articles/${article.id}`)
}

const editArticle = (article) => {
  router.push(`/articles/${article.id}/edit`)
}

const deleteSelected = async () => {
  if (selectedArticles.value.length === 0) return

  let validArticles = []

  if (typeof selectedArticles.value[0] === 'string') {
    validArticles = selectedArticles.value.map(id => ({
      id,
      title: articleStore.articles.find(a => a.id === id)?.title || 'Untitled'
    }))
  } else {
    validArticles = selectedArticles.value.filter(a => a.id && a.id !== 'undefined')
  }

  console.log('Valid articles to delete:', validArticles)

  if (validArticles.length === 0) {
    error('Invalid article selection')
    return
  }

  const count = validArticles.length
  const message = count === 1
    ? `Delete "${validArticles[0].title || 'Untitled'}"?`
    : `Delete ${count} articles?`

  if (confirm(message)) {
    let deletedCount = 0
    for (const article of validArticles) {
      console.log('Deleting article ID:', article.id)
      const result = await articleStore.deleteArticle(article.id)
      if (result) {
        deletedCount++
      }
    }
    if (deletedCount > 0) {
      success(`${deletedCount} article(s) deleted`)
      selectedArticles.value = []
      fetchArticles()
    } else {
      error('Failed to delete articles')
    }
  }
}

const fetchArticles = () => {
  articleStore.fetchArticles(page.value)
}

onMounted(() => {
  fetchArticles()
})
</script>