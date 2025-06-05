import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:instagram_puan_app/providers/user_provider.dart';
import 'package:instagram_puan_app/providers/notification_provider.dart';
import 'package:instagram_puan_app/services/statistics_service.dart';
import 'package:instagram_puan_app/themes/app_theme.dart';
import 'package:timeago/timeago.dart' as timeago;

class NotificationsScreen extends ConsumerWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notificationState = ref.watch(notificationProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Bildirimler'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: AppTheme.primaryGradient,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.refresh(notificationProvider),
          ),
        ],
      ),
      body: _buildNotificationsList(context, ref, notificationState.notifications),
    );
  }

  Widget _buildNotificationsList(BuildContext context, WidgetRef ref, List<dynamic> notifications) {
    final unreadCount = notifications.where((n) => !(n['isRead'] ?? false)).length;
    
    if (notifications.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.notifications_none, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            Text(
              'Henüz bildiriminiz yok',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Yeni görevler ve ödüller hakkında buradan bilgilendirileceğiz',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey,
              ),
            ),
          ],
        ),
      );
    }

    return Column(
      children: [
        if (unreadCount > 0)
          Container(
            padding: const EdgeInsets.all(16),
            margin: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                Icon(Icons.notifications_active, color: Colors.white),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    '$unreadCount okunmamış bildiriminiz var',
                    style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ),
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: notifications.length,
            itemBuilder: (context, index) {
              final notification = notifications[index];
              return _buildNotificationCard(context, ref, notification);
            },
          ),
        ),
      ],
    );
  }

  Widget _buildNotificationCard(BuildContext context, WidgetRef ref, Map<String, dynamic> notification) {
    final isRead = notification['read'] ?? false;
    final type = notification['type'] ?? 'info';
    final title = notification['title'] ?? '';
    final message = notification['message'] ?? '';
    final createdAt = notification['created_at'] ?? '';

    IconData getTypeIcon() {
      switch (type) {
        case 'task_completed':
          return Icons.task_alt;
        case 'reward':
          return Icons.card_giftcard;
        case 'level_up':
          return Icons.military_tech;
        case 'warning':
          return Icons.warning;
        case 'system':
          return Icons.settings;
        default:
          return Icons.info;
      }
    }

    Color getTypeColor() {
      switch (type) {
        case 'task_completed':
          return Colors.green;
        case 'reward':
          return Colors.purple;
        case 'level_up':
          return Colors.orange;
        case 'warning':
          return Colors.red;
        case 'system':
          return Colors.blue;
        default:
          return Colors.grey;
      }
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: isRead ? 1 : 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () async {
          if (!isRead) {
            final statisticsService = ref.read(statisticsServiceProvider);
            final auth = ref.read(userProvider);
            
            await auth.when(
              data: (user) async {
                if (user?.token != null && notification['id'] != null) {
                  final notificationId = int.tryParse(notification['id'].toString()) ?? 0;
                  await statisticsService.markNotificationRead(user!.token!, notificationId);
                  ref.refresh(notificationProvider);
                }
              },
              loading: () {},
              error: (error, stack) {},
            );
          }
        },
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),                color: isRead ? null : Colors.blue.withValues(alpha: 0.05),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: getTypeColor().withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  getTypeIcon(),
                  color: getTypeColor(),
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            title,
                            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                              fontWeight: isRead ? FontWeight.normal : FontWeight.bold,
                            ),
                          ),
                        ),
                        if (!isRead)
                          Container(
                            width: 8,
                            height: 8,
                            decoration: BoxDecoration(
                              color: Colors.blue,
                              borderRadius: BorderRadius.circular(4),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      message,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Colors.grey[600],
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _formatDate(createdAt),
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.grey[500],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatDate(String dateString) {
    try {
      final date = DateTime.parse(dateString);
      return timeago.format(date, locale: 'tr');
    } catch (e) {
      return 'Bilinmeyen';
    }
  }
}
