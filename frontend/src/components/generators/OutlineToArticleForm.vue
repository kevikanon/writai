<template>
  <v-card>
    <v-card-title>Outline to Article</v-card-title>
    <v-card-text>
      <p class="text-body-2 text-grey mb-4">
        Convert an outline structure into a full SEO-optimized article.
      </p>

      <v-form ref="formRef" @submit.prevent="generate">
        <v-text-field
          v-model="form.target_keywords"
          label="Main Keyword"
          placeholder="e.g., coffee makers"
          :rules="[rules.required]"
        />

        <div class="mb-4">
          <div class="d-flex justify-space-between align-center mb-2">
            <span class="text-subtitle-1">Outline Sections</span>
            <v-btn size="small" variant="outlined" @click="addSection">Add Section</v-btn>
          </div>

          <v-card
            v-for="(section, index) in form.outline.sections"
            :key="index"
            variant="outlined"
            class="mb-2 pa-3"
          >
            <v-row dense>
              <v-col cols="12">
                <v-text-field
                  v-model="section.heading"
                  label="Section Heading (H2)"
                  density="compact"
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="section.subheadings"
                  label="Subheadings (comma or line separated)"
                  rows="2"
                  density="compact"
                  placeholder="e.g., Types of coffee makers, Best brands, How to choose"
                />
              </v-col>
              <v-col cols="12" class="text-right">
                <v-btn size="small" color="error" variant="text" @click="removeSection(index)">
                  Remove
                </v-btn>
              </v-col>
            </v-row>
          </v-card>
        </div>

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
          v-model="form.num_faqs"
          :true-value="3"
          :false-value="0"
          label="Include FAQ section"
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
  outline: {
    sections: [{ heading: '', subheadings: '' }],
  },
  title: '',
  tone: 'professional',
  provider: 'openai',
  word_count_min: 800,
  word_count_max: 1500,
  num_faqs: 3,
  custom_prompt: '',
})

const loading = ref(false)
const formRef = ref(null)

const tones = ['professional', 'casual', 'formal', 'friendly', 'authoritative']
const providers = ['openai', 'anthropic', 'google', 'mistral']

const rules = {
  required: (v) => !!v || 'Required',
}

const addSection = () => {
  form.outline.sections.push({ heading: '', subheadings: '' })
}

const removeSection = (index) => {
  form.outline.sections.splice(index, 1)
}

const generate = async () => {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  const hasContent = form.outline.sections.some(
    (s) => s.heading || s.subheadings
  )
  if (!hasContent) {
    error('Please add at least one outline section')
    return
  }

  const outline = {
    sections: form.outline.sections
      .filter((s) => s.heading)
      .map((s) => ({
        heading: s.heading,
        subheadings: s.subheadings
          ? s.subheadings.split(/[\n,]/).map((sh) => sh.trim()).filter((sh) => sh)
          : [],
      })),
  }

  loading.value = true
  try {
    const article = await articleStore.createArticle({
      title: form.title || 'Untitled',
      target_keyword: form.target_keywords,
    })

    if (article) {
      const generated = await articleStore.generateArticle(article.id, {
        generator_type: 'outline_to_article',
        provider: form.provider,
        target_keywords: form.target_keywords,
        title: form.title || undefined,
        word_count_min: form.word_count_min,
        word_count_max: form.word_count_max,
        tone: form.tone,
        num_faqs: form.num_faqs,
        outline,
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