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
    } catch (e) {
      setState(() => _isLoading = false);
      _showErrorSnackBar('Failed to load notification settings');
    }
  }

  Future<void> _saveSettings() async {
    if (_currentSettings == null) return;

    setState(() => _isSaving = true);
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
      setState(() => _isSaving = false);
      _showSuccessSnackBar('Bildirim ayarları başarıyla güncellendi');
    } catch (e) {
      setState(() => _isSaving = false);
      _showErrorSnackBar('Bildirim ayarları güncellenemedi');
    }
  }

  Future<void> _sendTestNotification(String type) async {
    final userAsync = ref.read(userProvider);
    if (userAsync.value?.token == null) return;
    
    try {
      await _notificationService.sendTestNotification(userAsync.value!.token!, type);
      _showSuccessSnackBar('Test bildirimi gönderildi');
    } catch (e) {
      _showErrorSnackBar('Test bildirimi gönderilemedi');
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
        title: const Text('🔔 Bildirim Ayarları'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          if (!_isLoading && _currentSettings != null)
            IconButton(
              onPressed: _isSaving ? null : _saveSettings,
              icon: _isSaving 
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : const Icon(Icons.save),
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _currentSettings == null
              ? const Center(child: Text('Ayarlar yüklenemedi'))
              : _buildSettingsContent(),
    );
  }

  Widget _buildSettingsContent() {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Colors.deepPurple, Colors.purple, Colors.indigo],
        ),
      ),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildNotificationTypeSection(),
            const SizedBox(height: 24),
            _buildDeliveryMethodsSection(),
            const SizedBox(height: 24),
            _buildQuietHoursSection(),
            const SizedBox(height: 24),
            _buildTestSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildNotificationTypeSection() {
    if (_currentSettings == null) {
      return const Center(child: CircularProgressIndicator());
    }

    return Card(
      elevation: 8,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.notifications_active, color: Colors.deepPurple, size: 28),
                const SizedBox(width: 12),
                Text(
                  'Bildirim Türleri',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.deepPurple,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            
            // Core Notifications
            _buildSectionHeader('📝 Görev Bildirimleri'),
            _buildNotificationToggle(
              'Görev Atandı',
              'Yeni görev atandığında bildirim al',
              _currentSettings!.taskCompletion,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(taskCompletion: value)),
              icon: Icons.assignment,
            ),
            _buildNotificationToggle(
              'Görev Tamamlandı',
              'Görev tamamlandığında bildirim al',
              _currentSettings!.taskCompletion,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(taskCompletion: value)),
              icon: Icons.check_circle,
            ),
            _buildNotificationToggle(
              'Görev Süresi Doldu',
              'Görev süresi dolduğunda bildirim al',
              _currentSettings!.taskCompletion,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(taskCompletion: value)),
              icon: Icons.timer_off,
            ),
            
            const SizedBox(height: 24),
            
            // Coin & Rewards
            _buildSectionHeader('💰 Coin ve Ödüller'),
            _buildNotificationToggle(
              'Coin Kazandın',
              'Coin kazandığında bildirim al',
              _currentSettings!.dailyRewards,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(dailyRewards: value)),
              icon: Icons.diamond,
            ),
            _buildNotificationToggle(
              'Günlük Ödüller',
              'Günlük ödül bildirimlerini al',
              _currentSettings!.dailyRewards,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(dailyRewards: value)),
              icon: Icons.card_giftcard,
            ),
            _buildNotificationToggle(
              'Çekim İşlemleri',
              'Coin çekim durumu bildirimleri',
              _currentSettings!.systemUpdates,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(systemUpdates: value)),
              icon: Icons.account_balance_wallet,
            ),
            
            const SizedBox(height: 24),
            
            // Social Features
            _buildSectionHeader('👥 Sosyal Özellikler'),
            _buildNotificationToggle(
              'Rozet Kazandın',
              'Yeni rozet kazandığında bildirim al',
              _currentSettings!.promotional,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(promotional: value)),
              icon: Icons.emoji_events,
            ),
            _buildNotificationToggle(
              'Seviye Atladın',
              'Seviye atladığında bildirim al',
              _currentSettings!.promotional,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(promotional: value)),
              icon: Icons.trending_up,
            ),
            _buildNotificationToggle(
              'Referans Ödülleri',
              'Referans ödülü bildirimleri',
              _currentSettings!.promotional,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(promotional: value)),
              icon: Icons.people,
            ),
            
            const SizedBox(height: 24),
            
            // Security & Privacy
            _buildSectionHeader('🔒 Güvenlik ve Gizlilik'),
            _buildNotificationToggle(
              'Güvenlik Uyarıları',
              'Şüpheli aktivite bildirimleri',
              _currentSettings!.systemUpdates,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(systemUpdates: value)),
              icon: Icons.security,
              isImportant: true,
            ),
            _buildNotificationToggle(
              'GDPR İstekleri',
              'Veri işleme durumu bildirimleri',
              _currentSettings!.systemUpdates,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(systemUpdates: value)),
              icon: Icons.privacy_tip,
            ),
            
            const SizedBox(height: 24),
            
            // Mental Health
            _buildSectionHeader('🧠 Ruh Sağlığı'),
            _buildNotificationToggle(
              'Wellness Hatırlatıcıları',
              'Ruh sağlığı önerilerini al',
              _currentSettings!.promotional,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(promotional: value)),
              icon: Icons.psychology,
            ),
            _buildNotificationToggle(
              'Mola Önerileri',
              'Aşırı kullanım uyarıları',
              _currentSettings!.promotional,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(promotional: value)),
              icon: Icons.self_improvement,
            ),
            
            const SizedBox(height: 24),
            
            // System
            _buildSectionHeader('⚙️ Sistem'),
            _buildNotificationToggle(
              'Sistem Güncellemeleri',
              'Yeni özellik ve güncelleme bildirimleri',
              _currentSettings!.systemUpdates,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(systemUpdates: value)),
              icon: Icons.system_update,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleSmall?.copyWith(
          color: Colors.deepPurple,
          fontWeight: FontWeight.w600,
          fontSize: 16,
        ),
      ),
    );
  }

  Widget _buildNotificationToggle(
    String title,
    String subtitle,
    bool value,
    ValueChanged<bool> onChanged,
    {
      IconData? icon,
      bool isImportant = false,
    }
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: SwitchListTile(
        secondary: icon != null 
          ? Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: isImportant 
                  ? Colors.red.shade50
                  : Colors.deepPurple.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                icon, 
                color: isImportant 
                  ? Colors.red 
                  : Colors.deepPurple,
                size: 24,
              ),
            )
          : null,
        title: Text(
          title,
          style: TextStyle(
            fontWeight: isImportant ? FontWeight.bold : FontWeight.w500,
            color: isImportant ? Colors.red : Colors.black87,
          ),
        ),
        subtitle: Text(
          subtitle,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Colors.grey[600],
          ),
        ),
        value: value,
        onChanged: onChanged,
        activeColor: isImportant 
          ? Colors.red 
          : Colors.deepPurple,
      ),
    );
  }

  Widget _buildDeliveryMethodsSection() {
    return Card(
      elevation: 8,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.send, color: Colors.deepPurple, size: 28),
                const SizedBox(width: 12),
                Text(
                  'Bildirim Yöntemleri',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.deepPurple,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            _buildNotificationToggle(
              'Push Bildirimleri',
              'Cihazınızda bildirim alın',
              _currentSettings!.pushEnabled,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(pushEnabled: value)),
              icon: Icons.phone_android,
            ),
            _buildNotificationToggle(
              'E-posta Bildirimleri',
              'E-posta ile bildirim alın',
              _currentSettings!.emailEnabled,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(emailEnabled: value)),
              icon: Icons.email,
            ),
            _buildNotificationToggle(
              'SMS Bildirimleri',
              'SMS ile bildirim alın',
              _currentSettings!.smsEnabled,
              (value) => setState(() => _currentSettings = _currentSettings!.copyWith(smsEnabled: value)),
              icon: Icons.sms,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuietHoursSection() {
    return Card(
      elevation: 8,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.do_not_disturb, color: Colors.deepPurple, size: 28),
                const SizedBox(width: 12),
                Text(
                  'Sessiz Saatler',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.deepPurple,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Bildirim almak istemediğiniz zaman aralığını belirleyin',
              style: TextStyle(color: Colors.grey[600]),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.grey[50],
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.grey.shade200),
                    ),
                    child: ListTile(
                      title: const Text('Başlangıç'),
                      subtitle: Text(_quietHoursStart?.format(context) ?? 'Belirtilmedi'),
                      trailing: const Icon(Icons.access_time, color: Colors.deepPurple),
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
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.grey[50],
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.grey.shade200),
                    ),
                    child: ListTile(
                      title: const Text('Bitiş'),
                      subtitle: Text(_quietHoursEnd?.format(context) ?? 'Belirtilmedi'),
                      trailing: const Icon(Icons.access_time, color: Colors.deepPurple),
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
                ),
              ],
            ),
            if (_quietHoursStart != null || _quietHoursEnd != null)
              Padding(
                padding: const EdgeInsets.only(top: 16),
                child: TextButton.icon(
                  onPressed: () {
                    setState(() {
                      _quietHoursStart = null;
                      _quietHoursEnd = null;
                    });
                  },
                  icon: const Icon(Icons.clear),
                  label: const Text('Sessiz Saatleri Temizle'),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildTestSection() {
    return Card(
      elevation: 8,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.bug_report, color: Colors.deepPurple, size: 28),
                const SizedBox(width: 12),
                Text(
                  'Test Bildirimleri',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.deepPurple,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Ayarlarınızı test etmek için bildirim gönderin',
              style: TextStyle(color: Colors.grey[600]),
            ),
            const SizedBox(height: 20),
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                ElevatedButton.icon(
                  onPressed: () => _sendTestNotification('task_completion'),
                  icon: const Icon(Icons.check_circle),
                  label: const Text('Görev Tamamlandı'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                ),
                ElevatedButton.icon(
                  onPressed: () => _sendTestNotification('daily_reward'),
                  icon: const Icon(Icons.card_giftcard),
                  label: const Text('Günlük Ödül'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.orange,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                ),
                ElevatedButton.icon(
                  onPressed: () => _sendTestNotification('security_alert'),
                  icon: const Icon(Icons.security),
                  label: const Text('Güvenlik Uyarısı'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                ),
                ElevatedButton.icon(
                  onPressed: () => _sendTestNotification('badge_earned'),
                  icon: const Icon(Icons.emoji_events),
                  label: const Text('Rozet Kazandın'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.purple,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
