// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'email_verification.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

EmailVerificationRequest _$EmailVerificationRequestFromJson(
        Map<String, dynamic> json) =>
    EmailVerificationRequest(
      email: json['email'] as String,
    );

Map<String, dynamic> _$EmailVerificationRequestToJson(
        EmailVerificationRequest instance) =>
    <String, dynamic>{
      'email': instance.email,
    };

EmailVerificationResponse _$EmailVerificationResponseFromJson(
        Map<String, dynamic> json) =>
    EmailVerificationResponse(
      success: json['success'] as bool,
      message: json['message'] as String,
      expiresInMinutes: (json['expires_in_minutes'] as num?)?.toInt(),
      bonusCoins: (json['bonus_coins'] as num?)?.toInt(),
      newBalance: (json['new_balance'] as num?)?.toInt(),
    );

Map<String, dynamic> _$EmailVerificationResponseToJson(
        EmailVerificationResponse instance) =>
    <String, dynamic>{
      'success': instance.success,
      'message': instance.message,
      'expires_in_minutes': instance.expiresInMinutes,
      'bonus_coins': instance.bonusCoins,
      'new_balance': instance.newBalance,
    };
