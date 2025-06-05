import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'api_client.dart';
import '../providers/user_provider.dart';

class StatisticsService {
  final ApiClient _apiClient;

  StatisticsService(this._apiClient);

  /// Get user statistics from API - NO FALLBACK DATA, REAL DATA ONLY
  Future<Map<String, dynamic>> getUserStatistics(String token) async {
    try {
      final response = await _apiClient.get('/statistics', token: token);
      
      // Validate and ensure all required fields exist with proper types
      final validatedResponse = <String, dynamic>{
        'total_earnings': (response['total_earnings'] as num?)?.toInt() ?? 0,
        'completed_tasks': (response['completed_tasks'] as num?)?.toInt() ?? 0,
        'active_tasks': (response['active_tasks'] as num?)?.toInt() ?? 0,
        'daily_streak': (response['daily_streak'] as num?)?.toInt() ?? 0,
        'level': response['level'] as String? ?? 'Bronz',
      };
      
      // Handle weekly earnings array
      if (response['weekly_earnings'] is List) {
        validatedResponse['weekly_earnings'] = (response['weekly_earnings'] as List)
            .map((e) => (e as num?)?.toInt() ?? 0)
            .toList();
      } else {
        validatedResponse['weekly_earnings'] = List.filled(7, 0);
      }
      
      // Handle task distribution with proper type conversion
      if (response['task_distribution'] is Map) {
        final taskDist = <String, double>{};
        final rawTaskDist = response['task_distribution'] as Map<String, dynamic>;
        
        for (final entry in rawTaskDist.entries) {
          final key = entry.key;
          final value = entry.value;
          if (value is num) {
            taskDist[key] = value.toDouble();
          } else {
            taskDist[key] = 0.0;
          }
        }
        
        validatedResponse['task_distribution'] = taskDist;
      } else {
        // No fallback data - show empty state when no real data
        validatedResponse['task_distribution'] = <String, double>{
          'like': 0.0,
          'follow': 0.0,
          'comment': 0.0,
          'other': 0.0
        };
      }
      
      return validatedResponse;
      
    } catch (e) {
      // Error getting statistics - UI will handle error states
      rethrow;
    }
  }

  /// Get user notifications from API
  Future<Map<String, dynamic>> getNotifications(String token, {int limit = 20, int offset = 0}) async {
    try {
      // Backend /notifications endpoint returns an array directly
      final response = await _apiClient.getList('/notifications', token: token);
      return {
        'notifications': response,
        'unread_count': response.where((n) => !(n['is_read'] ?? false)).length
      };
    } catch (e) {
      // Error getting notifications - return empty state
      return {
        'notifications': [],
        'unread_count': 0
      };
    }
  }

  /// Mark notification as read
  Future<bool> markNotificationRead(String token, int notificationId) async {
    try {
      final response = await _apiClient.post('/notifications/$notificationId/mark-read', {}, token: token);
      return response['success'] == true;
    } catch (e) {
      // Error marking notification as read
      return false;
    }
  }
}

// Provider
final statisticsServiceProvider = Provider<StatisticsService>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return StatisticsService(apiClient);
});

// Statistics data provider
final statisticsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final statisticsService = ref.watch(statisticsServiceProvider);
  final user = ref.watch(userProvider);
  
  return user.when(
    data: (userData) async {
      if (userData?.token != null) {
        return await statisticsService.getUserStatistics(userData!.token!);
      }
      throw Exception('No authentication token');
    },
    loading: () => throw Exception('Loading authentication'),
    error: (error, stack) => throw error,
  );
});

// Notifications provider
final statisticsNotificationsProvider = FutureProvider<Map<String, dynamic>>((ref) async {
  final statisticsService = ref.watch(statisticsServiceProvider);
  final user = ref.watch(userProvider);
  
  return user.when(
    data: (userData) async {
      if (userData?.token != null) {
        return await statisticsService.getNotifications(userData!.token!);
      }
      throw Exception('No authentication token');
    },
    loading: () => throw Exception('Loading authentication'),
    error: (error, stack) => throw error,
  );
});
