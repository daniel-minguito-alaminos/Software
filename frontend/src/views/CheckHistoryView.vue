<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { request } from '../api/auth'

const checks = ref([])
const loading = ref(true)
const error = ref('')

function viesStatus(sources) {
  const vies = sources.find((source) => source.name === 'VIES')
  if (vies?.status === 'checked') {
    return vies.valid ? 'Valid VAT number' : 'Invalid VAT number'
  }
  return vies?.status === 'unavailable' ? 'Unavailable' : 'Not yet implemented'
}

onMounted(async () => {
  try {
    checks.value = await request('/partner-checks')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="history-page">
    <h1>Check history</h1>
    <p><RouterLink to="/app">Back to workspace</RouterLink></p>

    <p v-if="loading" role="status">Loading checks…</p>
    <p v-else-if="error" role="alert">{{ error }}</p>
    <p v-else-if="!checks.length">No partner checks have been saved yet.</p>

    <ul v-else>
      <li v-for="check in checks" :key="check.id">
        <RouterLink :to="{ name: 'check-details', params: { id: check.id } }">
          {{ check.identifier }}
        </RouterLink>
        · {{ new Date(check.checked_at).toLocaleString() }}
        · {{ viesStatus(check.sources) }}
      </li>
    </ul>
  </main>
</template>

<style scoped>
.history-page {
  padding: 44px clamp(16px, 5vw, 72px);
}

li {
  margin-block: 12px;
}
</style>