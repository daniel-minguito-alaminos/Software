<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <main class="hero">
    <div class="copy">
      <h1>Check your<br />business partners</h1>
      <p>Company checks for Austria’s construction industry.</p>
      <div class="actions">
        <RouterLink class="button" to="/register">Create an account</RouterLink>
        <RouterLink class="button outline" to="/login">Log in</RouterLink>
      </div>
    </div>
    <div class="art" aria-hidden="true">
      <svg viewBox="0 0 680 530" fill="none">
        <defs>
          <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
            <path d="M24 0H0V24" stroke="#b7e2ff" stroke-opacity=".35"/>
          </pattern>
          <linearGradient id="paper" x2="0" y2="1" gradientUnits="objectBoundingBox">
            <stop stop-color="#f6fcff"/><stop offset="1" stop-color="#8fc9f8"/>
          </linearGradient>
        </defs>
        <g transform="translate(127 113) skewX(-20) rotate(-9)">
          <rect x="10" y="12" width="520" height="315" rx="9" fill="#0b3878" opacity=".32"/>
          <rect width="520" height="315" rx="9" fill="#1556ad"/>
          <rect x="14" y="14" width="492" height="287" rx="4" fill="url(#grid)" stroke="#77b7eb"/>
          <g stroke="#e3f4ff" stroke-width="2" stroke-linejoin="round">
            <path d="M115 251V114L280 54l130 63v133l-128 31zM115 114l167 61 128-58M282 175v106M115 154l167 61 128-58M115 199l167 61 128-58M172 94v176m60-196v205m98-201v191m40-169v160"/>
            <path d="M88 112v139m-8-139h16m-16 139h16M102 286h309m-309-7v14m309-14v14" opacity=".6"/>
          </g>
        </g>
        <g transform="translate(385 74) rotate(-18)">
          <rect width="290" height="54" rx="26" fill="url(#paper)"/>
          <ellipse cx="24" cy="27" rx="20" ry="25" fill="#6aa9e0" stroke="#d8eeff" stroke-width="4"/>
          <path d="M75 4v46m50-46v46m50-46v46m50-46v46" stroke="#76b7ef" opacity=".5"/>
          <rect x="94" y="57" width="250" height="47" rx="23" fill="url(#paper)"/>
          <ellipse cx="114" cy="80" rx="17" ry="22" fill="#6aa9e0" stroke="#d8eeff" stroke-width="4"/>
        </g>
        <g transform="translate(435 347)">
          <ellipse cx="96" cy="122" rx="118" ry="21" fill="#143f7b" opacity=".24"/>
          <path d="M12 96c0-50 32-85 82-85 52 0 83 37 83 85z" fill="url(#paper)" stroke="#f0f9ff" stroke-width="3"/>
          <path d="M70 94V28c0-12 10-22 24-22s24 10 24 22v66" fill="#e6f4ff" stroke="#acd6f7" stroke-width="3"/>
          <path d="M5 92h179c11 0 18 6 18 13s-7 13-18 13H5c-10 0-17-6-17-13S-5 92 5 92z" fill="#edf8ff" stroke="#93c5ed" stroke-width="3"/>
        </g>
      </svg>
    </div>
  </main>
</template>

<style scoped>
.hero { min-height: min(650px, calc(100svh - 76px)); display: grid; grid-template-columns: .95fr 1.05fr; overflow: hidden; background: #eaf4fd; }
.copy { align-self: center; padding: 55px 0 55px clamp(20px, 5vw, 72px); z-index: 1; }
h1 { font-size: clamp(2.5rem, 5.4vw, 5rem); }
p { max-width: 28ch; font-size: clamp(1rem, 2vw, 1.25rem); }
.art { display: grid; align-items: center; background: linear-gradient(155deg, #b6dbfa, #629ad5); clip-path: polygon(24% 0, 100% 0, 100% 100%, 0 100%); }
svg { width: 100%; height: auto; }
@media (max-width: 740px) {
  .hero { grid-template-columns: 1fr; }
  .copy { padding: 52px 20px 36px; }
  .art { clip-path: none; }
  svg { max-height: 330px; }
}
</style>
