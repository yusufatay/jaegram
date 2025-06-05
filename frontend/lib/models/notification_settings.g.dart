// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'notification_settings.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

NotificationSetting _$NotificationSettingFromJson(Map<String, dynamic> json) =>
    NotificationSetting(
      id: (json['id'] as num).toInt(),
      userId: (json['user_id'] as num).toInt(),
      taskCompletion: json['task_completion'] as bool,
      dailyRewards: json['daily_rewards'] as bool,
      systemUpdates: json['system_updates'] as bool,
      promotional: json['promotional'] as bool,
      pushEnabled: json['push_enabled'] as bool,
      emailEnabled: json['email_enabled'] as bool,
      smsEnabled: json['sms_enabled'] as bool,
      quietHoursStart: json['quiet_hours_start'] as String?,
      quietHoursEnd: json['quiet_hours_end'] as String?,
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );

Map<String, dynamic> _$NotificationSettingToJson(
        NotificationSetting instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'task_completion': instance.taskCompletion,
      'daily_rewards': instance.dailyRewards,
      'system_updates': instance.systemUpdates,
      'promotional': instance.promotional,
      'push_enabled': instance.pushEnabled,
      'email_enabled': instance.emailEnabled,
      'sms_enabled': instance.smsEnabled,
      'quiet_hours_start': instance.quietHoursStart,
      'quiet_hours_end': instance.quietHoursEnd,
      'updated_at': instance.updatedAt.toIso8601String(),
    };
