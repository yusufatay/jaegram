import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:timezone/timezone.dart' as tz;
import 'dart:convert';

class NotificationService {
  static final FlutterLocalNotificationsPlugin _flutterLocalNotificationsPlugin = 
      FlutterLocalNotificationsPlugin();
  
  static bool _isInitialized = false;

  // Notification types
  static const String taskCompleted = 'task_completed';
  static const String badgeEarned = 'badge_earned';
  static const String coinReward = 'coin_reward';
  static const String instagramSync = 'instagram_sync';
  static const String leaderboardUpdate = 'leaderboard_update';
  static const String dailyReward = 'daily_reward';

  static Future<void> initialize() async {
    if (_isInitialized) return;

    const androidInitializationSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosInitializationSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const initializationSettings = InitializationSettings(
      android: androidInitializationSettings,
      iOS: iosInitializationSettings,
    );

    await _flutterLocalNotificationsPlugin.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );

    _isInitialized = true;
  }

  static void _onNotificationTapped(NotificationResponse notificationResponse) {
    // Handle notification tap - could navigate to specific screens
    final payload = notificationResponse.payload;
    if (payload != null) {
      try {
        final data = jsonDecode(payload);
        // Handle different notification types
        switch (data['type']) {
          case taskCompleted:
          case badgeEarned:
            // Navigate to badges screen
            break;
          case coinReward:
            // Navigate to profile screen
            break;
          case instagramSync:
            // Navigate to Instagram integration screen
            break;
          case leaderboardUpdate:
            // Navigate to leaderboard screen
            break;
          case dailyReward:
            // Navigate to daily reward screen
            break;
        }
      } catch (e) {
        debugPrint('Error parsing notification payload: $e');
      }
    }
  }

  static Future<bool> _isNotificationEnabled(String type) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool('notification_${type}_enabled') ?? true;
  }

  static Future<void> showTaskCompletedNotification({
    required String taskTitle,
    required int coinsEarned,
    String? badgeName,
  }) async {
    if (!await _isNotificationEnabled(taskCompleted)) return;

    await _showNotification(
      id: 1,
      title: '🎉 Görev Tamamlandı!',
      body: '$taskTitle görevi tamamlandı. $coinsEarned jeton kazandınız!',
      payload: jsonEncode({
        'type': taskCompleted,
        'taskTitle': taskTitle,
        'coinsEarned': coinsEarned,
        'badgeName': badgeName,
      }),
    );
  }

  static Future<void> showBadgeEarnedNotification({
    required String badgeName,
    required String badgeDescription,
  }) async {
    if (!await _isNotificationEnabled(badgeEarned)) return;

    await _showNotification(
      id: 2,
      title: '🏆 Yeni Rozet Kazandınız!',
      body: '$badgeName rozetini kazandınız: $badgeDescription',
      payload: jsonEncode({
        'type': badgeEarned,
        'badgeName': badgeName,
        'badgeDescription': badgeDescription,
      }),
    );
  }

  static Future<void> showCoinRewardNotification({
    required int coinsEarned,
    required String reason,
  }) async {
    if (!await _isNotificationEnabled(coinReward)) return;

    await _showNotification(
      id: 3,
      title: '💰 Jeton Kazandınız!',
      body: '$reason nedeniyle $coinsEarned jeton kazandınız!',
      payload: jsonEncode({
        'type': coinReward,
        'coinsEarned': coinsEarned,
        'reason': reason,
      }),
    );
  }

  static Future<void> showInstagramSyncNotification({
    required bool success,
    required String message,
  }) async {
    if (!await _isNotificationEnabled(instagramSync)) return;

    await _showNotification(
      id: 4,
      title: success ? '📸 Instagram Senkronizasyonu Başarılı' : '❌ Instagram Senkronizasyon Hatası',
      body: message,
      payload: jsonEncode({
        'type': instagramSync,
        'success': success,
        'message': message,
      }),
    );
  }

  static Future<void> showLeaderboardUpdateNotification({
    required int newRank,
    required int previousRank,
  }) async {
    if (!await _isNotificationEnabled(leaderboardUpdate)) return;

    final isImprovement = newRank < previousRank;
    final title = isImprovement ? '🚀 Sıralama Yükseldi!' : '📊 Sıralama Güncellendi';
    final body = isImprovement 
        ? 'Tebrikler! Sıralamanız $previousRank\'den $newRank\'e yükseldi!'
        : 'Yeni sıralamanız: $newRank';

    await _showNotification(
      id: 5,
      title: title,
      body: body,
      payload: jsonEncode({
        'type': leaderboardUpdate,
        'newRank': newRank,
        'previousRank': previousRank,
      }),
    );
  }

  static Future<void> showDailyRewardNotification({
    required int coinsEarned,
    required int streakDays,
  }) async {
    if (!await _isNotificationEnabled(dailyReward)) return;

    await _showNotification(
      id: 6,
      title: '🎁 Günlük Ödül Zamanı!',
      body: 'Günlük ödülünüzü almayı unutmayın! $streakDays gün üst üste giriş',
      payload: jsonEncode({
        'type': dailyReward,
        'coinsEarned': coinsEarned,
        'streakDays': streakDays,
      }),
    );
  }

  static Future<void> _showNotification({
    required int id,
    required String title,
    required String body,
    String? payload,
  }) async {
    if (!_isInitialized) await initialize();

    const androidNotificationDetails = AndroidNotificationDetails(
      'instagram_puan_app_channel',
      'Instagram Puan App',
      channelDescription: 'Instagram Puan App notifications',
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
      enableVibration: true,
      playSound: true,
    );

    const iosNotificationDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    const notificationDetails = NotificationDetails(
      android: androidNotificationDetails,
      iOS: iosNotificationDetails,
    );

    await _flutterLocalNotificationsPlugin.show(
      id,
      title,
      body,
      notificationDetails,
      payload: payload,
    );
  }

  static Future<void> cancelNotification(int id) async {
    await _flutterLocalNotificationsPlugin.cancel(id);
  }

  static Future<void> cancelAllNotifications() async {
    await _flutterLocalNotificationsPlugin.cancelAll();
  }

  static Future<void> scheduleNotification({
    required int id,
    required String title,
    required String body,
    required DateTime scheduledTime,
    String? payload,
  }) async {
    if (!_isInitialized) await initialize();

    const androidNotificationDetails = AndroidNotificationDetails(
      'instagram_puan_app_scheduled',
      'Instagram Puan App Scheduled',
      channelDescription: 'Scheduled notifications for Instagram Puan App',
      importance: Importance.high,
      priority: Priority.high,
    );

    const iosNotificationDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    const notificationDetails = NotificationDetails(
      android: androidNotificationDetails,
      iOS: iosNotificationDetails,
    );

    await _flutterLocalNotificationsPlugin.zonedSchedule(
      id,
      title,
      body,
      tz.TZDateTime.from(scheduledTime, tz.local),
      notificationDetails,
      payload: payload,
      uiLocalNotificationDateInterpretation: UILocalNotificationDateInterpretation.absoluteTime,
    );
  }

  // Permission handling
  static Future<bool> requestPermissions() async {
    if (!_isInitialized) await initialize();

    final androidImplementation = _flutterLocalNotificationsPlugin
        .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();
    
    if (androidImplementation != null) {
      final granted = await androidImplementation.requestNotificationsPermission();
      return granted ?? false;
    }

    final iosImplementation = _flutterLocalNotificationsPlugin
        .resolvePlatformSpecificImplementation<IOSFlutterLocalNotificationsPlugin>();
    
    if (iosImplementation != null) {
      final granted = await iosImplementation.requestPermissions(
        alert: true,
        badge: true,
        sound: true,
      );
      return granted ?? false;
    }

    return true; // Default to true for other platforms
  }

  static Future<bool> areNotificationsEnabled() async {
    // Check if notifications are enabled at the system level
    final androidImplementation = _flutterLocalNotificationsPlugin
        .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();
    
    if (androidImplementation != null) {
      final enabled = await androidImplementation.areNotificationsEnabled();
      return enabled ?? false;
    }

    return true; // Default to true for iOS and other platforms
  }
}
