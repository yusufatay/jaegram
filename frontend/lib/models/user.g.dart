// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

User _$UserFromJson(Map<String, dynamic> json) => User(
      id: json['id'] as String,
      username: json['username'] as String,
      fullName: json['full_name'] as String?,
      email: json['email'] as String?,
      profilePicUrl: json['profile_pic_url'] as String?,
      emailVerified: json['email_verified'] as bool? ?? false,
      twoFactorEnabled: json['two_factor_enabled'] as bool? ?? false,
      diamondBalance: (json['coin_balance'] as num?)?.toInt(),
      completedTasks: (json['completed_tasks'] as num?)?.toInt(),
      activeTasks: (json['active_tasks'] as num?)?.toInt(),
      token: json['token'] as String?,
      isAdminPlatform: json['is_admin_platform'] as bool? ?? false,
      instagramStats: json['instagram_stats'] == null
          ? null
          : InstagramProfileStats.fromJson(
              json['instagram_stats'] as Map<String, dynamic>),
      lastDailyReward: json['last_daily_reward'] == null
          ? null
          : DateTime.parse(json['last_daily_reward'] as String),
      dailyRewardStreak: (json['daily_reward_streak'] as num?)?.toInt() ?? 0,
      instagramConnected: json['instagram_connected'] as bool? ?? false,
    );

Map<String, dynamic> _$UserToJson(User instance) => <String, dynamic>{
      'id': instance.id,
      'username': instance.username,
      'full_name': instance.fullName,
      'email': instance.email,
      'profile_pic_url': instance.profilePicUrl,
      'email_verified': instance.emailVerified,
      'two_factor_enabled': instance.twoFactorEnabled,
      'coin_balance': instance.diamondBalance,
      'completed_tasks': instance.completedTasks,
      'active_tasks': instance.activeTasks,
      'token': instance.token,
      'is_admin_platform': instance.isAdminPlatform,
      'instagram_stats': instance.instagramStats,
      'last_daily_reward': instance.lastDailyReward?.toIso8601String(),
      'daily_reward_streak': instance.dailyRewardStreak,
      'instagram_connected': instance.instagramConnected,
    };

InstagramProfileStats _$InstagramProfileStatsFromJson(
        Map<String, dynamic> json) =>
    InstagramProfileStats(
      instagramUserId: json['instagram_user_id'] as String,
      username: json['username'] as String,
      fullName: json['full_name'] as String?,
      profilePicUrl: json['profile_pic_url'] as String?,
      isPrivate: json['is_private'] as bool?,
      isVerified: json['is_verified'] as bool?,
      biography: json['biography'] as String?,
      externalUrl: json['external_url'] as String?,
      category: json['category'] as String?,
      mediaCount: (json['media_count'] as num?)?.toInt(),
      isConnected: json['is_connected'] as bool?,
      connectionStatus: json['connection_status'] as String?,
      lastSync: json['last_sync'] as String?,
      connectedAt: json['connected_at'] as String?,
    );

Map<String, dynamic> _$InstagramProfileStatsToJson(
        InstagramProfileStats instance) =>
    <String, dynamic>{
      'instagram_user_id': instance.instagramUserId,
      'username': instance.username,
      'full_name': instance.fullName,
      'profile_pic_url': instance.profilePicUrl,
      'is_private': instance.isPrivate,
      'is_verified': instance.isVerified,
      'biography': instance.biography,
      'external_url': instance.externalUrl,
      'category': instance.category,
      'media_count': instance.mediaCount,
      'is_connected': instance.isConnected,
      'connection_status': instance.connectionStatus,
      'last_sync': instance.lastSync,
      'connected_at': instance.connectedAt,
    };
