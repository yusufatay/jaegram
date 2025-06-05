import 'dart:async';
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_client.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'user_provider.dart';
import '../models/notification_model.dart';
import '../utils/api_constants.dart';

class NotificationState {
  final List<NotificationModel> notifications;
  final bool isLoading;
  final String? error;

  NotificationState({
    this.notifications = const [],
    this.isLoading = false,
    this.error,
  });

  NotificationState copyWith({
    List<NotificationModel>? notifications,
    bool? isLoading,
    String? error,
    bool clearError = false,
  }) {
    return NotificationState(
      notifications: notifications ?? this.notifications,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : error ?? this.error,
    );
  }
}

class NotificationNotifier extends StateNotifier<NotificationState> {
  final Ref _ref;
  WebSocketChannel? _channel;
  StreamSubscription? _webSocketSubscription;
  bool _isDisposed = false;

  NotificationNotifier(this._ref) : super(NotificationState(isLoading: false)) {
    // Don't call _init() immediately in constructor to avoid build loop
    // Let the UI trigger fetchNotifications when needed
  }

  Future<void> _init() async {
    if (_isDisposed) return;
    await fetchNotifications();
    if (_isDisposed) return;
    await _connectWebSocket();
  }

  @override
  void dispose() {
    _isDisposed = true;
    _webSocketSubscription?.cancel();
    _webSocketSubscription = null;
    _channel?.sink.close();
    _channel = null;
    super.dispose();
  }

  Future<void> fetchNotifications() async {
    if (_isDisposed) return;
    
    final apiClient = _ref.read(apiClientProvider);
    final token = _ref.read(_userTokenProvider);
    
    if (token == null) {
      state = NotificationState(isLoading: false, error: 'Token not found for notifications');
      return;
    }

    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final response = await apiClient.get('/notifications', token: token);
      if (_isDisposed) return;

      if (response['success'] == true) {
        final notificationsData = response['notifications'] as List;
        final notifications = notificationsData
            .map((item) => NotificationModel.fromJson(item))
            .toList();
        notifications.sort((a, b) => b.createdAt.compareTo(a.createdAt));

        if (_isDisposed) return;
        state = state.copyWith(notifications: notifications, isLoading: false);
        
        // Update badge count
        final unreadCount = notifications.where((n) => !n.isRead).length;
        _ref.read(badgeNotificationCountProvider.notifier).state = unreadCount;
      } else {
        if (_isDisposed) return;
        state = state.copyWith(
          error: response['message'] ?? 'Bildirimler yüklenemedi',
          isLoading: false,
        );
      }
    } catch (e) {
      if (_isDisposed) return;
      state = state.copyWith(error: e.toString(), isLoading: false);
    }
  }

  Future<void> _connectWebSocket() async {
    if (_isDisposed) return;
    
    final token = _ref.read(_userTokenProvider);
    if (token == null) return;

    // Clean up existing connection before creating a new one
    await _webSocketSubscription?.cancel();
    _webSocketSubscription = null;
    _channel?.sink.close();
    _channel = null;

    final wsUrl = '${ApiConstants.wsBaseUrl}/ws/notifications?token=$token';
    try {
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      if (_isDisposed) {
        _channel?.sink.close();
        _channel = null;
        return;
      }

      _webSocketSubscription = _channel!.stream.listen(
        (event) async {
          if (!_isDisposed) {
            final data = json.decode(event);
            if (data['type'] == 'notification') {
              await fetchNotifications();
            }
          }
        },
        onError: (error) {
          if (!_isDisposed) {
            _webSocketSubscription?.cancel();
            _webSocketSubscription = null;
            _channel?.sink.close();
            _channel = null;
          }
        },
        onDone: () {
          if (!_isDisposed) {
            _webSocketSubscription?.cancel();
            _webSocketSubscription = null;
            _channel?.sink.close();
            _channel = null;
          }
        },
        cancelOnError: true,
      );
    } catch (e) {
      if (!_isDisposed) {
        _channel = null;
      }
    }
  }

  Future<void> markAsRead(int notificationId) async {
    if (_isDisposed) return;
    
    final apiClient = _ref.read(apiClientProvider);
    final token = _ref.read(_userTokenProvider);
    if (token == null) return;

    try {
      await apiClient.post('/notifications/$notificationId/mark-read', {}, token: token);
      if (_isDisposed) return;

      final currentNotifications = List<NotificationModel>.from(state.notifications);
      final index = currentNotifications.indexWhere((n) => n.id == notificationId);
      if (index != -1) {
        currentNotifications[index] = currentNotifications[index].copyWith(isRead: true);
        final unreadCount = currentNotifications.where((n) => !n.isRead).length;
        _ref.read(badgeNotificationCountProvider.notifier).state = unreadCount;
        if (!_isDisposed) {
          state = state.copyWith(notifications: currentNotifications);
        }
      }
    } catch (e) {
      // Silently handle error
    }
  }

  Future<void> markAllAsRead() async {
    if (_isDisposed) return;
    
    final apiClient = _ref.read(apiClientProvider);
    final token = _ref.read(_userTokenProvider);
    if (token == null) return;

    try {
      await apiClient.post('/notifications/mark-all-read', {}, token: token);
      if (_isDisposed) return;

      final updatedNotifications = state.notifications
          .map((n) => n.copyWith(isRead: true))
          .toList();
      _ref.read(badgeNotificationCountProvider.notifier).state = 0;
      if (!_isDisposed) {
        state = state.copyWith(notifications: updatedNotifications);
      }
    } catch (e) {
      // Silently handle error
    }
  }
}

// Main notification provider
final notificationProvider = StateNotifierProvider<NotificationNotifier, NotificationState>((ref) {
  return NotificationNotifier(ref);
});

// Badge notification counter provider
final badgeNotificationCountProvider = StateProvider<int>((ref) => 0);

// Notifications summary provider
final notificationsProvider = Provider<Map<String, dynamic>>((ref) {
  final notificationState = ref.watch(notificationProvider);
  final unreadCount = notificationState.notifications
      .where((notification) => !notification.isRead)
      .length;
  
  return {
    'unread_count': unreadCount,
    'total_count': notificationState.notifications.length,
  };
});

// User token provider
final _userTokenProvider = Provider<String?>((ref) {
  final user = ref.watch(userProvider).value;
  return user?.token;
});

// Notification filter provider
final notificationFilterProvider = StateProvider<Set<NotificationType>>((ref) {
  return {
    NotificationType.badge,
    NotificationType.level,
    NotificationType.coins,
    NotificationType.instagram,
    NotificationType.system,
    NotificationType.taskCompleted,
    NotificationType.badgeEarned,
    NotificationType.coinReward,
    NotificationType.instagramSync,
    NotificationType.leaderboardUpdate,
    NotificationType.dailyReward,
  };
});