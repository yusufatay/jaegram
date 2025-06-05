import 'package:json_annotation/json_annotation.dart';

part 'leaderboard.g.dart';

@JsonSerializable()
class Leaderboard {
  final int id;
  @JsonKey(name: 'user_id')
  final int userId;
  final String username;
  @JsonKey(name: 'total_coins', defaultValue: 0)
  final int totalCoins;
  @JsonKey(name: 'tasks_completed', defaultValue: 0)
  final int tasksCompleted;
  @JsonKey(defaultValue: 0)
  final int rank;
  @JsonKey(name: 'weekly_coins', defaultValue: 0)
  final int weeklyCoins;
  @JsonKey(name: 'monthly_coins', defaultValue: 0)
  final int monthlyCoins;
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;
  @JsonKey(name: 'profile_pic_url', defaultValue: '')
  final String profilePicUrl;

  Leaderboard({
    required this.id,
    required this.userId,
    required this.username,
    required this.totalCoins,
    required this.tasksCompleted,
    required this.rank,
    required this.weeklyCoins,
    required this.monthlyCoins,
    required this.updatedAt,
    required this.profilePicUrl,
  });

  factory Leaderboard.fromJson(Map<String, dynamic> json) => _$LeaderboardFromJson(json);
  Map<String, dynamic> toJson() => _$LeaderboardToJson(this);
}
