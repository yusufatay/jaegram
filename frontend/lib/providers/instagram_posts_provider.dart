import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';
import '../models/instagram_post.dart';
import '../providers/user_provider.dart';

final instagramPostsProvider = FutureProvider<List<InstagramPost>>((ref) async {
  try {
    final apiClient = ref.read(apiClientProvider);
    final user = ref.watch(userProvider).valueOrNull;
    
    if (user == null || user.token == null) {
      return [];
    }
    
    final response = await apiClient.get(
      '/user/instagram-posts?limit=6', 
      token: user.token
    );
    final List<dynamic> data = response['posts'] ?? [];
    
    // Convert the backend response format to InstagramPost format
    return data.map((json) {
      return InstagramPost(
        id: json['id'] ?? '',
        url: json['instagram_url'] ?? '',
        imageUrl: json['media_url'] ?? json['thumbnail_url'] ?? '',
        videoUrl: json['media_type'] == 'VIDEO' ? json['media_url'] : null,
        caption: json['caption'] ?? '',
        likeCount: json['like_count'] ?? 0,
        commentCount: json['comment_count'] ?? 0,
        createdAt: json['timestamp'] != null ? DateTime.tryParse(json['timestamp']) : null,
      );
    }).toList();
  } catch (e) {
    return [];
  }
});