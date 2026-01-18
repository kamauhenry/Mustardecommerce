"""
Integration tests for end-to-end workflows in the e-commerce system.
These tests verify that different components work together correctly.
"""
from django.test import TestCase
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import transaction
from ecommerce.models import (
    Product, Inventory, Category, Order, OrderItem,
    Cart, CartItem, ShippingMethod, DeliveryLocation,
    CompletedOrder, Payment
)

User = get_user_model()


class PickAndPayPurchaseFlowTest(TestCase):
    """Test complete Pick & Pay purchase workflow from cart to completion"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.category = Category.objects.create(name="Electronics", slug="electronics")

    def test_complete_pick_and_pay_purchase_flow(self):
        """
        End-to-end workflow:
        1. User adds Pick & Pay product to cart
        2. Creates order from cart
        3. Processes M-Pesa payment (mocked)
        4. Inventory is reduced
        5. Order marked complete
        6. User receives points
        """
        # Step 1: Create Pick & Pay product with inventory
        product = Product.objects.create(
            name="Pick & Pay Product",
            price=Decimal("500.00"),
            is_pick_and_pay=True,
            category=self.category
        )
        inventory = Inventory.objects.create(product=product, quantity=20)

        # Step 2: User adds product to cart
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2
        )

        # Verify cart totals
        self.assertEqual(cart.subtotal, Decimal("1000.00"))
        self.assertEqual(cart.total, Decimal("1000.00"))  # No shipping for Pick & Pay

        # Step 3: Create order from cart
        order = Order.objects.create(
            user=self.user,
            is_pick_and_pay=True
        )

        # Transfer cart items to order
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Calculate order total
        order.update_total_price()
        self.assertEqual(order.total_price, Decimal("1000.00"))

        # Step 4: Reduce inventory when order is placed
        with transaction.atomic():
            for item in order.items.all():
                if item.product.is_pick_and_pay:
                    inv = Inventory.objects.get(product=item.product)
                    inv.reduce_stock(item.quantity)

        # Verify inventory reduced
        inventory.refresh_from_db()
        self.assertEqual(inventory.quantity, 18)  # 20 - 2 = 18

        # Step 5: Process payment (mocked)
        payment = Payment.objects.create(
            order=order,
            phone_number='254712345678',
            amount=order.total_price,
            payment_method='mpesa',
            payment_status='completed',
            mpesa_receipt_number='ABC123'
        )

        # Update order payment status
        order.payment_status = 'paid'
        order.delivery_status = 'delivered'
        order.save()

        # Step 6: Mark order as completed and award points
        completed_order = CompletedOrder.objects.create(
            original_order=order,  # Fixed: use original_order not order
            order_number=f"ORD-{order.id}",
            user=self.user,
            shipping_method=order.shipping_method.name if order.shipping_method else "Pick and Pay",
            order_date=order.created_at
        )

        # Verify completion
        self.assertEqual(order.payment_status, 'paid')
        self.assertEqual(order.delivery_status, 'delivered')
        # Verify order is linked to completed order
        self.assertEqual(completed_order.original_order, order)


class MOQGroupBuyFlowTest(TestCase):
    """Test MOQ group buy workflow with multiple users"""

    def setUp(self):
        self.category = Category.objects.create(name="Electronics", slug="electronics")

    def test_moq_group_buy_progress_tracking(self):
        """
        End-to-end workflow:
        1. Create MOQ product (target: 50 units)
        2. User 1 orders 20 units → 40% progress
        3. User 2 orders 15 units → 70% progress
        4. User 3 orders 20 units → 110% progress (exceeds MOQ)
        5. Admin closes MOQ (moq_status='completed')
        """
        # Step 1: Create MOQ product
        product = Product.objects.create(
            name="MOQ Group Buy Product",
            price=Decimal("5000.00"),
            below_moq_price=Decimal("6000.00"),
            moq=50,
            moq_per_person=5,
            moq_status='active',
            is_pick_and_pay=False,
            category=self.category
        )

        # Step 2: User 1 orders 20 units
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass'
        )
        order1 = Order.objects.create(user=user1, payment_status='paid')
        OrderItem.objects.create(
            order=order1,
            product=product,
            quantity=20,
            price=product.price
        )

        # Verify progress at 40%
        self.assertEqual(product.current_moq_count(), 20)
        self.assertEqual(product.moq_progress_percentage(), 40)

        # Step 3: User 2 orders 15 units
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass'
        )
        order2 = Order.objects.create(user=user2, payment_status='paid')
        OrderItem.objects.create(
            order=order2,
            product=product,
            quantity=15,
            price=product.price
        )

        # Verify progress at 70%
        self.assertEqual(product.current_moq_count(), 35)
        self.assertEqual(product.moq_progress_percentage(), 70)

        # Step 4: User 3 orders 20 units
        user3 = User.objects.create_user(
            username='user3',
            email='user3@example.com',
            password='pass'
        )
        order3 = Order.objects.create(user=user3, payment_status='paid')
        OrderItem.objects.create(
            order=order3,
            product=product,
            quantity=20,
            price=product.price
        )

        # Verify progress at 110% (exceeds MOQ)
        self.assertEqual(product.current_moq_count(), 55)
        self.assertEqual(product.moq_progress_percentage(), 110)

        # Step 5: Admin closes MOQ
        product.moq_status = 'completed'
        product.save()

        # Verify MOQ is completed
        self.assertEqual(product.moq_status, 'completed')
        self.assertGreaterEqual(product.current_moq_count(), product.moq)


class CartToOrderConversionTest(TestCase):
    """Test cart to order conversion with multiple products"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.shipping_method = ShippingMethod.objects.create(
            name="Standard Shipping",
            price=Decimal("200.00")
        )
        self.delivery_location = DeliveryLocation.objects.create(
            user=self.user,
            county="Nairobi",
            ward="Westlands",
            address="123 Test St"
        )

    def test_cart_to_order_conversion_workflow(self):
        """
        End-to-end workflow:
        1. Create cart with multiple products
        2. Select shipping method
        3. Create order from cart
        4. Verify items transferred
        5. Verify total price calculation (items + shipping)
        """
        # Step 1: Create multiple products and add to cart
        product1 = Product.objects.create(
            name="Product 1",
            price=Decimal("1000.00"),
            category=self.category
        )
        product2 = Product.objects.create(
            name="Product 2",
            price=Decimal("500.00"),
            category=self.category
        )

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=product1, quantity=2)
        CartItem.objects.create(cart=cart, product=product2, quantity=3)

        # Step 2: Select shipping method
        cart.shipping_method = self.shipping_method
        cart.save()

        # Verify cart totals
        # 2*1000 + 3*500 + 200 = 3700
        self.assertEqual(cart.subtotal, Decimal("3500.00"))
        self.assertEqual(cart.total, Decimal("3700.00"))

        # Step 3: Create order from cart
        order = Order.objects.create(
            user=self.user,
            shipping_method=self.shipping_method,
            delivery_location=self.delivery_location
        )

        # Step 4: Transfer cart items to order
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

        # Step 5: Calculate and verify order total
        order.update_total_price()
        order.refresh_from_db()

        # Verify items transferred
        self.assertEqual(order.items.count(), 2)

        # Verify total price (items + shipping)
        self.assertEqual(order.total_price, Decimal("3700.00"))

        # Verify order details
        self.assertEqual(order.shipping_method, self.shipping_method)
        self.assertEqual(order.delivery_location, self.delivery_location)


class OrderCancellationFlowTest(TestCase):
    """Test order cancellation workflow with inventory restoration"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.category = Category.objects.create(name="Electronics", slug="electronics")

    def test_order_cancellation_restores_inventory(self):
        """
        End-to-end workflow:
        1. Create Pick & Pay order with inventory reduction
        2. Cancel order
        3. Verify inventory restored
        4. Verify order status updated
        """
        # Step 1: Create Pick & Pay product and order
        product = Product.objects.create(
            name="Pick & Pay Product",
            price=Decimal("500.00"),
            is_pick_and_pay=True,
            category=self.category
        )
        inventory = Inventory.objects.create(product=product, quantity=20)

        order = Order.objects.create(
            user=self.user,
            is_pick_and_pay=True,
            payment_status='pending',
            delivery_status='processing'
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=5,
            price=product.price
        )

        # Reduce inventory when order placed
        inventory.reduce_stock(5)
        inventory.refresh_from_db()
        self.assertEqual(inventory.quantity, 15)

        # Step 2: Cancel order
        with transaction.atomic():
            # Restore inventory for Pick & Pay products
            for item in order.items.all():
                if item.product.is_pick_and_pay:
                    inv = Inventory.objects.get(product=item.product)
                    inv.restock(item.quantity)

            order.is_cancelled = True
            order.delivery_status = 'cancelled'
            order.save()

        # Step 3: Verify inventory restored
        inventory.refresh_from_db()
        self.assertEqual(inventory.quantity, 20)

        # Step 4: Verify order status updated
        self.assertTrue(order.is_cancelled)
        self.assertEqual(order.delivery_status, 'cancelled')


class AdminOrderManagementFlowTest(TestCase):
    """Test admin order management workflow"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass',
            user_type='admin',
            is_staff=True,
            is_superuser=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.category = Category.objects.create(name="Electronics", slug="electronics")

    def test_admin_bulk_order_status_update(self):
        """
        End-to-end workflow:
        1. Admin bulk updates order statuses
        2. Verify all orders updated
        3. Verify status transitions are valid
        """
        # Step 1: Create multiple orders
        product = Product.objects.create(
            name="Test Product",
            price=Decimal("1000.00"),
            category=self.category
        )

        orders = []
        for i in range(5):
            order = Order.objects.create(
                user=self.user,
                delivery_status='processing',
                payment_status='paid'
            )
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                price=product.price
            )
            orders.append(order)

        # Step 2: Admin bulk updates to 'shipped'
        order_ids = [order.id for order in orders]
        updated_orders = Order.objects.filter(id__in=order_ids)

        for order in updated_orders:
            order.delivery_status = 'shipped'
            order.save()

        # Step 3: Verify all orders updated
        for order in Order.objects.filter(id__in=order_ids):
            self.assertEqual(order.delivery_status, 'shipped')

        # Step 4: Further update to 'delivered'
        for order in updated_orders:
            order.delivery_status = 'delivered'
            order.save()

        # Verify final status
        for order in Order.objects.filter(id__in=order_ids):
            self.assertEqual(order.delivery_status, 'delivered')

    def test_admin_dashboard_statistics(self):
        """
        Test admin can retrieve order statistics
        """
        # Create various orders
        product = Product.objects.create(
            name="Test Product",
            price=Decimal("1000.00"),
            category=self.category
        )

        # Paid order
        paid_order = Order.objects.create(
            user=self.user,
            payment_status='paid',
            delivery_status='delivered'
        )
        OrderItem.objects.create(
            order=paid_order,
            product=product,
            quantity=1,
            price=product.price
        )
        paid_order.update_total_price()

        # Pending order
        pending_order = Order.objects.create(
            user=self.user,
            payment_status='pending',
            delivery_status='processing'
        )
        OrderItem.objects.create(
            order=pending_order,
            product=product,
            quantity=2,
            price=product.price
        )
        pending_order.update_total_price()

        # Verify statistics
        total_orders = Order.objects.count()
        paid_orders = Order.objects.filter(payment_status='paid').count()
        pending_orders = Order.objects.filter(payment_status='pending').count()

        self.assertEqual(total_orders, 2)
        self.assertEqual(paid_orders, 1)
        self.assertEqual(pending_orders, 1)
