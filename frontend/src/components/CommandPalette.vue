<template>
  <v-dialog v-model="isOpen" max-width="500" :scrim="true" scrim-class="command-palette-scrim">
    <v-card class="command-palette">
      <v-text-field
        ref="searchInput"
        v-model="query"
        placeholder="Search commands..."
        variant="solo"
        density="compact"
        hide-details
        autofocus
        prepend-inner-icon="mdi-magnify"
        @keydown.down.prevent="navigateDown"
        @keydown.up.prevent="navigateUp"
        @keydown.enter.prevent="executeSelected"
        @keydown.esc="close"
      />

      <v-list v-if="filteredCommands.length > 0" density="compact" class="py-0">
        <v-list-item
          v-for="(cmd, index) in filteredCommands"
          :key="cmd.id"
          :active="index === selectedIndex"
          :value="cmd"
          @click="execute(cmd)"
          @mouseover="selectedIndex = index"
        >
          <template v-slot:prepend>
            <v-icon :icon="cmd.icon" size="small" />
          </template>
          <v-list-item-title>{{ cmd.title }}</v-list-item-title>
          <v-list-item-subtitle v-if="cmd.description">{{ cmd.description }}</v-list-item-subtitle>
          <template v-slot:append v-if="index === selectedIndex">
            <v-icon icon="mdi-arrow-right" size="small" />
          </template>
        </v-list-item>
      </v-list>

      <div v-else-if="query" class="pa-4 text-center text-grey">
        No commands found
      </div>

      <v-divider />

      <div class="pa-2 text-caption text-grey d-flex justify-space-between">
        <span><kbd>↑↓</kbd> Navigate</span>
        <span><kbd>Enter</kbd> Select</span>
        <span><kbd>Esc</kbd> Close</span>
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isOpen = ref(false)
const query = ref('')
const selectedIndex = ref(0)
const searchInput = ref(null)

const commands = [
  { id: 'craft-magic', title: 'Magic Writer', description: 'Generate article from keyword', icon: 'mdi-magic-staff', action: () => router.push('/craft?tab=magic') },
  { id: 'craft-bulk', title: 'Bulk Writer', description: 'Generate multiple articles', icon: 'mdi-file-document-multiple', action: () => router.push('/craft?tab=bulk') },
  { id: 'craft-short', title: 'Short Info Writer', description: 'Brief info to article', icon: 'mdi-text-short', action: () => router.push('/craft?tab=short_info') },
  { id: 'craft-outline', title: 'Outline to Article', description: 'Convert outline to full article', icon: 'mdi-format-list-bulleted', action: () => router.push('/craft?tab=outline') },
  { id: 'craft-biography', title: 'Biography Writer', description: 'Generate biography', icon: 'mdi-account', action: () => router.push('/craft?tab=biography') },
  { id: 'craft-manual', title: 'Manual Writer', description: 'Write your own content', icon: 'mdi-pencil', action: () => router.push('/craft?tab=manual') },
  { id: 'articles', title: 'My Articles', description: 'View all articles', icon: 'mdi-file-document', action: () => router.push('/articles') },
  { id: 'new-article', title: 'New Article', description: 'Create blank article', icon: 'mdi-plus', action: () => createNewArticle() },
  { id: 'settings', title: 'Settings', description: 'API keys & publishing', icon: 'mdi-cog', action: () => router.push('/settings') },
]

const filteredCommands = computed(() => {
  if (!query.value) return commands
  const q = query.value.toLowerCase()
  return commands.filter(cmd => 
    cmd.title.toLowerCase().includes(q) || 
    cmd.description?.toLowerCase().includes(q)
  )
})

const navigateDown = () => {
  if (selectedIndex.value < filteredCommands.value.length - 1) {
    selectedIndex.value++
  }
}

const navigateUp = () => {
  if (selectedIndex.value > 0) {
    selectedIndex.value--
  }
}

const execute = (cmd) => {
  cmd.action()
  close()
}

const executeSelected = () => {
  if (filteredCommands.value[selectedIndex.value]) {
    execute(filteredCommands.value[selectedIndex.value])
  }
}

const close = () => {
  isOpen.value = false
  query.value = ''
  selectedIndex.value = 0
}

const createNewArticle = async () => {
  const { api } = await import('../stores/auth')
  try {
    const { data } = await api.post('/articles', { title: 'Untitled', target_keyword: '' })
    router.push(`/articles/${data.id}`)
  } catch (e) {
    console.error('Failed to create article:', e)
  }
}

const handleKeydown = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    isOpen.value = true
    nextTick(() => {
      searchInput.value?.focus()
    })
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

defineExpose({ open: () => { isOpen.value = true } })
</script>

<style scoped>
.command-palette {
  border-radius: 8px;
}
.command-palette-scrim {
  background-color: rgba(0, 0, 0, 0.5);
}
kbd {
  background: #eee;
  border-radius: 3px;
  padding: 1px 4px;
  font-size: 11px;
  font-family: monospace;
}
</style>