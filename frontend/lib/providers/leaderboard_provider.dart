import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/social_service.dart';
import 'user_provider.dart';

final currentUserRankProvider = FutureProvider<Map<String, dynamic>?>((ref) async {
  final user = ref.watch(userProvider).value;
  if (user?.token == null) return null;
  final socialService = ref.watch(socialServiceProvider);
  return await socialService.getUserRank(user!.token!);
});
