<template>
  <v-container>
    <h1 class="text-h4 mb-4">Craft Articles</h1>

    <v-tabs v-model="activeTab" color="primary">
      <v-tab value="magic">Magic Writer</v-tab>
      <v-tab value="bulk">Bulk Writer</v-tab>
      <v-tab value="short_info">Short Info</v-tab>
      <v-tab value="outline">Outline to Article</v-tab>
      <v-tab value="biography">Biography</v-tab>
      <v-tab value="manual">Manual</v-tab>
    </v-tabs>

    <v-window v-model="activeTab" class="mt-4">
      <v-window-item value="magic">
        <MagicWriterForm @generated="onGenerated" />
      </v-window-item>

      <v-window-item value="bulk">
        <BulkWriterForm @generated="onGenerated" />
      </v-window-item>

      <v-window-item value="short_info">
        <ShortInfoWriterForm @generated="onGenerated" />
      </v-window-item>

      <v-window-item value="outline">
        <OutlineToArticleForm @generated="onGenerated" />
      </v-window-item>

      <v-window-item value="biography">
        <BiographyWriterForm @generated="onGenerated" />
      </v-window-item>

      <v-window-item value="manual">
        <ManualWriterForm @generated="onGenerated" />
      </v-window-item>
    </v-window>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import MagicWriterForm from '../components/generators/MagicWriterForm.vue'
import BulkWriterForm from '../components/generators/BulkWriterForm.vue'
import ShortInfoWriterForm from '../components/generators/ShortInfoWriterForm.vue'
import OutlineToArticleForm from '../components/generators/OutlineToArticleForm.vue'
import BiographyWriterForm from '../components/generators/BiographyWriterForm.vue'
import ManualWriterForm from '../components/generators/ManualWriterForm.vue'

const router = useRouter()
const route = useRoute()
const activeTab = ref('magic')

onMounted(() => {
  if (route.query.tab) {
    activeTab.value = route.query.tab
  }
})

const onGenerated = (article) => {
  router.push(`/articles/${article.id}`)
}
</script>