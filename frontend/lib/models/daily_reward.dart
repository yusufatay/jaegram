import 'package:json_annotation/json_annotation.dart';

part 'daily_reward.g.dart';

@JsonSerializable()
class DailyRewardStatus {
  @JsonKey(name: 'can_claim')
  final bool canClaim;
  @JsonKey(name: 'current_streak')
  final int currentStreak;
  @JsonKey(name: 'next_reward')
  final int nextReward;
  @JsonKey(name: 'last_claim')
  final DateTime? lastClaim;

  const DailyRewardStatus({
    required this.canClaim,
    required this.currentStreak,
    required this.nextReward,
    this.lastClaim,
  });

  factory DailyRewardStatus.fromJson(Map<String, dynamic> json) =>
      _$DailyRewardStatusFromJson(json);

  Map<String, dynamic> toJson() => _$DailyRewardStatusToJson(this);
}

@JsonSerializable()
class DailyRewardResponse {
  final bool success;
  @JsonKey(name: 'coins_awarded')
  final int diamondsAwarded;
  @JsonKey(name: 'streak_day')
  final int streakDay;
  @JsonKey(name: 'new_balance')
  final int newBalance;
  final String message;

  const DailyRewardResponse({
    required this.success,
    required this.diamondsAwarded,
    required this.streakDay,
    required this.newBalance,
    required this.message,
  });

  factory DailyRewardResponse.fromJson(Map<String, dynamic> json) =>
      _$DailyRewardResponseFromJson(json);

  Map<String, dynamic> toJson() => _$DailyRewardResponseToJson(this);
}
