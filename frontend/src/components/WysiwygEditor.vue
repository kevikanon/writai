<template>
  <div class="tiptap-editor">
    <div v-if="editor" class="toolbar mb-2">
      <v-btn-group density="compact" variant="outlined">
        <v-btn size="small" @click="editor.chain().focus().toggleBold().run()" :class="{ 'v-btn--active': editor.isActive('bold') }">
          <v-icon icon="mdi-format-bold" size="18" />
        </v-btn>
        <v-btn size="small" @click="editor.chain().focus().toggleItalic().run()" :class="{ 'v-btn--active': editor.isActive('italic') }">
          <v-icon icon="mdi-format-italic" size="18" />
        </v-btn>
        <v-btn size="small" @click="editor.chain().focus().toggleStrike().run()" :class="{ 'v-btn--active': editor.isActive('strike') }">
          <v-icon icon="mdi-format-strikethrough" size="18" />
        </v-btn>
        <v-btn size="small" @click="editor.chain().focus().toggleHeading({ level: 1 }).run()" :class="{ 'v-btn--active': editor.isActive('heading', { level: 1 }) }">
          H1
        </v-btn>
        <v-btn size="small" @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" :class="{ 'v-btn--active': editor.isActive('heading', { level: 2 }) }">
          H2
        </v-btn>
        <v-btn size="small" @click="editor.chain().focus().toggleHeading({ level: 3 }).run()" :class="{ 'v-btn--active': editor.isActive('heading', { level: 3 }) }">
          H3
        </v-btn>
        <v-btn size="small" @click="editor.chain().focus().toggleBulletList().run()" :class="{ 'v-btn--active': editor.isActive('bulletList') }">
          <v-icon icon="mdi-format-list-bulleted" size="18" />
        </v-btn>
        <v-btn size="small" @click="editor.chain().focus().toggleOrderedList().run()" :class="{ 'v-btn--active': editor.isActive('orderedList') }">
          <v-icon icon="mdi-format-list-numbered" size="18" />
        </v-btn>
        <v-btn size="small" @click="editor.chain().focus().toggleBlockquote().run()" :class="{ 'v-btn--active': editor.isActive('blockquote') }">
          <v-icon icon="mdi-format-quote-close" size="18" />
        </v-btn>
        <v-btn size="small" @click="editor.chain().focus().undo().run()" :disabled="!editor.can().undo()">
          <v-icon icon="mdi-undo" size="18" />
        </v-btn>
        <v-btn size="small" @click="editor.chain().focus().redo().run()" :disabled="!editor.can().redo()">
          <v-icon icon="mdi-redo" size="18" />
        </v-btn>
      </v-btn-group>
    </div>
    <v-card variant="outlined" class="editor-content">
      <v-card-text class="pa-0">
        <editor-content :editor="editor" class="editor-inner" />
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { watch, onMounted, onBeforeUnmount } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  editable: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:modelValue'])

const editor = useEditor({
  content: props.modelValue,
  editable: props.editable,
  extensions: [StarterKit],
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
})

watch(() => props.modelValue, (value) => {
  if (editor.value && editor.value.getHTML() !== value) {
    editor.value.commands.setContent(value, false)
  }
})

watch(() => props.editable, (value) => {
  if (editor.value) {
    editor.value.setEditable(value)
  }
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})
</script>

<style scoped>
.tiptap-editor {
  border: none;
}
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.editor-content {
  min-height: 300px;
}
.editor-inner {
  padding: 16px;
  min-height: 300px;
}
.editor-inner :deep(.ProseMirror) {
  outline: none;
  min-height: 280px;
}
.editor-inner :deep(.ProseMirror p) {
  margin: 0 0 0.5em 0;
}
.editor-inner :deep(.ProseMirror h1) {
  font-size: 2em;
  font-weight: bold;
  margin: 0 0 0.5em 0;
}
.editor-inner :deep(.ProseMirror h2) {
  font-size: 1.5em;
  font-weight: bold;
  margin: 1em 0 0.5em 0;
}
.editor-inner :deep(.ProseMirror h3) {
  font-size: 1.25em;
  font-weight: bold;
  margin: 1em 0 0.5em 0;
}
.editor-inner :deep(.ProseMirror ul),
.editor-inner :deep(.ProseMirror ol) {
  padding-left: 1.5em;
  margin: 0 0 0.5em 0;
}
.editor-inner :deep(.ProseMirror blockquote) {
  border-left: 3px solid #ccc;
  padding-left: 1em;
  margin-left: 0;
  font-style: italic;
}
.v-btn--active {
  background-color: rgba(0, 0, 0, 0.1);
}
</style>