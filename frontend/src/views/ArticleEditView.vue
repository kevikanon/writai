<template>
  <v-container v-if="article">
    <div class="d-flex justify-space-between align-center mb-4">
      <h1 class="text-h4">Edit Article</h1>
      <div>
        <v-btn color="primary" @click="generate" :loading="articleStore.loading">
          Generate
        </v-btn>
        <v-btn color="success" class="ml-2" @click="publish">Publish</v-btn>
        <v-btn color="error" class="ml-2" @click="deleteArticle">Delete</v-btn>
      </div>
    </div>

    <v-alert v-if="articleStore.error" type="error" class="mb-4">
      {{ articleStore.error }}
    </v-alert>

    <v-row>
      <v-col cols="12" md="8">
        <v-text-field v-model="article.title" label="Title" class="mb-2" />
        <v-textarea
          v-model="article.content"
          label="Content"
          rows="20"
          class="mb-2"
        />
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="mb-4">
          <v-card-title>Settings</v-card-title>
          <v-card-text>
            <v-text-field v-model="article.target_keyword" label="Target Keyword" />
            <v-select
              v-model="article.article_type"
              :items="articleTypes"
              label="Article Type"
            />
            <v-text-field v-model.number="article.word_count_target" label="Word Count" type="number" />
            <v-select
              v-model="article.tone"
              :items="tones"
              label="Tone"
            />
          </v-card-text>
        </v-card>

        <v-card class="mb-4">
          <v-card-title>SEO</v-card-title>
          <v-card-text>
            <v-text-field v-model="article.meta_title" label="Meta Title" />
            <v-textarea
              v-model="article.meta_description"
              label="Meta Description"
              rows="3"
            />
          </v-card-text>
        </v-card>

        <v-card>
          <v-card-title>Details</v-card-title>
          <v-card-text>
            <p>Status: {{ article.status }}</p>
            <p>Words: {{ article.word_count }}</p>
            <p>Reading time: {{ article.reading_time }} min</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useArticleStore } from '../stores/articles'

const route = useRoute()
const router = useRouter()
const articleStore = useArticleStore()

const article = computed(() => articleStore.currentArticle)

const articleTypes = ['magic', 'bulk', 'short_info', 'outline', 'biography', 'manual']
const tones = ['professional', 'casual', 'formal', 'friendly', 'authoritative']

const generate = async () => {
  await articleStore.generateArticle(route.params.id, {
    generator_type: article.value?.article_type || 'magic',
  })
}

const publish = async () => {
  // TODO: Implement publish
}

const deleteArticle = async () => {
  if (confirm('Are you sure?')) {
    await articleStore.deleteArticle(route.params.id)
    router.push('/articles')
  }
}

onMounted(() => {
  articleStore.fetchArticle(route.params.id)
})
</script>