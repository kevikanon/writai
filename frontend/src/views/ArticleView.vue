<template>
  <v-container v-if="article">
    <div class="d-flex justify-space-between align-center mb-4">
      <div>
        <v-btn icon variant="text" @click="goBack" class="mr-2">
          <v-icon icon="mdi-arrow-left" />
        </v-btn>
        <span class="text-h4">{{ article.title || 'Untitled' }}</span>
      </div>
      <div>
        <v-btn color="primary" @click="editArticle">Edit</v-btn>
      </div>
    </div>

    <v-chip :color="getStatusColor(article.status)" size="small" class="mb-4">
      {{ article.status }}
    </v-chip>
    <span class="text-grey ml-2">{{ article.word_count }} words · {{ article.reading_time }} min read</span>

    <v-divider class="my-4" />

    <div class="article-content" v-html="article.content"></div>

    <v-divider class="my-4" />

    <v-card v-if="article.target_keyword || article.meta_description" variant="outlined">
      <v-card-title>SEO Details</v-card-title>
      <v-card-text>
        <p v-if="article.target_keyword"><strong>Target Keyword:</strong> {{ article.target_keyword }}</p>
        <p v-if="article.meta_description"><strong>Meta Description:</strong> {{ article.meta_description }}</p>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useArticleStore } from '../stores/articles'

const route = useRoute()
const router = useRouter()
const articleStore = useArticleStore()

const article = computed(() => articleStore.currentArticle)

const getStatusColor = (status) => {
  const colors = { draft: 'grey', generated: 'success', published: 'primary' }
  return colors[status] || 'grey'
}

const goBack = () => {
  router.push('/articles')
}

const editArticle = () => {
  router.push(`/articles/${route.params.id}/edit`)
}

onMounted(() => {
  articleStore.fetchArticle(route.params.id)
})
</script>

<style scoped>
.article-content {
  line-height: 1.8;
  font-size: 1.1rem;
}
.article-content :deep(h1) { font-size: 2em; margin: 1em 0 0.5em; }
.article-content :deep(h2) { font-size: 1.5em; margin: 1em 0 0.5em; }
.article-content :deep(h3) { font-size: 1.25em; margin: 1em 0 0.5em; }
.article-content :deep(p) { margin: 0 0 1em; }
.article-content :deep(ul), .article-content :deep(ol) { padding-left: 1.5em; margin: 0 0 1em; }
.article-content :deep(blockquote) {
  border-left: 3px solid #ccc;
  padding-left: 1em;
  font-style: italic;
}
</style>