import 'package:freezed_annotation/freezed_annotation.dart';

part 'notification_model.freezed.dart';
part 'notification_model.g.dart';

enum NotificationType {
  @JsonValue('badge')
  badge,
  @JsonValue('level')
  level,
  @JsonValue('coins')
  coins,
  @JsonValue('instagram')
  instagram,
  @JsonValue('system')
  system,
  @JsonValue('task_completed')
  taskCompleted,
  @JsonValue('badge_earned')
  badgeEarned,
  @JsonValue('coin_reward')
  coinReward,
  @JsonValue('instagram_sync')
  instagramSync,
  @JsonValue('leaderboard_update')
  leaderboardUpdate,
  @JsonValue('daily_reward')
  dailyReward,
}

enum NotificationActionType {
  @JsonValue('none')
  none,
  @JsonValue('navigate')
  navigate,
  @JsonValue('viewBadge')
  viewBadge,
  @JsonValue('viewProfile')
  viewProfile,
  @JsonValue('viewInstagram')
  viewInstagram,
  @JsonValue('collectCoins')
  collectCoins,
  @JsonValue('open_badge')
  openBadge,
  @JsonValue('refresh_coins')
  refreshCoins,
  @JsonValue('sync_instagram')
  syncInstagram,
}

@freezed
class NotificationModel with _$NotificationModel {
  const factory NotificationModel({
    required int id,
    required String message,
    required bool isRead,
    required DateTime createdAt,
    NotificationType? type, // Bildirim tipi
    String? route, // Tıklanınca gidilecek yol
    NotificationActionType? actionType, // Aksiyon tipi
    String? referenceId, // Referans ID
  }) = _NotificationModel;

  factory NotificationModel.fromJson(Map<String, dynamic> json) =>
      _$NotificationModelFromJson(json);
} 