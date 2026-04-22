<template>
  <v-container>
    <div class="d-flex justify-space-between align-center mb-4">
      <h1 class="text-h4">Articles</h1>
      <v-btn color="primary" @click="createNew">New Article</v-btn>
    </div>

    <v-alert v-if="articleStore.error" type="error" class="mb-4">
      {{ articleStore.error }}
    </v-alert>

    <v-progress-linear v-if="articleStore.loading" indeterminate />

    <v-row v-if="!articleStore.loading && articleStore.articles.length === 0">
      <v-col cols="12" class="text-center">
        <p class="text-h6 text-grey">No articles yet</p>
        <v-btn color="primary" @click="createNew">Create First Article</v-btn>
      </v-col>
    </v-row>

    <v-row v-else>
      <v-col v-for="article in articleStore.articles" :key="article.id" cols="12" md="6" lg="4">
        <v-card :to="`/articles/${article.id}`" class="h-100">
          <v-card-title>{{ article.title || 'Untitled' }}</v-card-title>
          <v-card-subtitle>{{ article.target_keyword }}</v-card-subtitle>
          <v-card-text>
            <v-chip :color="getStatusColor(article.status)" size="small">
              {{ article.status }}
            </v-chip>
            <span class="ml-2">{{ article.word_count }} words</span>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-pagination
      v-if="articleStore.pagination.total > articleStore.pagination.per_page"
      v-model="page"
      :length="totalPages"
      @update:model-value="fetchArticles"
    />
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useArticleStore } from '../stores/articles'

const router = useRouter()
const articleStore = useArticleStore()

const page = computed(() => articleStore.pagination.page)
const totalPages = computed(() =>
  Math.ceil(articleStore.pagination.total / articleStore.pagination.per_page)
)

const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    generated: 'success',
    published: 'primary',
  }
  return colors[status] || 'grey'
}

const createNew = async () => {
  const article = await articleStore.createArticle({
    title: 'Untitled',
    target_keyword: '',
  })
  if (article) {
    router.push(`/articles/${article.id}`)
  }
}

const fetchArticles = () => {
  articleStore.fetchArticles(page.value)
}

onMounted(() => {
  fetchArticles()
})
</script>