from django.db.models import Q, Sum, Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions, status
from django.core.cache import cache
from django.core.cache.backends.base import InvalidCacheBackendError
from ..models import User, Order, Product
from .serializers import ProductSerializer
from .utils import MAX_DASHBOARD_ITEMS
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_dashboard(request):
    logger.info(f"Admin dashboard accessed by user: {request.user.username} (ID: {request.user.id}, Type: {request.user.user_type})")

    if request.user.user_type != 'admin':
        logger.warning(f"Non-admin user {request.user.username} attempted to access the dashboard")
        return Response(
            {'error': 'Only admins can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )

    cache_key = 'admin_dashboard'
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Cache error: {e}. Falling back to direct query.")

    try:
        total_sales = Order.objects.count()
        total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
        total_customers = User.objects.filter(user_type='customer').count()
        top_products = Product.objects.select_related('category').annotate(
            moq_count=Count('orderitem', filter=Q(orderitem__order__delivery_status__in=['processing', 'shipped']))
        ).order_by('-moq_count')[:MAX_DASHBOARD_ITEMS]
        top_products_data = ProductSerializer(top_products, many=True, context={'request': request}).data

        today = datetime.today()
        revenue_trend = {'current': [], 'previous': []}
        for i in range(6):
            month = today - timedelta(days=30 * i)
            current_month_revenue = Order.objects.filter(
                created_at__month=month.month, created_at__year=month.year
            ).aggregate(Sum('total_price'))['total_price__sum'] or 0
            previous_month = month - timedelta(days=30)
            previous_month_revenue = Order.objects.filter(
                created_at__month=previous_month.month, created_at__year=previous_month.year
            ).aggregate(Sum('total_price'))['total_price__sum'] or 0
            revenue_trend['current'].insert(0, float(current_month_revenue))
            revenue_trend['previous'].insert(0, float(previous_month_revenue))

        sales_by_location = Order.objects.filter(delivery_location__isnull=False).select_related('delivery_location').values('delivery_location__county').annotate(sales=Count('id')).order_by('-sales')[:3]
        sales_by_location = [
            {'location': item['delivery_location__county'] or 'Unknown', 'sales': item['sales']}
            for item in sales_by_location
        ]
        total_sales_breakdown = [
            {'channel': 'Direct', 'sales': 38},
            {'channel': 'Affiliate', 'sales': 15},
            {'channel': 'Sponsored', 'sales': 14},
            {'channel': 'E-mail', 'sales': 48},
        ]

        active_orders = Order.objects.filter(delivery_status__in=['processing', 'shipped']).count()
        recent_orders = Order.objects.select_related('user', 'shipping_method').prefetch_related('items').order_by('-created_at')[:MAX_DASHBOARD_ITEMS].values(
            'id', 'total_price', 'created_at', 'payment_status', 'delivery_status', 'user__email'
        )

        response_data = {
            'total_sales': total_sales,
            'total_revenue': float(total_revenue),
            'total_customers': total_customers,
            'top_products': top_products_data,
            'revenue_trend': revenue_trend,
            'sales_by_location': sales_by_location,
            'total_sales_breakdown': total_sales_breakdown,
            'active_orders': active_orders,
            'recent_orders': list(recent_orders),
            'user_leaderboard': User.objects.filter(user_type='customer').annotate(
                total_purchases=Count('order')
            ).order_by('-total_purchases').values('id', 'username', 'email', 'total_purchases')[:MAX_DASHBOARD_ITEMS]
        }

        try:
            cache.set(cache_key, response_data, timeout=60 * 5)  # Cache for 5 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        logger.info(f"Dashboard data retrieved successfully for user: {request.user.username}")
        return Response(response_data)
    except Exception as e:
        logger.error(f"Error retrieving dashboard data for user {request.user.username}: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Internal server error while fetching dashboard data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
