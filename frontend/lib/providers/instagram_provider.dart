import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/instagram_service.dart';

// Instagram Service Provider
final instagramServiceProvider = Provider<InstagramService>((ref) {
  return InstagramService();
});
