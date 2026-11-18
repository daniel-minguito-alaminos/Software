<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { request } from '../api/auth'

const route = useRoute()
const check = ref(null)
const loading = ref(true)
const error = ref('')

function sourceStatus(source) {
  if (source.status === 'checked') {
    return source.valid ? 'Valid VAT number' : 'Invalid VAT number'
  }
  return source.status === 'unavailable' ? 'Unavailable' : 'Not yet implemented'
}

onMounted(async () => {
  try {
    check.value = await request(`/partner-checks/${route.params.id}`)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="details-page">
    <h1>Check details</h1>
    <p><RouterLink to="/app/checks">Back to check history</RouterLink></p>

    <p v-if="loading" role="status">Loading check…</p>
    <p v-else-if="error" role="alert">{{ error }}</p>

    <section v-else-if="check">
      <h2>{{ check.identifier }}</h2>
      <p>Checked on {{ new Date(check.checked_at).toLocaleString() }}</p>
      <dl>
        <div v-for="source in check.sources" :key="source.name">
          <dt>{{ source.name }}</dt>
          <dd>{{ sourceStatus(source) }}</dd>
        </div>
      </dl>
    </section>
  </main>
</template>

<style scoped>
.details-page {
  padding: 44px clamp(16px, 5vw, 72px);
}

dl > div {
  margin-block: 12px;
}

dt {
  font-weight: 650;
}

dd {
  margin-inline-start: 0;
}
</style>