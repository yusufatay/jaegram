import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';
import 'user_provider.dart';

final instagramCredentialProvider = FutureProvider<Map<String, dynamic>?>((ref) async {
  try {
    final apiClient = ref.read(apiClientProvider);
    final userNotifier = ref.read(userProvider.notifier);
    final token = userNotifier.token;
    
    if (token == null) {
      return null;
    }
    
    final response = await apiClient.get('/user/instagram-credentials', token: token);
    return response;
  } catch (e) {
    return null;
  }
});
