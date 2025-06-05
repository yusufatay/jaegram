// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'badge.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Badge _$BadgeFromJson(Map<String, dynamic> json) => Badge(
      id: (json['id'] as num).toInt(),
      name: json['name'] as String,
      description: json['description'] as String,
      iconUrl: json['icon_url'] as String,
      category: json['category'] as String,
      requirementsJson: json['requirements_json'] as Map<String, dynamic>,
      isActive: json['is_active'] as bool,
      createdAt: DateTime.parse(json['created_at'] as String),
    );

Map<String, dynamic> _$BadgeToJson(Badge instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'icon_url': instance.iconUrl,
      'category': instance.category,
      'requirements_json': instance.requirementsJson,
      'is_active': instance.isActive,
      'created_at': instance.createdAt.toIso8601String(),
    };

UserBadge _$UserBadgeFromJson(Map<String, dynamic> json) => UserBadge(
      id: (json['id'] as num).toInt(),
      userId: (json['user_id'] as num).toInt(),
      badgeId: (json['badge_id'] as num).toInt(),
      earnedAt: DateTime.parse(json['earned_at'] as String),
      badge: json['badge'] == null
          ? null
          : Badge.fromJson(json['badge'] as Map<String, dynamic>),
    );

Map<String, dynamic> _$UserBadgeToJson(UserBadge instance) => <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'badge_id': instance.badgeId,
      'earned_at': instance.earnedAt.toIso8601String(),
      'badge': instance.badge,
    };
