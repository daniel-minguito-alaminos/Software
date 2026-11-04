<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="site">
    <header>
      <RouterLink class="brand" to="/">
        <svg viewBox="0 0 32 32" width="30" aria-hidden="true">
          <path fill="currentColor" d="M2 29V15l8-6v20zm10 0V8l8-6v27zm10 0V5l8 6v18z"/>
        </svg>
        BizPartnerCheck
      </RouterLink>
      <nav aria-label="Account">
        <RouterLink class="button outline" to="/login">Log in</RouterLink>
        <RouterLink class="button" to="/register">Create an account</RouterLink>
      </nav>
    </header>
    <RouterView :key="$route.path" />
  </div>
</template>

<style>
* { box-sizing: border-box; }
body { margin: 0; background: #f3f8fd; color: #102e5b; font: 16px/1.5 system-ui, sans-serif; }
#app { display: block; max-width: none; padding: 0; margin: 0; }
.site { max-width: 1440px; margin: auto; }
.site header { min-height: 76px; display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; padding: 16px clamp(20px, 5vw, 72px); border-bottom: 1px solid #c6d9ee; }
.site nav, .actions, .brand { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.site a { color: #0847ae; text-decoration: none; }
.site .brand { color: #102e5b; font-weight: 800; font-size: 1.15rem; }
.site .button { display: inline-block; border: 1px solid #0847ae; border-radius: 7px; padding: 10px 17px; background: #0847ae; color: white; font: inherit; font-weight: 650; cursor: pointer; }
.site .button:hover { background: #073680; color: white; }
.site .outline { background: transparent; color: #0847ae; }
.site :focus-visible { outline: 3px solid #376dc2; outline-offset: 4px; }
.site h1 { color: #102e5b; line-height: 1.04; letter-spacing: -.045em; margin: 0 0 18px; }
.site p { margin: 0 0 24px; }
</style>
