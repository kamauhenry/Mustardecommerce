<template>
  <div class="home-page-container">
    <TopRow></TopRow>
    <PagesRow></PagesRow>
    <CategoriesRow></CategoriesRow>
  </div>
</template>

<script>
  import TopRow from "./components/navigation/TopRow.vue";
  import PagesRow from "./components/navigation/PagesRow.vue";
  import CategoriesRow from "./components/navigation/CategoriesRow.vue";

  export default {
    components: {
      TopRow,
      PagesRow,
      CategoriesRow,
    },
  };
</script>
