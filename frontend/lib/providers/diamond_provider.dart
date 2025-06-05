import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';
import 'user_provider.dart';
import '../utils/api_constants.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

/// Diamond (puan) state yönetimi için Riverpod provider.
final diamondProvider = Provider<int?>((ref) {
  final user = ref.watch(userProvider).value;
  return user?.diamondBalance;
});

class DiamondNotifier extends AsyncNotifier<int?> {
  WebSocketChannel? _channel;

  @override
  Future<int?> build() async {
    // Watch user provider for diamond balance updates
    final user = ref.watch(userProvider).value;
    
    // If user has diamond balance, use it directly
    if (user?.diamondBalance != null) {
      // Connect WebSocket for real-time updates, but don't await it
      Future.microtask(() => _connectWebSocket());
      return user!.diamondBalance;
    }
    
    // Otherwise fetch from API
    final diamond = await fetchDiamond();
    // Connect WebSocket after diamond fetch, but don't await it to avoid blocking
    Future.microtask(() => _connectWebSocket());
    return diamond;
  }

  Future<int?> fetchDiamond() async {
    try {
      final apiClient = ref.read(apiClientProvider);
      final token = ref.read(_userTokenProvider);
      if (token == null) {
        throw Exception('Authentication token not found');
      }
      // API endpoint'ini /coins yerine /users/me/diamond-balance olarak düzeltin 
      // veya API'nizdeki doğru endpoint'i kullanın.
      // Bu örnekte /users/me olarak varsayıyorum, çünkü genellikle kullanıcı bilgileri buradan gelir.
      // Gerçek endpoint'i API dökümantasyonunuza göre ayarlamanız gerekebilir.
      final result = await apiClient.get('/users/me', token: token); 
      return result['diamondBalance'] as int?;
    } catch (e) {
      throw Exception('Elmas yüklenemedi: $e');
    }
  }

  /// Diamond bakiyesini yenile
  Future<void> refreshDiamond() async {
    state = const AsyncValue.loading();
    try {
      final diamond = await fetchDiamond();
      state = AsyncValue.data(diamond);
    } catch (e) {
      state = AsyncValue.error('Elmas yüklenemedi: $e', StackTrace.current);
    }
  }

  /// Manuel olarak diamond balance güncelle (örneğin daily reward sonrası)
  void updateDiamondBalance(int newBalance) {
    state = AsyncValue.data(newBalance);
  }

  Future<void> _connectWebSocket() async {
    try {
      final token = ref.read(_userTokenProvider);
      if (token == null) return;
      
      // Use API constants for consistent URL
      final wsUrl = '${ApiConstants.wsBaseUrl}/ws/notifications?token=$token';
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      
      _channel!.stream.listen(
        (event) async {
          // WebSocket olay adını kontrol edin, 'coin_update' yerine 'diamond_update' olmalı
          if (event.toString().contains('diamond_update')) {
            await refreshDiamond();
          }
        },
        onError: (error) {
          // WebSocket error - fail silently
          _channel = null;
        },
        onDone: () {
          // WebSocket connection closed
          _channel = null;
        },
      );
    } catch (e) {
      // Failed to connect WebSocket - fail silently
      _channel = null;
    }
  }
}

final _userTokenProvider = Provider<String?>((ref) {
  final user = ref.watch(userProvider).value;
  return user?.token;
});
