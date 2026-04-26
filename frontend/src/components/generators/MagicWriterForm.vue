<template>
  <v-card>
    <v-card-title>Magic Writer</v-card-title>
    <v-card-text>
      <p class="text-body-2 text-grey mb-4">
        Generate a complete SEO-optimized article from a single keyword.
      </p>

      <v-form ref="form" @submit.prevent="generate">
        <v-text-field
          v-model="form.target_keywords"
          label="Target Keyword"
          placeholder="e.g., best coffee makers 2024"
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

        <v-row>
          <v-col cols="6">
            <v-text-field
              v-model.number="form.num_subheadings"
              label="Subheadings"
              type="number"
              min="1"
            />
          </v-col>
          <v-col cols="6">
            <v-text-field
              v-model.number="form.num_faqs"
              label="FAQs"
              type="number"
              min="0"
            />
          </v-col>
        </v-row>

        <v-checkbox
          v-model="form.pros_cons"
          label="Include Pros & Cons section"
        />

        <v-checkbox
          v-model="form.alternatives"
          label="Include Alternatives section"
        />

        <v-textarea
          v-model="form.custom_prompt"
          label="Custom Instructions (optional)"
          rows="2"
          placeholder="Any specific requirements..."
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
  title: '',
  tone: 'professional',
  provider: 'openai',
  word_count_min: 800,
  word_count_max: 1500,
  num_subheadings: 5,
  num_faqs: 3,
  pros_cons: false,
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

  loading.value = true
  try {
    const article = await articleStore.createArticle({
      title: form.title || 'Untitled',
      target_keyword: form.target_keywords,
    })

    if (article) {
      const generated = await articleStore.generateArticle(article.id, {
        generator_type: 'magic',
        provider: form.provider,
        target_keywords: form.target_keywords,
        title: form.title || undefined,
        word_count_min: form.word_count_min,
        word_count_max: form.word_count_max,
        tone: form.tone,
        num_subheadings: form.num_subheadings,
        num_faqs: form.num_faqs,
        pros_cons: form.pros_cons,
        alternatives: form.alternatives,
        custom_prompt: form.custom_prompt || undefined,
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