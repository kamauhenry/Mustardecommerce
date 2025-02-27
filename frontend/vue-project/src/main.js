/* eslint-disable vue/multi-word-component-names */
import './assets/main.css'
import './assets/admindashboard.css'

import { createApp } from 'vue'
import App from './App.vue'
import Sidebar from './components/Sidebar.vue';
import OrdersTable from './components/OrdersTable.vue';
import StatsPanel from './components/StatsPanel.vue';

const app = createApp(App);

app.component('Sidebar', Sidebar);
app.component('OrdersTable', OrdersTable);
app.component('StatsPanel', StatsPanel);

app.mount('#app');
