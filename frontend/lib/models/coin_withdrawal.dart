import 'package:json_annotation/json_annotation.dart';

part 'coin_withdrawal.g.dart';

@JsonSerializable()
class CoinWithdrawalRequest {
  final int id;
  @JsonKey(name: 'user_id')
  final int userId;
  final int amount;
  @JsonKey(name: 'withdrawal_method')
  final String withdrawalMethod;
  @JsonKey(name: 'bank_account_info')
  final Map<String, dynamic>? bankAccountInfo;
  final String status;
  @JsonKey(name: 'security_check_passed')
  final bool securityCheckPassed;
  @JsonKey(name: 'admin_notes')
  final String? adminNotes;
  @JsonKey(name: 'processed_at')
  final DateTime? processedAt;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  CoinWithdrawalRequest({
    required this.id,
    required this.userId,
    required this.amount,
    required this.withdrawalMethod,
    this.bankAccountInfo,
    required this.status,
    required this.securityCheckPassed,
    this.adminNotes,
    this.processedAt,
    required this.createdAt,
    required this.updatedAt,
  });

  factory CoinWithdrawalRequest.fromJson(Map<String, dynamic> json) => _$CoinWithdrawalRequestFromJson(json);
  Map<String, dynamic> toJson() => _$CoinWithdrawalRequestToJson(this);
}
