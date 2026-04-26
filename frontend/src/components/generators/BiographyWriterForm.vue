<template>
  <v-card>
    <v-card-title>Biography Writer</v-card-title>
    <v-card-text>
      <p class="text-body-2 text-grey mb-4">
        Generate a biography article about a person.
      </p>

      <v-form ref="formRef" @submit.prevent="generate">
        <v-text-field
          v-model="form.subject_name"
          label="Person's Name"
          placeholder="e.g., Elon Musk"
          :rules="[rules.required]"
        />

        <v-text-field
          v-model="form.profession"
          label="Profession / Claim to Fame"
          placeholder="e.g., CEO of Tesla and SpaceX"
        />

        <v-textarea
          v-model="form.life_events"
          label="Key Life Events (optional)"
          placeholder="Key events to include (comma or line separated)"
          rows="2"
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
          v-model="form.chronological_timeline"
          label="Use chronological timeline format"
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
          Generate Biography
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
  subject_name: '',
  profession: '',
  life_events: '',
  tone: 'professional',
  provider: 'openai',
  word_count_min: 800,
  word_count_max: 1500,
  chronological_timeline: false,
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

  const keywords = [form.subject_name]
  if (form.life_events) {
    const events = form.life_events
      .split(/[\n,]/)
      .map((e) => e.trim())
      .filter((e) => e)
    keywords.push(...events)
  }

  loading.value = true
  try {
    const article = await articleStore.createArticle({
      title: `Biography of ${form.subject_name}`,
      target_keyword: form.subject_name,
    })

    if (article) {
      const generated = await articleStore.generateArticle(article.id, {
        generator_type: 'biography',
        provider: form.provider,
        target_keywords: keywords,
        subject_name: form.subject_name,
        profession: form.profession || undefined,
        word_count_min: form.word_count_min,
        word_count_max: form.word_count_max,
        tone: form.tone,
        chronological_timeline: form.chronological_timeline,
        custom_prompt: form.custom_prompt || undefined,
      })

      if (generated) {
        success('Biography generated successfully!')
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