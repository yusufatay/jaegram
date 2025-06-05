// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'daily_reward.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

DailyRewardStatus _$DailyRewardStatusFromJson(Map<String, dynamic> json) =>
    DailyRewardStatus(
      canClaim: json['can_claim'] as bool,
      currentStreak: (json['current_streak'] as num).toInt(),
      nextReward: (json['next_reward'] as num).toInt(),
      lastClaim: json['last_claim'] == null
          ? null
          : DateTime.parse(json['last_claim'] as String),
    );

Map<String, dynamic> _$DailyRewardStatusToJson(DailyRewardStatus instance) =>
    <String, dynamic>{
      'can_claim': instance.canClaim,
      'current_streak': instance.currentStreak,
      'next_reward': instance.nextReward,
      'last_claim': instance.lastClaim?.toIso8601String(),
    };

DailyRewardResponse _$DailyRewardResponseFromJson(Map<String, dynamic> json) =>
    DailyRewardResponse(
      success: json['success'] as bool,
      diamondsAwarded: (json['coins_awarded'] as num).toInt(),
      streakDay: (json['streak_day'] as num).toInt(),
      newBalance: (json['new_balance'] as num).toInt(),
      message: json['message'] as String,
    );

Map<String, dynamic> _$DailyRewardResponseToJson(
        DailyRewardResponse instance) =>
    <String, dynamic>{
      'success': instance.success,
      'coins_awarded': instance.diamondsAwarded,
      'streak_day': instance.streakDay,
      'new_balance': instance.newBalance,
      'message': instance.message,
    };
