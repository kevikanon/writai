<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="8">
        <h1 class="text-h4 mb-4">Settings</h1>
        
        <v-card class="mb-4">
          <v-card-title>Profile</v-card-title>
          <v-card-text>
            <v-text-field v-model="name" label="Name" />
            <v-text-field v-model="email" label="Email" disabled />
          </v-card-text>
        </v-card>

        <v-card class="mb-4">
          <v-card-title>API Keys</v-card-title>
          <v-card-text>
            <v-alert v-if="apiKeyError" type="error" class="mb-2">{{ apiKeyError }}</v-alert>
            <v-list>
              <v-list-item v-for="key in apiKeys" :key="key.id">
                <v-list-item-title>{{ key.provider }}</v-list-item-title>
                <v-list-item-subtitle>******{{ key.key_hash?.slice(-4) }}</v-list-item-subtitle>
                <template v-slot:append>
                  <v-btn icon="mdi-delete" variant="text" @click="deleteKey(key.id)" />
                </template>
              </v-list-item>
            </v-list>
            <v-btn color="primary" @click="showAddKeyDialog = true">Add Key</v-btn>
          </v-card-text>
        </v-card>

        <v-card>
          <v-card-title>Publishing</v-card-title>
          <v-card-text>
            <v-alert v-if="publishError" type="error" class="mb-2">{{ publishError }}</v-alert>
            <v-list>
              <v-list-item v-for="config in publishingConfigs" :key="config.id">
                <v-list-item-title>{{ config.name }}</v-list-item-title>
                <v-list-item-subtitle>{{ config.platform }}</v-list-item-subtitle>
                <template v-slot:append>
                  <v-btn icon="mdi-delete" variant="text" @click="deleteConfig(config.id)" />
                </template>
              </v-list-item>
            </v-list>
            <v-btn color="primary" @click="showAddConfigDialog = true">Add Config</v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="showAddKeyDialog" max-width="400">
      <v-card>
        <v-card-title>Add API Key</v-card-title>
        <v-card-text>
          <v-select v-model="newKeyProvider" :items="providers" label="Provider" />
          <v-text-field v-model="newKey" label="API Key" type="password" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showAddKeyDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="addApiKey">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showAddConfigDialog" max-width="400">
      <v-card>
        <v-card-title>Add Publishing Config</v-card-title>
        <v-card-text>
          <v-text-field v-model="newConfigName" label="Name" />
          <v-select v-model="newConfigPlatform" :items="platforms" label="Platform" />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showAddConfigDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="addPublishingConfig">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { api } from '../stores/auth'

const authStore = useAuthStore()
const name = computed(() => authStore.user?.name || '')
const email = computed(() => authStore.user?.email || '')

const apiKeys = ref([])
const apiKeyError = ref('')
const showAddKeyDialog = ref(false)
const newKeyProvider = ref('openai')
const newKey = ref('')
const providers = ['openai', 'anthropic', 'google', 'mistral']

const publishingConfigs = ref([])
const publishError = ref('')
const showAddConfigDialog = ref(false)
const newConfigName = ref('')
const newConfigPlatform = ref('wordpress')
const platforms = ['wordpress', 'blogger', 'shopify', 'webhook']

const fetchApiKeys = async () => {
  try {
    const { data } = await api.get('/api-keys')
    apiKeys.value = data
  } catch (e) {
    apiKeyError.value = e.response?.data?.detail || 'Failed to fetch API keys'
  }
}

const addApiKey = async () => {
  try {
    await api.post('/api-keys', { provider: newKeyProvider.value, api_key: newKey.value })
    showAddKeyDialog.value = false
    newKey.value = ''
    fetchApiKeys()
  } catch (e) {
    apiKeyError.value = e.response?.data?.detail || 'Failed to add API key'
  }
}

const deleteKey = async (id) => {
  try {
    await api.delete(`/api-keys/${id}`)
    fetchApiKeys()
  } catch (e) {
    apiKeyError.value = e.response?.data?.detail || 'Failed to delete API key'
  }
}

const fetchPublishingConfigs = async () => {
  try {
    const { data } = await api.get('/publishing')
    publishingConfigs.value = data
  } catch (e) {
    publishError.value = e.response?.data?.detail || 'Failed to fetch configs'
  }
}

const addPublishingConfig = async () => {
  try {
    await api.post('/publishing', { name: newConfigName.value, platform: newConfigPlatform.value })
    showAddConfigDialog.value = false
    newConfigName.value = ''
    fetchPublishingConfigs()
  } catch (e) {
    publishError.value = e.response?.data?.detail || 'Failed to add config'
  }
}

const deleteConfig = async (id) => {
  try {
    await api.delete(`/publishing/${id}`)
    fetchPublishingConfigs()
  } catch (e) {
    publishError.value = e.response?.data?.detail || 'Failed to delete config'
  }
}

fetchApiKeys()
fetchPublishingConfigs()
</script>