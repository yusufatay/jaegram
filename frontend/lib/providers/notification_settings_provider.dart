import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

// General notification settings
final notificationEnabledProvider = StateNotifierProvider<NotificationSettingsNotifier, bool>((ref) {
  return NotificationSettingsNotifier('notification_enabled', true);
});

final badgeNotificationEnabledProvider = StateNotifierProvider<NotificationSettingsNotifier, bool>((ref) {
  return NotificationSettingsNotifier('badge_notification_enabled', true);
});

final soundNotificationEnabledProvider = StateNotifierProvider<NotificationSettingsNotifier, bool>((ref) {
  return NotificationSettingsNotifier('sound_notification_enabled', true);
});

class NotificationSettingsNotifier extends StateNotifier<bool> {
  final String _key;
  final bool _defaultValue;

  NotificationSettingsNotifier(this._key, this._defaultValue) : super(_defaultValue) {
    _loadSetting();
  }

  Future<void> _loadSetting() async {
    final prefs = await SharedPreferences.getInstance();
    state = prefs.getBool(_key) ?? _defaultValue;
  }

  Future<void> toggle() async {
    state = !state;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_key, state);
  }

  Future<void> setValue(bool value) async {
    state = value;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_key, value);
  }
}
