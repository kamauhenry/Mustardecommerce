<template>
  <AdminLayout>
    <div class="orders">
      <h2>Orders</h2>
      <table>
        <thead>
          <tr>
            <th>Order ID</th>
            <th>User</th>
            <th>Product</th>
            <th>Quantity</th>
            <th>Total Price</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id">
            <td>{{ order.id }}</td>
            <td>{{ order.user }}</td>
            <td>{{ order.product.name }}</td>
            <td>{{ order.quantity }}</td>
            <td>KES {{ order.total_price }}</td>
            <td>
              <button @click="deleteOrder(order.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </AdminLayout>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import AdminLayout from '@/components/admin/AdminLayout.vue';

export default {
  components: { AdminLayout },
  setup() {
    const orders = ref([]);

    const fetchOrders = async () => {
      const response = await axios.get('orders/');
      orders.value = response.data;
    };

    const deleteOrder = async (id) => {
      if (confirm('Are you sure you want to delete this order?')) {
        await axios.delete(`orders/${id}/`);
        fetchOrders();
      }
    };

    onMounted(() => {
      fetchOrders();
    });

    return { orders, deleteOrder };
  },
};
</script>

<style scoped>
.orders {
  padding: 1rem;
}

h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f8f9fa;
  font-weight: 600;
}

td button {
  padding: 0.25rem 0.5rem;
  background-color: #dc3545;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

td button:hover {
  opacity: 0.9;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  th, td {
    padding: 0.5rem;
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  th, td {
    font-size: 0.8rem;
  }
}
</style>
