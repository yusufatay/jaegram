import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/badge.dart';
import '../services/api_client.dart';
import '../providers/user_provider.dart';

final earnedBadgesProvider = FutureProvider<List<UserBadge>>((ref) async {
  try {
    final apiClient = ref.read(apiClientProvider);
    final user = ref.watch(userProvider).valueOrNull;
    
    if (user == null || user.token == null) {
      return [];
    }
    
    // Fetch the earned badges from the API
    final response = await apiClient.get(
      '/user/badges',
      token: user.token
    );
    
    if (response.containsKey('badges')) {
      final List<dynamic> data = response['badges'] ?? [];
      return data.map((json) => UserBadge.fromJson(json)).toList();
    }
    return [];
  } catch (e) {
    // Handle error
    return [];
  }
});
