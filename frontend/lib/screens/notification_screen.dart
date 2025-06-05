import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/notification_provider.dart';
import '../providers/user_provider.dart';
import '../providers/badge_provider.dart' as badge_providers;
import '../models/notification_model.dart';
import '../widgets/badge_widget.dart';
import 'package:instagram_puan_app/generated/app_localizations.dart';
import 'package:instagram_puan_app/widgets/gradient_button.dart';

class NotificationScreen extends ConsumerStatefulWidget {
  const NotificationScreen({super.key});

  @override
  ConsumerState<NotificationScreen> createState() => _NotificationScreenState();
}

class _NotificationScreenState extends ConsumerState<NotificationScreen> with TickerProviderStateMixin {
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _fadeController, curve: Curves.easeInOut),
    );
    _fadeController.forward();
    
    // Reset badge counter when this screen is opened
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(badgeNotificationCountProvider.notifier).state = 0;
    });
  }

  @override
  void dispose() {
    _fadeController.dispose();
    super.dispose();
  }  @override
  Widget build(BuildContext context) {
    final notificationState = ref.watch(notificationProvider);
    final localizations = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(localizations.notifications),
        actions: [
          if (notificationState.notifications.isNotEmpty && !notificationState.isLoading)
            IconButton(
              icon: const Icon(Icons.done_all),
              tooltip: localizations.markAllAsRead,
              onPressed: () {
                ref.read(notificationProvider.notifier).markAllAsRead();
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(localizations.allNotificationsMarkedAsRead),
                    behavior: SnackBarBehavior.floating,
                    margin: const EdgeInsets.all(8),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                );
              },
            ),
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'filter') {
                _showFilterDialog(context);
              } else if (value == 'settings') {
                context.push('/settings');
              }
            },
            itemBuilder: (context) => [
              PopupMenuItem<String>(
                value: 'filter',
                child: Row(
                  children: [
                    const Icon(Icons.filter_list),
                    const SizedBox(width: 8),
                    Text(localizations.filterNotifications),
                  ],
                ),
              ),
              PopupMenuItem<String>(
                value: 'settings',
                child: Row(
                  children: [
                    const Icon(Icons.settings),
                    const SizedBox(width: 8),
                    Text(localizations.notificationSettings),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: FadeTransition(
        opacity: _fadeAnimation,
        child: RefreshIndicator(
          onRefresh: () async {
            ref.refresh(notificationProvider);
          },
          child: _buildBody(notificationState, localizations, theme),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          ref.refresh(notificationProvider);
        },
        child: const Icon(Icons.refresh),
      ),
    );
  }

  Widget _buildBody(NotificationState notificationState, AppLocalizations localizations, ThemeData theme) {
    if (notificationState.isLoading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Bildirimler yükleniyor...'),
          ],
        ),
      );
    }

    if (notificationState.error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 48, color: theme.colorScheme.error),
            const SizedBox(height: 16),
            Text(
              localizations.errorLoadingNotifications,
              style: TextStyle(color: theme.colorScheme.error),
            ),
            const SizedBox(height: 16),
            GradientButton(
              text: localizations.tryAgain,
              onPressed: () => ref.refresh(notificationProvider),
            ),
          ],
        ),
      );
    }

    final notifications = notificationState.notifications;
    if (notifications.isEmpty) {
      return _buildEmptyState(localizations, theme);
    }
    
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: notifications.length,
      separatorBuilder: (context, index) => const SizedBox(height: 8),
      itemBuilder: (context, index) {
        final notification = notifications[index];
        final DateTime time = notification.createdAt;
        final relativeTime = _getRelativeTime(time, localizations);
        
        return AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          decoration: BoxDecoration(
            color: notification.isRead
                ? theme.colorScheme.surface
                : theme.colorScheme.primaryContainer.withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: theme.shadowColor.withValues(alpha: 0.05),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Material(
            color: Colors.transparent,
            borderRadius: BorderRadius.circular(12),
            clipBehavior: Clip.antiAlias,
            child: InkWell(
              onTap: () => _handleNotificationTap(notification),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildNotificationIcon(notification, theme),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  _getNotificationTitle(notification, localizations),
                                  style: theme.textTheme.titleSmall?.copyWith(
                                    fontWeight: notification.isRead ? FontWeight.normal : FontWeight.bold,
                                  ),
                                ),
                              ),
                              if (!notification.isRead)
                                Container(
                                  width: 8,
                                  height: 8,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    color: theme.colorScheme.primary,
                                  ),
                                ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(
                            notification.message,
                            style: theme.textTheme.bodyMedium,
                          ),
                          const SizedBox(height: 8),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                relativeTime,
                                style: theme.textTheme.bodySmall?.copyWith(
                                  color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                                ),
                              ),
                              if (_hasAction(notification))
                                TextButton(
                                  onPressed: () => _handleActionButton(notification),
                                  child: Text(_getActionText(notification, localizations)),
                                ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }
  
  Widget _buildEmptyState(AppLocalizations localizations, ThemeData theme) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const SizedBox(height: 80),
        Icon(
          Icons.notifications_none,
          size: 80,
          color: theme.disabledColor,
        ),
        const SizedBox(height: 16),
        Text(
          localizations.noNotifications,
          textAlign: TextAlign.center,
          style: theme.textTheme.titleLarge,
        ),
        const SizedBox(height: 8),
        Text(
          localizations.notificationsWillAppearHere,
          textAlign: TextAlign.center,
          style: theme.textTheme.bodyMedium,
        ),
        const SizedBox(height: 24),
        Center(
          child: GradientButton(
            text: localizations.refresh,
            onPressed: () => ref.refresh(notificationProvider),
          ),
        ),
      ],
    );
  }

  Widget _buildNotificationIcon(NotificationModel notification, ThemeData theme) {
    late IconData icon;
    late Color color;
    
    switch (notification.type) {
      case NotificationType.badge:
        icon = Icons.emoji_events;
        color = Colors.amber;
        break;
      case NotificationType.level:
        icon = Icons.trending_up;
        color = Colors.green;
        break;
      case NotificationType.coins:
        icon = Icons.diamond;
        color = Colors.orange;
        break;
      case NotificationType.instagram:
        icon = Icons.camera_alt;
        color = Colors.purple;
        break;
      case NotificationType.system:
        icon = Icons.info;
        color = theme.colorScheme.primary;
        break;
      default:
        icon = Icons.notifications;
        color = theme.colorScheme.primary;
    }
    
    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.2),
        shape: BoxShape.circle,
      ),
      child: Icon(
        icon,
        color: color,
      ),
    );
  }

  String _getNotificationTitle(NotificationModel notification, AppLocalizations localizations) {
    switch (notification.type) {
      case NotificationType.badge:
        return localizations.newBadgeEarned;
      case NotificationType.level:
        return localizations.levelUp;
      case NotificationType.coins:
        return localizations.coinsReceived;
      case NotificationType.instagram:
        return localizations.instagramUpdate;
      case NotificationType.system:
        return localizations.systemNotification;
      default:
        return localizations.notification;
    }
  }

  String _getRelativeTime(DateTime time, AppLocalizations localizations) {
    final now = DateTime.now();
    final difference = now.difference(time);
    
    if (difference.inDays > 30) {
      final months = difference.inDays ~/ 30;
      return '$months ${months == 1 ? localizations.month : localizations.months} ${localizations.ago}';
    } else if (difference.inDays > 0) {
      return '${difference.inDays} ${difference.inDays == 1 ? localizations.day : localizations.days} ${localizations.ago}';
    } else if (difference.inHours > 0) {
      return '${difference.inHours} ${difference.inHours == 1 ? localizations.hour : localizations.hours} ${localizations.ago}';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} ${difference.inMinutes == 1 ? localizations.minute : localizations.minutes} ${localizations.ago}';
    } else {
      return localizations.justNow;
    }
  }

  bool _hasAction(NotificationModel notification) {
    return notification.actionType != null && notification.actionType != NotificationActionType.none;
  }

  String _getActionText(NotificationModel notification, AppLocalizations localizations) {
    switch (notification.actionType) {
      case NotificationActionType.viewBadge:
        return localizations.viewBadge;
      case NotificationActionType.viewProfile:
        return localizations.viewProfile;
      case NotificationActionType.viewInstagram:
        return localizations.viewInstagram;
      case NotificationActionType.collectCoins:
        return localizations.collectCoins;
      default:
        return localizations.view;
    }
  }

  void _handleNotificationTap(NotificationModel notification) {
    // Mark notification as read
    ref.read(notificationProvider.notifier).markAsRead(notification.id);
    
    // Show details if needed
    if (notification.type == NotificationType.badge && notification.referenceId != null) {
      // Show badge details
      final badgeId = int.tryParse(notification.referenceId!);
      if (badgeId != null) {
        _showBadgeDetails(badgeId);
      }
    }
  }

  void _handleActionButton(NotificationModel notification) {
    // Mark notification as read
    ref.read(notificationProvider.notifier).markAsRead(notification.id);
    
    // Navigate based on action type
    switch (notification.actionType) {
      case NotificationActionType.viewBadge:
        if (notification.referenceId != null) {
          final badgeId = int.tryParse(notification.referenceId!);
          if (badgeId != null) {
            _showBadgeDetails(badgeId);
          }
        }
        break;
      case NotificationActionType.viewProfile:
        context.push('/profile');
        break;
      case NotificationActionType.viewInstagram:
        context.push('/instagram-integration');
        break;
      case NotificationActionType.collectCoins:
        if (notification.referenceId != null) {
          final coinAmount = int.tryParse(notification.referenceId!);
          if (coinAmount != null) {
            _collectCoins(coinAmount);
          }
        }
        break;
      default:
        break;
    }
  }

  void _showBadgeDetails(int badgeId) {
    ref.read(badge_providers.badgeDetailsProvider(badgeId.toString())).whenData((badge) {
      if (badge != null) {
        showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          shape: const RoundedRectangleBorder(
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          builder: (context) {
            return DraggableScrollableSheet(
              initialChildSize: 0.6,
              maxChildSize: 0.9,
              minChildSize: 0.5,
              expand: false,
              builder: (context, scrollController) {
                return SingleChildScrollView(
                  controller: scrollController,
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        BadgeWidget(
                          badge: badge,
                          isEarned: true,
                          showAnimation: true,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          badge.name,
                          style: Theme.of(context).textTheme.titleLarge,
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          badge.description,
                          style: Theme.of(context).textTheme.bodyMedium,
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 24),
                        GradientButton(
                          text: AppLocalizations.of(context)!.close,
                          onPressed: () {
                            Navigator.of(context).pop();
                          },
                        ),
                      ],
                    ),
                  ),
                );
              },
            );
          },
        );
      }
    });
  }

  void _collectCoins(int transactionId) {
    // Animate coins collection
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(AppLocalizations.of(context)!.coinsCollected),
        backgroundColor: Colors.green,
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(8),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    );
    
    // Refresh user provider to update coins count
    ref.refresh(userProvider);
  }

  void _showFilterDialog(BuildContext context) {
    final theme = Theme.of(context);
    final localizations = AppLocalizations.of(context)!;
    
    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setState) {
            final currentFilter = ref.watch(notificationFilterProvider);
            
            return AlertDialog(
              title: Text(localizations.filterNotifications),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CheckboxListTile(
                    title: Text(localizations.showBadgeNotifications),
                    value: currentFilter.contains(NotificationType.badge),
                    onChanged: (value) {
                      setState(() {
                        if (value == true) {
                          ref.read(notificationFilterProvider.notifier).update((state) => 
                            {...state, NotificationType.badge});
                        } else {
                          ref.read(notificationFilterProvider.notifier).update((state) => 
                            state.where((type) => type != NotificationType.badge).toSet());
                        }
                      });
                    },
                  ),
                  CheckboxListTile(
                    title: Text(localizations.showLevelNotifications),
                    value: currentFilter.contains(NotificationType.level),
                    onChanged: (value) {
                      setState(() {
                        if (value == true) {
                          ref.read(notificationFilterProvider.notifier).update((state) => 
                            {...state, NotificationType.level});
                        } else {
                          ref.read(notificationFilterProvider.notifier).update((state) => 
                            state.where((type) => type != NotificationType.level).toSet());
                        }
                      });
                    },
                  ),
                  CheckboxListTile(
                    title: Text(localizations.showCoinNotifications),
                    value: currentFilter.contains(NotificationType.coins),
                    onChanged: (value) {
                      setState(() {
                        if (value == true) {
                          ref.read(notificationFilterProvider.notifier).update((state) => 
                            {...state, NotificationType.coins});
                        } else {
                          ref.read(notificationFilterProvider.notifier).update((state) => 
                            state.where((type) => type != NotificationType.coins).toSet());
                        }
                      });
                    },
                  ),
                  CheckboxListTile(
                    title: Text(localizations.showInstagramNotifications),
                    value: currentFilter.contains(NotificationType.instagram),
                    onChanged: (value) {
                      setState(() {
                        if (value == true) {
                          ref.read(notificationFilterProvider.notifier).update((state) => 
                            {...state, NotificationType.instagram});
                        } else {
                          ref.read(notificationFilterProvider.notifier).update((state) => 
                            state.where((type) => type != NotificationType.instagram).toSet());
                        }
                      });
                    },
                  ),
                  CheckboxListTile(
                    title: Text(localizations.showSystemNotifications),
                    value: currentFilter.contains(NotificationType.system),
                    onChanged: (value) {
                      setState(() {
                        if (value == true) {
                          ref.read(notificationFilterProvider.notifier).update((state) => 
                            {...state, NotificationType.system});
                        } else {
                          ref.read(notificationFilterProvider.notifier).update((state) => 
                            state.where((type) => type != NotificationType.system).toSet());
                        }
                      });
                    },
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    ref.read(notificationFilterProvider.notifier).state = {
                      NotificationType.badge,
                      NotificationType.level,
                      NotificationType.coins,
                      NotificationType.instagram,
                      NotificationType.system
                    };
                    Navigator.of(context).pop();
                  },
                  child: Text(localizations.resetFilters),
                ),
                TextButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                  },
                  child: Text(localizations.apply),
                ),
              ],
            );
          },
        );
      },
    );
  }
}