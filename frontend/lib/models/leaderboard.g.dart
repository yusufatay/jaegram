// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'leaderboard.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Leaderboard _$LeaderboardFromJson(Map<String, dynamic> json) => Leaderboard(
      id: (json['id'] as num).toInt(),
      userId: (json['user_id'] as num).toInt(),
      username: json['username'] as String,
      totalCoins: (json['total_coins'] as num?)?.toInt() ?? 0,
      tasksCompleted: (json['tasks_completed'] as num?)?.toInt() ?? 0,
      rank: (json['rank'] as num?)?.toInt() ?? 0,
      weeklyCoins: (json['weekly_coins'] as num?)?.toInt() ?? 0,
      monthlyCoins: (json['monthly_coins'] as num?)?.toInt() ?? 0,
      updatedAt: DateTime.parse(json['updated_at'] as String),
      profilePicUrl: json['profile_pic_url'] as String? ?? '',
    );

Map<String, dynamic> _$LeaderboardToJson(Leaderboard instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'username': instance.username,
      'total_coins': instance.totalCoins,
      'tasks_completed': instance.tasksCompleted,
      'rank': instance.rank,
      'weekly_coins': instance.weeklyCoins,
      'monthly_coins': instance.monthlyCoins,
      'updated_at': instance.updatedAt.toIso8601String(),
      'profile_pic_url': instance.profilePicUrl,
    };
