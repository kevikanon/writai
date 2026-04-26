<template>
  <v-card>
    <v-card-title>Manual Writer</v-card-title>
    <v-card-text>
      <p class="text-body-2 text-grey mb-4">
        Create an article manually. No AI generation - write your own content.
      </p>

      <v-form ref="form" @submit.prevent="generate">
        <v-text-field
          v-model="form.title"
          label="Article Title"
          placeholder="Enter article title"
          :rules="[rules.required]"
        />

        <v-text-field
          v-model="form.target_keyword"
          label="Target Keyword (optional)"
          placeholder="Primary SEO keyword"
        />

        <v-row>
          <v-col cols="12" md="6">
            <v-select
              v-model="form.tone"
              :items="tones"
              label="Tone"
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-text-field
              v-model.number="form.word_count_target"
              label="Target Word Count"
              type="number"
              min="0"
            />
          </v-col>
        </v-row>

        <v-textarea
          v-model="form.content"
          label="Article Content"
          placeholder="Write your article content here..."
          rows="15"
        />

        <v-textarea
          v-model="form.meta_description"
          label="Meta Description (optional)"
          rows="2"
          counter="160"
          hint="Max 160 characters for SEO"
        />

        <v-btn
          type="submit"
          color="primary"
          :loading="loading"
          :disabled="loading"
          block
          class="mt-4"
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

const emit = defineEmits(['generated'])
const router = useRouter()
const articleStore = useArticleStore()
const { success, error } = useToast()

const form = reactive({
  title: '',
  target_keyword: '',
  tone: 'professional',
  word_count_target: null,
  content: '',
  meta_description: '',
})

const loading = ref(false)
const formRef = ref(null)

const tones = ['professional', 'casual', 'formal', 'friendly', 'authoritative']

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
      target_keyword: form.target_keyword || undefined,
      tone: form.tone,
      word_count_target: form.word_count_target || undefined,
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