import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/user.dart';
import '../services/api_client.dart';
import '../providers/user_provider.dart';

final instagramProfileProvider = FutureProvider<InstagramProfileStats?>((ref) async {
  try {
    final apiClient = ref.read(apiClientProvider);
    final user = ref.watch(userProvider).valueOrNull;
    
    if (user == null || user.token == null) {
      return null;
    }
    
    // Fetch the Instagram profile stats from the API
    final response = await apiClient.get(
      '/user/instagram-profile',
      token: user.token
    );
    
    if (response.containsKey('profile')) {
      return InstagramProfileStats.fromJson(response['profile']);
    }
    return null;
  } catch (e) {
    // Handle error
    return null;
  }
});
