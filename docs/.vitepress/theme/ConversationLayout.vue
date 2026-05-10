<script setup lang="ts">
import DefaultTheme from 'vitepress/theme'
import { useData } from 'vitepress'
import { computed } from 'vue'

const { frontmatter } = useData()

const layoutClass = computed(() => ({
  'conversation-article': Boolean(frontmatter.value.conversation),
}))
</script>

<template>
  <div :class="layoutClass">
    <DefaultTheme.Layout />
  </div>
</template>
