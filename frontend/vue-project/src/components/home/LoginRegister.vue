<template>
  <div class="modal-content">
    <TabGroup>
      <TabList class="tab-list">
        <Tab as="template" v-slot="{ selected }">
          <button @click="currentTab = 'login'">
            Login
          </button>
        </Tab>
        <Tab as="template" v-slot="{ selected }">
          <button @click="currentTab = 'register'">
            Register
          </button>
        </Tab>
      </TabList>

      <TabPanels>
        <TabPanel>
          <Login />
        </TabPanel>
        <TabPanel>
          <Register />
        </TabPanel>
      </TabPanels>
    </TabGroup>
  </div>
</template>

<script setup>
import { ref } from "vue";
import Login from "@/components/auth/Login.vue";
import Register from "@/components/auth/Register.vue";
import { Tab, TabGroup, TabList, TabPanel, TabPanels } from '@headlessui/vue';

const currentTab = ref('login');
</script>

<style>
.modal-content {
  z-index: 1000;
}
.tab-list {
  display: flex;
  border-radius: 10px;
  background-color: #ccc;
  padding: 5px;
  gap: 5px;
}

.tab-button {
  width: 100%;
  padding: 10px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
}

.tab-button-unselected {
  background-color: rgba(255, 255, 255, 0.1);
  color: #337ab7;
}

.tab-button-unselected:hover {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.tab-button-selected {
  background-color: white;
  color: #337ab7;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}

.tab-panels {
  margin-top: 20px;
}

.tab-panel {
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
}
</style>
