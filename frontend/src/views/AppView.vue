<script setup>
import { currentUser } from '../auth/session'
</script>

<!-- Protected application page (BIZ-32). Only reachable with a valid session. -->
<template>
  <main class="app-page">
    <section aria-labelledby="app-title">
      <h1 id="app-title">Your workspace</h1>
      <p>
        Signed in as <strong>{{ currentUser?.email }}</strong>.
      </p>
      <p class="placeholder">Business partner checks will appear here.</p>
    </section>
  </main>
</template>

<style scoped>
.app-page { min-height: calc(100svh - 76px); padding: 44px clamp(16px, 5vw, 72px); background: #eaf4fd; }
section { max-width: 900px; border: 1px solid #c6d9ee; border-radius: 16px; padding: clamp(22px, 5vw, 40px); background: white; box-shadow: 0 18px 52px #17498214; }
h1 { font-size: clamp(2rem, 5vw, 2.75rem); }
strong { overflow-wrap: anywhere; }
.placeholder { margin: 0; padding: 16px; border: 1px dashed #93abc9; border-radius: 7px; color: #3c5a85; }
</style>
