import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';
import '../models/daily_reward.dart';
import '../providers/user_provider.dart';

class DailyRewardService {
  final ApiClient _apiClient;

  DailyRewardService(this._apiClient);

  Future<DailyRewardStatus> getDailyRewardStatus(String token) async {
    final response = await _apiClient.get('/daily-reward-status', token: token);
    
    // Transform backend response to match our model
    final transformedResponse = {
      'can_claim': response['can_claim'],
      'current_streak': response['streak'] ?? 0,
      'next_reward': response['next_reward'],
      'last_claim': response['last_claim'],
    };
    
    return DailyRewardStatus.fromJson(transformedResponse);
  }

  Future<DailyRewardResponse> claimDailyReward(String token) async {
    final response = await _apiClient.post('/claim-daily-reward', {}, token: token);
    
    // Transform backend response to match our model
    final transformedResponse = {
      'success': response['success'] ?? true,
      'diamonds_awarded': response['coins_earned'] ?? 0,
      'streak_day': response['streak'] ?? response['consecutive_days'] ?? 1,
      'new_balance': response['total_balance'] ?? 0,
      'message': response['message'] ?? 'Günlük ödül alındı!',
    };
    
    return DailyRewardResponse.fromJson(transformedResponse);
  }
}

final dailyRewardServiceProvider = Provider<DailyRewardService>((ref) {
  final apiClient = ref.read(apiClientProvider);
  return DailyRewardService(apiClient);
});

class DailyRewardNotifier extends StateNotifier<AsyncValue<DailyRewardStatus?>> {
  final DailyRewardService _service;
  final Ref _ref;

  DailyRewardNotifier(this._service, this._ref) : super(const AsyncValue.data(null));

  Future<void> fetchStatus() async {
    final userAsync = _ref.read(userProvider);
    final user = userAsync.value;
    
    if (user?.token == null) return;

    state = const AsyncValue.loading();
    
    try {
      final status = await _service.getDailyRewardStatus(user!.token!);
      state = AsyncValue.data(status);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  Future<DailyRewardResponse?> claimReward() async {
    final userAsync = _ref.read(userProvider);
    final user = userAsync.value;
    
    if (user?.token == null) return null;

    try {
      final response = await _service.claimDailyReward(user!.token!);
      
      // Immediately update user balance with the new balance from response
      final updatedUser = user.copyWith(diamondBalance: response.newBalance);
      _ref.read(userProvider.notifier).setUser(updatedUser);
      
      // Also update the diamond provider if it exists
      // (Artık diamondProvider güncellenmiyor, userProvider güncellenince diamondProvider otomatik güncellenir)
      
      // Also refresh the profile to get latest data from backend
      await _ref.read(userProvider.notifier).refreshProfile();
      
      // Refresh status
      await fetchStatus();
      
      return response;
    } catch (error) {
      rethrow;
    }
  }
}

final dailyRewardProvider = StateNotifierProvider<DailyRewardNotifier, AsyncValue<DailyRewardStatus?>>((ref) {
  final service = ref.read(dailyRewardServiceProvider);
  return DailyRewardNotifier(service, ref);
});
