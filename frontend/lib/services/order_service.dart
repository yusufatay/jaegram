import 'api_client.dart';
import '../models/order.dart';

/// Siparişlerle ilgili API işlemleri
class OrderService {
  final ApiClient _apiClient;
  OrderService(this._apiClient);

  /// Sipariş oluştur
  Future<Order> createOrder({
    required int productId,
    required int quantity,
    required String token,
  }) async {
    final response = await _apiClient.post(
      '/orders',
      {
        'product_id': productId,
        'quantity': quantity,
      },
      token: token,
    );
    return Order.fromJson(response['order'] as Map<String, dynamic>);
  }
}
