import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@JsonSerializable()
class User {
  final String id;
  final String username;
  @JsonKey(name: 'full_name')
  final String? fullName;
  final String? email;
  @JsonKey(name: 'profile_pic_url')
  final String? profilePicUrl;
  @JsonKey(name: 'email_verified')
  final bool emailVerified;
  @JsonKey(name: 'two_factor_enabled')
  final bool twoFactorEnabled;
  @JsonKey(name: 'coin_balance')
  final int? diamondBalance;
  @JsonKey(name: 'completed_tasks')
  final int? completedTasks;
  @JsonKey(name: 'active_tasks')
  final int? activeTasks;
  final String? token;
  @JsonKey(name: 'is_admin_platform')
  final bool isAdminPlatform;
  @JsonKey(name: 'instagram_stats')
  final InstagramProfileStats? instagramStats;
  @JsonKey(name: 'last_daily_reward')
  final DateTime? lastDailyReward;
  @JsonKey(name: 'daily_reward_streak')
  final int dailyRewardStreak;
  @JsonKey(name: 'instagram_connected')
  final bool instagramConnected;

  const User({
    required this.id,
    required this.username,
    this.fullName,
    this.email,
    this.profilePicUrl,
    this.emailVerified = false,
    this.twoFactorEnabled = false,
    this.diamondBalance,
    this.completedTasks,
    this.activeTasks,
    this.token,
    this.isAdminPlatform = false,
    this.instagramStats,
    this.lastDailyReward,
    this.dailyRewardStreak = 0,
    this.instagramConnected = false,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    // Handle both coin_balance and diamondBalance for compatibility
    int? balance;
    if (json['diamondBalance'] != null) {
      balance = (json['diamondBalance'] as num?)?.toInt();
    } else if (json['coin_balance'] != null) {
      balance = (json['coin_balance'] as num?)?.toInt();
    }
    
    // Create a modified json with the balance
    final modifiedJson = Map<String, dynamic>.from(json);
    if (balance != null) {
      modifiedJson['coin_balance'] = balance;
    }
    
    return _$UserFromJson(modifiedJson);
  }
  Map<String, dynamic> toJson() => _$UserToJson(this);

  User copyWith({
    String? id,
    String? username,
    String? fullName,
    String? email,
    String? profilePicUrl,
    bool? emailVerified,
    bool? twoFactorEnabled,
    int? diamondBalance,
    int? completedTasks,
    int? activeTasks,
    String? token,
    bool? isAdminPlatform,
    InstagramProfileStats? instagramStats,
    DateTime? lastDailyReward,
    int? dailyRewardStreak,
    bool? instagramConnected,
  }) {
    return User(
      id: id ?? this.id,
      username: username ?? this.username,
      fullName: fullName ?? this.fullName,
      email: email ?? this.email,
      profilePicUrl: profilePicUrl ?? this.profilePicUrl,
      emailVerified: emailVerified ?? this.emailVerified,
      twoFactorEnabled: twoFactorEnabled ?? this.twoFactorEnabled,
      diamondBalance: diamondBalance ?? this.diamondBalance,
      completedTasks: completedTasks ?? this.completedTasks,
      activeTasks: activeTasks ?? this.activeTasks,
      token: token ?? this.token,
      isAdminPlatform: isAdminPlatform ?? this.isAdminPlatform,
      instagramStats: instagramStats ?? this.instagramStats,
      lastDailyReward: lastDailyReward ?? this.lastDailyReward,
      dailyRewardStreak: dailyRewardStreak ?? this.dailyRewardStreak,
      instagramConnected: instagramConnected ?? this.instagramConnected,
    );
  }
}

@JsonSerializable()
class InstagramProfileStats {
  @JsonKey(name: 'instagram_user_id')
  final String instagramUserId;
  final String username;
  @JsonKey(name: 'full_name')
  final String? fullName;
  @JsonKey(name: 'profile_pic_url')
  final String? profilePicUrl;
  @JsonKey(name: 'is_private')
  final bool? isPrivate;
  @JsonKey(name: 'is_verified')
  final bool? isVerified;
  @JsonKey(name: 'biography')
  final String? biography;
  @JsonKey(name: 'external_url')
  final String? externalUrl;
  @JsonKey(name: 'category')
  final String? category;
  @JsonKey(name: 'media_count')
  final int? mediaCount;
  @JsonKey(name: 'is_connected')
  final bool? isConnected;
  @JsonKey(name: 'connection_status')
  final String? connectionStatus;
  @JsonKey(name: 'last_sync')
  final String? lastSync;
  @JsonKey(name: 'connected_at')
  final String? connectedAt;

  const InstagramProfileStats({
    required this.instagramUserId,
    required this.username,
    this.fullName,
    this.profilePicUrl,
    this.isPrivate,
    this.isVerified,
    this.biography,
    this.externalUrl,
    this.category,
    this.mediaCount,
    this.isConnected,
    this.connectionStatus,
    this.lastSync,
    this.connectedAt,
  });

  factory InstagramProfileStats.fromJson(Map<String, dynamic> json) =>
      _$InstagramProfileStatsFromJson(json);

  Map<String, dynamic> toJson() => _$InstagramProfileStatsToJson(this);
}
