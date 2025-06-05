import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/notification_settings.dart';
import '../utils/api_constants.dart';

class NotificationSettingsService {
  final String baseUrl = ApiConstants.baseUrl;

  // Get Current Settings
  Future<NotificationSetting> getSettings(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/notifications/settings'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return NotificationSetting.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to load notification settings');
  }

  // Update Settings
  Future<NotificationSetting> updateSettings(String token, NotificationSetting settings) async {
    final response = await http.put(
      Uri.parse('$baseUrl/notifications/settings'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode(settings.toJson()),
    );

    if (response.statusCode == 200) {
      return NotificationSetting.fromJson(jsonDecode(response.body));
    }
    throw Exception('Failed to update notification settings');
  }

  // Test Notification
  Future<bool> sendTestNotification(String token, String type) async {
    final response = await http.post(
      Uri.parse('$baseUrl/notifications/test'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'type': type}),
    );

    return response.statusCode == 200;
  }

  // Register FCM Token
  Future<bool> registerFCMToken(String token, String fcmToken, String deviceType) async {
    final response = await http.post(
      Uri.parse('$baseUrl/notifications/register-token'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'fcm_token': fcmToken,
        'device_type': deviceType,
      }),
    );

    return response.statusCode == 200;
  }

  // Unregister FCM Token
  Future<bool> unregisterFCMToken(String token, String fcmToken) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/notifications/unregister-token'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'fcm_token': fcmToken}),
    );

    return response.statusCode == 200;
  }

  // Get Notification History
  Future<List<Map<String, dynamic>>> getNotificationHistory(String token, {int limit = 50}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/notifications/history?limit=$limit'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return List<Map<String, dynamic>>.from(jsonDecode(response.body));
    }
    throw Exception('Failed to load notification history');
  }

  // Mark Notifications as Read
  Future<bool> markAsRead(String token, List<int> notificationIds) async {
    final response = await http.put(
      Uri.parse('$baseUrl/notifications/mark-read'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'notification_ids': notificationIds}),
    );

    return response.statusCode == 200;
  }

  // Clear All Notifications
  Future<bool> clearAllNotifications(String token) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/notifications/clear-all'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    return response.statusCode == 200;
  }

  // Get Notification Preferences
  Future<Map<String, dynamic>> getNotificationPreferences(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/notifications/preferences'),
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    throw Exception('Failed to load notification preferences');
  }

  // Update Notification Preferences
  Future<bool> updateNotificationPreferences(String token, Map<String, dynamic> preferences) async {
    final response = await http.put(
      Uri.parse('$baseUrl/notifications/preferences'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode(preferences),
    );

    return response.statusCode == 200;
  }
}
