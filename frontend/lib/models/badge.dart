import 'package:json_annotation/json_annotation.dart';

part 'badge.g.dart';

@JsonSerializable()
class Badge {
  final int id;
  final String name;
  final String description;
  @JsonKey(name: 'icon_url')
  final String iconUrl;
  final String category;
  @JsonKey(name: 'requirements_json')
  final Map<String, dynamic> requirementsJson;
  @JsonKey(name: 'is_active')
  final bool isActive;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  Badge({
    required this.id,
    required this.name,
    required this.description,
    required this.iconUrl,
    required this.category,
    required this.requirementsJson,
    required this.isActive,
    required this.createdAt,
  });

  factory Badge.fromJson(Map<String, dynamic> json) => _$BadgeFromJson(json);
  Map<String, dynamic> toJson() => _$BadgeToJson(this);
}

@JsonSerializable()
class UserBadge {
  final int id;
  @JsonKey(name: 'user_id')
  final int userId;
  @JsonKey(name: 'badge_id')
  final int badgeId;
  @JsonKey(name: 'earned_at')
  final DateTime earnedAt;
  final Badge? badge;

  UserBadge({
    required this.id,
    required this.userId,
    required this.badgeId,
    required this.earnedAt,
    this.badge,
  });

  factory UserBadge.fromJson(Map<String, dynamic> json) => _$UserBadgeFromJson(json);
  Map<String, dynamic> toJson() => _$UserBadgeToJson(this);
}
