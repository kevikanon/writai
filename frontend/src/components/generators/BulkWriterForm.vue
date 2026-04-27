<template>
  <v-card>
    <v-card-title>Bulk Writer</v-card-title>
    <v-card-text>
      <p class="text-body-2 text-grey mb-4">
        Generate multiple SEO articles from a list of keywords (comma or line separated).
      </p>

      <v-form ref="formRef" @submit.prevent="generate">
        <v-textarea
          v-model="form.keywords"
          label="Keywords"
          placeholder="Enter keywords (one per line or comma separated)"
          rows="4"
          :rules="[rules.required]"
        />

        <v-text-field
          v-model="form.title"
          label="Custom Title (optional)"
          placeholder="Leave empty for AI-generated title"
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
            <v-select
              v-model="form.provider"
              :items="providers"
              label="AI Provider"
            />
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="6">
            <v-text-field
              v-model.number="form.word_count_min"
              label="Min Words"
              type="number"
              min="100"
            />
          </v-col>
          <v-col cols="6">
            <v-text-field
              v-model.number="form.word_count_max"
              label="Max Words"
              type="number"
              min="100"
            />
          </v-col>
        </v-row>

        <v-checkbox
          v-model="form.alternatives"
          label="Include Alternatives section"
        />

        <v-textarea
          v-model="form.custom_prompt"
          label="Custom Instructions (optional)"
          rows="2"
        />

        <v-btn
          type="submit"
          color="primary"
          :loading="loading"
          :disabled="loading"
          block
        >
          Generate Articles
        </v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useArticleStore } from '../../stores/articles'
import { useToast } from '../../composables/useToast'

const emit = defineEmits(['generated'])
const articleStore = useArticleStore()
const { success, error } = useToast()

const form = reactive({
  keywords: '',
  title: '',
  tone: 'professional',
  provider: 'openai',
  word_count_min: 800,
  word_count_max: 1500,
  alternatives: false,
  custom_prompt: '',
})

const loading = ref(false)
const formRef = ref(null)

const tones = ['professional', 'casual', 'formal', 'friendly', 'authoritative', 'humorous']
const providers = ['openai', 'anthropic', 'google', 'mistral']

const rules = {
  required: (v) => !!v || 'Required',
}

const generate = async () => {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  const firstKeyword = form.keywords.split(/[\n,]/).map((k) => k.trim()).filter((k) => k)[0]

  if (!firstKeyword) {
    error('Please enter at least one keyword')
    return
  }

  loading.value = true
  try {
    const keywords = form.keywords
      .split(/[\n,]/)
      .map((k) => k.trim())
      .filter((k) => k)

    for (let i = 0; i < keywords.length; i++) {
      const keyword = keywords[i]
      const article = await articleStore.createArticle({
        title: form.title ? `${form.title} - ${keyword}` : keyword,
        target_keyword: keyword,
      })

      if (article) {
        const generated = await articleStore.generateArticle(article.id, {
          generator_type: 'magic',
          provider: form.provider,
          target_keywords: keyword,
          title: article.title,
          word_count_min: form.word_count_min,
          word_count_max: form.word_count_max,
          tone: form.tone,
          alternatives: form.alternatives,
          custom_prompt: form.custom_prompt || undefined,
        })

        if (generated && i === 0) {
          emit('generated', generated)
        }
      }
    }

    success(`Generated ${keywords.length} articles successfully!`)
  } catch (e) {
    error(e.response?.data?.detail || 'Generation failed')
  } finally {
    loading.value = false
  }
}
</script>