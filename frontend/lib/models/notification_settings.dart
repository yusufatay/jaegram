import 'package:json_annotation/json_annotation.dart';

part 'notification_settings.g.dart';

@JsonSerializable()
class NotificationSetting {
  final int id;
  @JsonKey(name: 'user_id')
  final int userId;
  @JsonKey(name: 'task_completion')
  final bool taskCompletion;
  @JsonKey(name: 'daily_rewards')
  final bool dailyRewards;
  @JsonKey(name: 'system_updates')
  final bool systemUpdates;
  @JsonKey(name: 'promotional')
  final bool promotional;
  @JsonKey(name: 'push_enabled')
  final bool pushEnabled;
  @JsonKey(name: 'email_enabled')
  final bool emailEnabled;
  @JsonKey(name: 'sms_enabled')
  final bool smsEnabled;
  @JsonKey(name: 'quiet_hours_start')
  final String? quietHoursStart;
  @JsonKey(name: 'quiet_hours_end')
  final String? quietHoursEnd;
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  NotificationSetting({
    required this.id,
    required this.userId,
    required this.taskCompletion,
    required this.dailyRewards,
    required this.systemUpdates,
    required this.promotional,
    required this.pushEnabled,
    required this.emailEnabled,
    required this.smsEnabled,
    this.quietHoursStart,
    this.quietHoursEnd,
    required this.updatedAt,
  });

  factory NotificationSetting.fromJson(Map<String, dynamic> json) => _$NotificationSettingFromJson(json);
  Map<String, dynamic> toJson() => _$NotificationSettingToJson(this);

  NotificationSetting copyWith({
    int? id,
    int? userId,
    bool? taskCompletion,
    bool? dailyRewards,
    bool? systemUpdates,
    bool? promotional,
    bool? pushEnabled,
    bool? emailEnabled,
    bool? smsEnabled,
    String? quietHoursStart,
    String? quietHoursEnd,
    DateTime? updatedAt,
  }) {
    return NotificationSetting(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      taskCompletion: taskCompletion ?? this.taskCompletion,
      dailyRewards: dailyRewards ?? this.dailyRewards,
      systemUpdates: systemUpdates ?? this.systemUpdates,
      promotional: promotional ?? this.promotional,
      pushEnabled: pushEnabled ?? this.pushEnabled,
      emailEnabled: emailEnabled ?? this.emailEnabled,
      smsEnabled: smsEnabled ?? this.smsEnabled,
      quietHoursStart: quietHoursStart ?? this.quietHoursStart,
      quietHoursEnd: quietHoursEnd ?? this.quietHoursEnd,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
