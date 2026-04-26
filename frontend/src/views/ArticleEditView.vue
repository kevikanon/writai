<template>
  <v-container v-if="article">
    <div class="d-flex justify-space-between align-center mb-4">
      <div>
        <v-btn icon variant="text" @click="goBack" class="mr-2">
          <v-icon icon="mdi-arrow-left" />
        </v-btn>
        <span class="text-h4">Edit Article</span>
      </div>
      <div>
        <v-btn color="primary" @click="save" :loading="saving">
          Save
        </v-btn>
        <v-btn color="error" class="ml-2" @click="deleteArticle">Delete</v-btn>
      </div>
    </div>

    <v-alert v-if="articleStore.error" type="error" class="mb-4">
      {{ articleStore.error }}
    </v-alert>

    <v-row>
      <v-col cols="12" md="8">
        <v-text-field v-model="article.title" label="Title" class="mb-2" />
        <WysiwygEditor v-model="article.content" />
      </v-col>
      <v-col cols="12" md="4">
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
import { useToast } from '../composables/useToast'
import WysiwygEditor from '../components/WysiwygEditor.vue'

const route = useRoute()
const router = useRouter()
const articleStore = useArticleStore()
const { success, error } = useToast()

const article = computed(() => articleStore.currentArticle)
const saving = ref(false)

const goBack = () => {
  router.push(`/articles/${route.params.id}`)
}

const save = async () => {
  saving.value = true
  try {
    await articleStore.updateArticle(route.params.id, {
      title: article.value.title,
      content: article.value.content,
      meta_title: article.value.meta_title,
      meta_description: article.value.meta_description,
    })
    success('Article saved')
  } catch (e) {
    error(e.response?.data?.detail || 'Failed to save')
  } finally {
    saving.value = false
  }
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