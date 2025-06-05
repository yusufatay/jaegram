import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../models/notification_settings.dart';
import '../providers/user_provider.dart';
import '../services/notification_settings_service.dart';

class NotificationSettingsScreen extends ConsumerStatefulWidget {
  const NotificationSettingsScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<NotificationSettingsScreen> createState() => _NotificationSettingsScreenState();
}

class _NotificationSettingsScreenState extends ConsumerState<NotificationSettingsScreen> {
  final NotificationSettingsService _notificationService = NotificationSettingsService();
  NotificationSetting? _currentSettings;
  bool _isLoading = true;
  bool _isSaving = false;

  TimeOfDay? _quietHoursStart;
  TimeOfDay? _quietHoursEnd;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final userAsync = ref.read(userProvider);
    if (userAsync.value?.token == null) return;
    
    try {
      final settings = await _notificationService.getSettings(userAsync.value!.token!);
      if (mounted) {
        setState(() {
          _currentSettings = settings;
          _quietHoursStart = settings.quietHoursStart != null 
              ? _parseTimeString(settings.quietHoursStart!) 
              : null;
          _quietHoursEnd = settings.quietHoursEnd != null 
              ? _parseTimeString(settings.quietHoursEnd!) 
              : null;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
      }
      _showErrorSnackBar('Failed to load notification settings');
    }
  }

  Future<void> _saveSettings() async {
    if (_currentSettings == null) return;

    if (mounted) {
      setState(() => _isSaving = true);
    }
    final userAsync = ref.read(userProvider);
    if (userAsync.value?.token == null) return;

    try {
      final updatedSettings = NotificationSetting(
        id: _currentSettings!.id,
        userId: _currentSettings!.userId,
        taskCompletion: _currentSettings!.taskCompletion,
        dailyRewards: _currentSettings!.dailyRewards,
        systemUpdates: _currentSettings!.systemUpdates,
        promotional: _currentSettings!.promotional,
        pushEnabled: _currentSettings!.pushEnabled,
        emailEnabled: _currentSettings!.emailEnabled,
        smsEnabled: _currentSettings!.smsEnabled,
        quietHoursStart: _quietHoursStart != null ? _formatTimeOfDay(_quietHoursStart!) : null,
        quietHoursEnd: _quietHoursEnd != null ? _formatTimeOfDay(_quietHoursEnd!) : null,
        updatedAt: DateTime.now(),
      );

      await _notificationService.updateSettings(userAsync.value!.token!, updatedSettings);
      if (mounted) {
        setState(() => _isSaving = false);
      }
      _showSuccessSnackBar('Notification settings updated successfully');
    } catch (e) {
      if (mounted) {
        setState(() => _isSaving = false);
      }
      _showErrorSnackBar('Failed to update notification settings');
    }
  }

  Future<void> _sendTestNotification(String type) async {
    final userAsync = ref.read(userProvider);
    if (userAsync.value?.token == null) return;
    
    try {
      await _notificationService.sendTestNotification(userAsync.value!.token!, type);
      _showSuccessSnackBar('Test notification sent');
    } catch (e) {
      _showErrorSnackBar('Failed to send test notification');
    }
  }

  TimeOfDay _parseTimeString(String timeString) {
    final parts = timeString.split(':');
    return TimeOfDay(hour: int.parse(parts[0]), minute: int.parse(parts[1]));
  }

  String _formatTimeOfDay(TimeOfDay time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.green),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notification Settings'),
        actions: [
          if (!_isLoading && _currentSettings != null)
            IconButton(
              onPressed: _isSaving ? null : _saveSettings,
              icon: _isSaving 
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.save),
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _currentSettings == null
              ? const Center(child: Text('Failed to load settings'))
              : _buildSettingsContent(),
    );
  }

  Widget _buildSettingsContent() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildNotificationTypesSection(),
          const SizedBox(height: 24),
          _buildDeliveryMethodsSection(),
          const SizedBox(height: 24),
          _buildQuietHoursSection(),
          const SizedBox(height: 24),
          _buildTestSection(),
        ],
      ),
    );
  }

  Widget _buildNotificationTypesSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Notification Types',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              title: const Text('Task Completion'),
              subtitle: const Text('Get notified when tasks are completed'),
              value: _currentSettings!.taskCompletion,
              onChanged: (value) {
                setState(() {
                  _currentSettings = NotificationSetting(
                    id: _currentSettings!.id,
                    userId: _currentSettings!.userId,
                    taskCompletion: value,
                    dailyRewards: _currentSettings!.dailyRewards,
                    systemUpdates: _currentSettings!.systemUpdates,
                    promotional: _currentSettings!.promotional,
                    pushEnabled: _currentSettings!.pushEnabled,
                    emailEnabled: _currentSettings!.emailEnabled,
                    smsEnabled: _currentSettings!.smsEnabled,
                    quietHoursStart: _currentSettings!.quietHoursStart,
                    quietHoursEnd: _currentSettings!.quietHoursEnd,
                    updatedAt: _currentSettings!.updatedAt,
                  );
                });
              },
            ),
            SwitchListTile(
              title: const Text('Daily Rewards'),
              subtitle: const Text('Get notified about daily reward availability'),
              value: _currentSettings!.dailyRewards,
              onChanged: (value) {
                setState(() {
                  _currentSettings = NotificationSetting(
                    id: _currentSettings!.id,
                    userId: _currentSettings!.userId,
                    taskCompletion: _currentSettings!.taskCompletion,
                    dailyRewards: value,
                    systemUpdates: _currentSettings!.systemUpdates,
                    promotional: _currentSettings!.promotional,
                    pushEnabled: _currentSettings!.pushEnabled,
                    emailEnabled: _currentSettings!.emailEnabled,
                    smsEnabled: _currentSettings!.smsEnabled,
                    quietHoursStart: _currentSettings!.quietHoursStart,
                    quietHoursEnd: _currentSettings!.quietHoursEnd,
                    updatedAt: _currentSettings!.updatedAt,
                  );
                });
              },
            ),
            SwitchListTile(
              title: const Text('System Updates'),
              subtitle: const Text('Get notified about app updates and maintenance'),
              value: _currentSettings!.systemUpdates,
              onChanged: (value) {
                setState(() {
                  _currentSettings = NotificationSetting(
                    id: _currentSettings!.id,
                    userId: _currentSettings!.userId,
                    taskCompletion: _currentSettings!.taskCompletion,
                    dailyRewards: _currentSettings!.dailyRewards,
                    systemUpdates: value,
                    promotional: _currentSettings!.promotional,
                    pushEnabled: _currentSettings!.pushEnabled,
                    emailEnabled: _currentSettings!.emailEnabled,
                    smsEnabled: _currentSettings!.smsEnabled,
                    quietHoursStart: _currentSettings!.quietHoursStart,
                    quietHoursEnd: _currentSettings!.quietHoursEnd,
                    updatedAt: _currentSettings!.updatedAt,
                  );
                });
              },
            ),
            SwitchListTile(
              title: const Text('Promotional'),
              subtitle: const Text('Get notified about special offers and events'),
              value: _currentSettings!.promotional,
              onChanged: (value) {
                setState(() {
                  _currentSettings = NotificationSetting(
                    id: _currentSettings!.id,
                    userId: _currentSettings!.userId,
                    taskCompletion: _currentSettings!.taskCompletion,
                    dailyRewards: _currentSettings!.dailyRewards,
                    systemUpdates: _currentSettings!.systemUpdates,
                    promotional: value,
                    pushEnabled: _currentSettings!.pushEnabled,
                    emailEnabled: _currentSettings!.emailEnabled,
                    smsEnabled: _currentSettings!.smsEnabled,
                    quietHoursStart: _currentSettings!.quietHoursStart,
                    quietHoursEnd: _currentSettings!.quietHoursEnd,
                    updatedAt: _currentSettings!.updatedAt,
                  );
                });
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDeliveryMethodsSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Delivery Methods',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            SwitchListTile(
              title: const Text('Push Notifications'),
              subtitle: const Text('Receive notifications on your device'),
              value: _currentSettings!.pushEnabled,
              onChanged: (value) {
                setState(() {
                  _currentSettings = NotificationSetting(
                    id: _currentSettings!.id,
                    userId: _currentSettings!.userId,
                    taskCompletion: _currentSettings!.taskCompletion,
                    dailyRewards: _currentSettings!.dailyRewards,
                    systemUpdates: _currentSettings!.systemUpdates,
                    promotional: _currentSettings!.promotional,
                    pushEnabled: value,
                    emailEnabled: _currentSettings!.emailEnabled,
                    smsEnabled: _currentSettings!.smsEnabled,
                    quietHoursStart: _currentSettings!.quietHoursStart,
                    quietHoursEnd: _currentSettings!.quietHoursEnd,
                    updatedAt: _currentSettings!.updatedAt,
                  );
                });
              },
            ),
            SwitchListTile(
              title: const Text('Email Notifications'),
              subtitle: const Text('Receive notifications via email'),
              value: _currentSettings!.emailEnabled,
              onChanged: (value) {
                setState(() {
                  _currentSettings = NotificationSetting(
                    id: _currentSettings!.id,
                    userId: _currentSettings!.userId,
                    taskCompletion: _currentSettings!.taskCompletion,
                    dailyRewards: _currentSettings!.dailyRewards,
                    systemUpdates: _currentSettings!.systemUpdates,
                    promotional: _currentSettings!.promotional,
                    pushEnabled: _currentSettings!.pushEnabled,
                    emailEnabled: value,
                    smsEnabled: _currentSettings!.smsEnabled,
                    quietHoursStart: _currentSettings!.quietHoursStart,
                    quietHoursEnd: _currentSettings!.quietHoursEnd,
                    updatedAt: _currentSettings!.updatedAt,
                  );
                });
              },
            ),
            SwitchListTile(
              title: const Text('SMS Notifications'),
              subtitle: const Text('Receive notifications via SMS'),
              value: _currentSettings!.smsEnabled,
              onChanged: (value) {
                setState(() {
                  _currentSettings = NotificationSetting(
                    id: _currentSettings!.id,
                    userId: _currentSettings!.userId,
                    taskCompletion: _currentSettings!.taskCompletion,
                    dailyRewards: _currentSettings!.dailyRewards,
                    systemUpdates: _currentSettings!.systemUpdates,
                    promotional: _currentSettings!.promotional,
                    pushEnabled: _currentSettings!.pushEnabled,
                    emailEnabled: _currentSettings!.emailEnabled,
                    smsEnabled: value,
                    quietHoursStart: _currentSettings!.quietHoursStart,
                    quietHoursEnd: _currentSettings!.quietHoursEnd,
                    updatedAt: _currentSettings!.updatedAt,
                  );
                });
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuietHoursSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Quiet Hours',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              'Set a time range when you don\'t want to receive notifications',
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: ListTile(
                    title: const Text('Start Time'),
                    subtitle: Text(_quietHoursStart?.format(context) ?? 'Not set'),
                    trailing: const Icon(Icons.access_time),
                    onTap: () async {
                      final time = await showTimePicker(
                        context: context,
                        initialTime: _quietHoursStart ?? const TimeOfDay(hour: 22, minute: 0),
                      );
                      if (time != null) {
                        setState(() => _quietHoursStart = time);
                      }
                    },
                  ),
                ),
                Expanded(
                  child: ListTile(
                    title: const Text('End Time'),
                    subtitle: Text(_quietHoursEnd?.format(context) ?? 'Not set'),
                    trailing: const Icon(Icons.access_time),
                    onTap: () async {
                      final time = await showTimePicker(
                        context: context,
                        initialTime: _quietHoursEnd ?? const TimeOfDay(hour: 8, minute: 0),
                      );
                      if (time != null) {
                        setState(() => _quietHoursEnd = time);
                      }
                    },
                  ),
                ),
              ],
            ),
            if (_quietHoursStart != null || _quietHoursEnd != null)
              TextButton(
                onPressed: () {
                  setState(() {
                    _quietHoursStart = null;
                    _quietHoursEnd = null;
                  });
                },
                child: const Text('Clear Quiet Hours'),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildTestSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Test Notifications',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              'Send test notifications to verify your settings',
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              children: [
                ElevatedButton(
                  onPressed: () => _sendTestNotification('task_completion'),
                  child: const Text('Task Complete'),
                ),
                ElevatedButton(
                  onPressed: () => _sendTestNotification('daily_reward'),
                  child: const Text('Daily Reward'),
                ),
                ElevatedButton(
                  onPressed: () => _sendTestNotification('system_update'),
                  child: const Text('System Update'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
