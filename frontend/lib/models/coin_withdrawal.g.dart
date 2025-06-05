// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'coin_withdrawal.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

CoinWithdrawalRequest _$CoinWithdrawalRequestFromJson(
        Map<String, dynamic> json) =>
    CoinWithdrawalRequest(
      id: (json['id'] as num).toInt(),
      userId: (json['user_id'] as num).toInt(),
      amount: (json['amount'] as num).toInt(),
      withdrawalMethod: json['withdrawal_method'] as String,
      bankAccountInfo: json['bank_account_info'] as Map<String, dynamic>?,
      status: json['status'] as String,
      securityCheckPassed: json['security_check_passed'] as bool,
      adminNotes: json['admin_notes'] as String?,
      processedAt: json['processed_at'] == null
          ? null
          : DateTime.parse(json['processed_at'] as String),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );

Map<String, dynamic> _$CoinWithdrawalRequestToJson(
        CoinWithdrawalRequest instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'amount': instance.amount,
      'withdrawal_method': instance.withdrawalMethod,
      'bank_account_info': instance.bankAccountInfo,
      'status': instance.status,
      'security_check_passed': instance.securityCheckPassed,
      'admin_notes': instance.adminNotes,
      'processed_at': instance.processedAt?.toIso8601String(),
      'created_at': instance.createdAt.toIso8601String(),
      'updated_at': instance.updatedAt.toIso8601String(),
    };
