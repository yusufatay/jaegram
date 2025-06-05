import 'package:json_annotation/json_annotation.dart';

part 'referral.g.dart';

@JsonSerializable()
class Referral {
  final int id;
  @JsonKey(name: 'referrer_id')
  final int referrerId;
  @JsonKey(name: 'referred_id')
  final int referredId;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @JsonKey(name: 'coins_earned')
  final int coinsEarned;
  @JsonKey(name: 'is_active')
  final bool isActive;

  Referral({
    required this.id,
    required this.referrerId,
    required this.referredId,
    required this.createdAt,
    required this.coinsEarned,
    required this.isActive,
  });

  factory Referral.fromJson(Map<String, dynamic> json) => _$ReferralFromJson(json);
  Map<String, dynamic> toJson() => _$ReferralToJson(this);
}
