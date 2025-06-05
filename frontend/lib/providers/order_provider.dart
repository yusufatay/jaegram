import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';
import './user_provider.dart';

/// Siparişlerin yönetimi için Riverpod provider.
final orderProvider = AsyncNotifierProvider<OrderNotifier, Map<String, dynamic>?>(OrderNotifier.new);

class OrderNotifier extends AsyncNotifier<Map<String, dynamic>?> {

  @override
  Future<Map<String, dynamic>?> build() async {
    return null;
  }  /// Sipariş oluştur
  Future<bool> createOrder({
    required String postUrl, 
    required String orderType, 
    required int targetCount, 
    String? commentText, // Add commentText for comment orders
  }) async {
    state = const AsyncValue.loading();
    final userState = ref.read(userProvider);

    final token = userState.valueOrNull?.token;
    if (token == null) {
      state = AsyncValue.error('Sipariş oluşturulamadı: Kullanıcı girişi yapılmamış veya token bulunamadı.', StackTrace.current);
      return false;
    }

    try {
      final apiClient = ref.read(apiClientProvider);
      final Map<String, dynamic> orderData = {
        'post_url': postUrl,
        'order_type': orderType,
        'target_count': targetCount,
      };
      if (orderType == 'comment' && commentText != null && commentText.isNotEmpty) {
        orderData['comment_text'] = commentText;
      }

      final result = await apiClient.post(
        '/create-order', 
        orderData,
        token: token, // Pass the token
      );
      state = AsyncValue.data(result);
      // Optionally, refresh user's coin balance or other relevant data
      ref.invalidate(userProvider); // To refresh user data like coin balance
      return true;
    } catch (e, stackTrace) {
      state = AsyncValue.error('Sipariş oluşturulamadı: ${e.toString()}', stackTrace);
      return false;
    }
  }

  void clearState() {
    state = const AsyncValue.data(null);
  }
}
