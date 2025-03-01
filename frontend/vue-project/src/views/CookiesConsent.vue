<template>
  <div v-if="showCookieBanner" class="cookie-banner">
    <p>
      This website uses cookies to ensure you get the best experience. Read our
      <a href="/privacy-policy" class="link">Privacy Policy</a>.
    </p>
    <button @click="acceptCookies" class="btn">Got it!</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const showCookieBanner = ref(false);

onMounted(() => {
  if (!localStorage.getItem("cookieAccepted")) {
    showCookieBanner.value = true;
  }
});

const acceptCookies = () => {
  localStorage.setItem("cookieAccepted", "true");
  showCookieBanner.value = false;
};
</script>

<style scoped>
.cookie-banner {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background: #333;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.link {
  color: #ffcc00;
  text-decoration: underline;
}

.btn {
  background: #ffcc00;
  border: none;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-weight: bold;
}
</style>
