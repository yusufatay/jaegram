// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'referral.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Referral _$ReferralFromJson(Map<String, dynamic> json) => Referral(
      id: (json['id'] as num).toInt(),
      referrerId: (json['referrer_id'] as num).toInt(),
      referredId: (json['referred_id'] as num).toInt(),
      createdAt: DateTime.parse(json['created_at'] as String),
      coinsEarned: (json['coins_earned'] as num).toInt(),
      isActive: json['is_active'] as bool,
    );

Map<String, dynamic> _$ReferralToJson(Referral instance) => <String, dynamic>{
      'id': instance.id,
      'referrer_id': instance.referrerId,
      'referred_id': instance.referredId,
      'created_at': instance.createdAt.toIso8601String(),
      'coins_earned': instance.coinsEarned,
      'is_active': instance.isActive,
    };
