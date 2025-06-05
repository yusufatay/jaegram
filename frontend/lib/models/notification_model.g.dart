// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'notification_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$NotificationModelImpl _$$NotificationModelImplFromJson(
        Map<String, dynamic> json) =>
    _$NotificationModelImpl(
      id: (json['id'] as num).toInt(),
      message: json['message'] as String,
      isRead: json['isRead'] as bool,
      createdAt: DateTime.parse(json['createdAt'] as String),
      type: $enumDecodeNullable(_$NotificationTypeEnumMap, json['type']),
      route: json['route'] as String?,
      actionType: $enumDecodeNullable(
          _$NotificationActionTypeEnumMap, json['actionType']),
      referenceId: json['referenceId'] as String?,
    );

Map<String, dynamic> _$$NotificationModelImplToJson(
        _$NotificationModelImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'message': instance.message,
      'isRead': instance.isRead,
      'createdAt': instance.createdAt.toIso8601String(),
      'type': _$NotificationTypeEnumMap[instance.type],
      'route': instance.route,
      'actionType': _$NotificationActionTypeEnumMap[instance.actionType],
      'referenceId': instance.referenceId,
    };

const _$NotificationTypeEnumMap = {
  NotificationType.badge: 'badge',
  NotificationType.level: 'level',
  NotificationType.coins: 'coins',
  NotificationType.instagram: 'instagram',
  NotificationType.system: 'system',
  NotificationType.taskCompleted: 'task_completed',
  NotificationType.badgeEarned: 'badge_earned',
  NotificationType.coinReward: 'coin_reward',
  NotificationType.instagramSync: 'instagram_sync',
  NotificationType.leaderboardUpdate: 'leaderboard_update',
  NotificationType.dailyReward: 'daily_reward',
};

const _$NotificationActionTypeEnumMap = {
  NotificationActionType.none: 'none',
  NotificationActionType.navigate: 'navigate',
  NotificationActionType.viewBadge: 'viewBadge',
  NotificationActionType.viewProfile: 'viewProfile',
  NotificationActionType.viewInstagram: 'viewInstagram',
  NotificationActionType.collectCoins: 'collectCoins',
  NotificationActionType.openBadge: 'open_badge',
  NotificationActionType.refreshCoins: 'refresh_coins',
  NotificationActionType.syncInstagram: 'sync_instagram',
};
