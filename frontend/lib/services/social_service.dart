import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/badge.dart';
import '../models/leaderboard.dart';
import '../models/referral.dart';
import 'api_client.dart';

class SocialService {
  final ApiClient _apiClient;

  SocialService({ApiClient? apiClient}) : _apiClient = apiClient ?? ApiClient();

  // Referral System
  Future<String> generateReferralCode(String token) async {
    final response = await _apiClient.post('/social/referral/generate', {}, token: token);
    return response['referral_code'];
  }

  Future<bool> useReferralCode(String token, String referralCode) async {
    try {
      await _apiClient.post('/social/referral/use', {'referral_code': referralCode}, token: token);
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<List<Referral>> getReferrals(String token) async {
    final response = await _apiClient.getList('/social/referrals', token: token);
    return response.map((json) => Referral.fromJson(json)).toList();
  }

  // Badge System
  Future<List<Badge>> getAvailableBadges(String token) async {
    final response = await _apiClient.getList('/social/badges', token: token);
    return response.map((json) => Badge.fromJson(json)).toList();
  }

  Future<List<UserBadge>> getUserBadges(String token) async {
    final response = await _apiClient.getList('/social/user-badges', token: token);
    return response.map((json) => UserBadge.fromJson(json)).toList();
  }

  // Leaderboard System
  Future<List<Leaderboard>> getLeaderboard(String token, {String period = 'all'}) async {
    final response = await _apiClient.getList('/social/leaderboard?period=$period', token: token);
    return response.map((json) => Leaderboard.fromJson(json)).toList();
  }

  Future<Map<String, dynamic>> getUserRank(String token) async {
    return await _apiClient.get('/social/my-rank', token: token);
  }

  // Social Features
  Future<Map<String, dynamic>> getSocialStats(String token) async {
    return await _apiClient.get('/social/stats', token: token);
  }

  Future<bool> followUser(String token, int userId) async {
    try {
      await _apiClient.post('/social/follow', {'user_id': userId}, token: token);
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> unfollowUser(String token, int userId) async {
    try {
      await _apiClient.post('/social/unfollow', {'user_id': userId}, token: token);
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<List<Map<String, dynamic>>> getFollowers(String token) async {
    return await _apiClient.getList('/social/followers', token: token);
  }

  Future<List<Map<String, dynamic>>> getFollowing(String token) async {
    return await _apiClient.getList('/social/following', token: token);
  }
}

final socialServiceProvider = Provider<SocialService>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return SocialService(apiClient: apiClient);
});
