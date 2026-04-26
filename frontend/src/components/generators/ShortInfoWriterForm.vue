<template>
  <v-card>
    <v-card-title>Short Info Writer</v-card-title>
    <v-card-text>
      <p class="text-body-2 text-grey mb-4">
        Generate a concise article (300-500 words) from brief information.
      </p>

      <v-form ref="form" @submit.prevent="generate">
        <v-text-field
          v-model="form.target_keywords"
          label="Main Topic / Keyword"
          placeholder="e.g., coffee benefits"
          :rules="[rules.required]"
        />

        <v-textarea
          v-model="form.short_info"
          label="Brief Information"
          placeholder="Key points or information to expand on..."
          rows="3"
          :rules="[rules.required]"
        />

        <v-text-field
          v-model="form.title"
          label="Custom Title (optional)"
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
          Generate Article
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
  target_keywords: '',
  short_info: '',
  title: '',
  tone: 'professional',
  provider: 'openai',
  custom_prompt: '',
})

const loading = ref(false)
const formRef = ref(null)

const tones = ['professional', 'casual', 'formal', 'friendly', 'authoritative']
const providers = ['openai', 'anthropic', 'google', 'mistral']

const rules = {
  required: (v) => !!v || 'Required',
}

const generate = async () => {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  loading.value = true
  try {
    const article = await articleStore.createArticle({
      title: form.title || 'Untitled',
      target_keyword: form.target_keywords,
    })

    if (article) {
      const generated = await articleStore.generateArticle(article.id, {
        generator_type: 'short_info',
        provider: form.provider,
        target_keywords: form.target_keywords,
        title: form.title || undefined,
        word_count_min: 300,
        word_count_max: 500,
        tone: form.tone,
        custom_prompt: form.short_info + (form.custom_prompt ? '\n' + form.custom_prompt : ''),
      })

      if (generated) {
        success('Article generated successfully!')
        emit('generated', generated)
      }
    }
  } catch (e) {
    error(e.response?.data?.detail || 'Generation failed')
  } finally {
    loading.value = false
  }
}
</script>