<template>
  <v-card>
    <v-card-title>Manual Writer</v-card-title>
    <v-card-text>
      <p class="text-body-2 text-grey mb-4">
        Create an article manually. No AI generation - write your own content.
      </p>

      <v-form ref="formRef" @submit.prevent="generate">
        <v-text-field
          v-model="form.title"
          label="Article Title"
          placeholder="Enter article title"
          :rules="[rules.required]"
        />

        <v-textarea
          v-model="form.meta_description"
          label="Meta Description (optional)"
          rows="2"
          counter="160"
          hint="Max 160 characters for SEO"
          class="mb-4"
        />

        <WysiwygEditor v-model="form.content" class="mb-4" />

        <v-btn
          type="submit"
          color="primary"
          :loading="loading"
          :disabled="loading"
          block
        >
          Save Article
        </v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useArticleStore } from '../../stores/articles'
import { useToast } from '../../composables/useToast'
import WysiwygEditor from '../../components/WysiwygEditor.vue'

const emit = defineEmits(['generated'])
const router = useRouter()
const articleStore = useArticleStore()
const { success, error } = useToast()

const form = reactive({
  title: '',
  content: '',
  meta_description: '',
})

const loading = ref(false)
const formRef = ref(null)

const rules = {
  required: (v) => !!v || 'Required',
}

const generate = async () => {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  loading.value = true
  try {
    const article = await articleStore.createArticle({
      title: form.title,
      content: form.content,
      meta_description: form.meta_description || undefined,
    })

    if (article) {
      success('Article saved successfully!')
      emit('generated', article)
    }
  } catch (e) {
    error(e.response?.data?.detail || 'Failed to save article')
  } finally {
    loading.value = false
  }
}
</script>