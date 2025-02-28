/* eslint-disable vue/multi-word-component-names */
import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import Sidebar from './components/adminDashboardComponents/Sidebar.vue';
import OrdersTable from './components/adminDashboardComponents/OrdersTable.vue';
import StatsPanel from './components/adminDashboardComponents/StatsPanel.vue';

const app = createApp(App);

app.component('Sidebar', Sidebar);
app.component('OrdersTable', OrdersTable);
app.component('StatsPanel', StatsPanel);

app.mount('#app');
