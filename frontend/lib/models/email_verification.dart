import 'package:json_annotation/json_annotation.dart';

part 'email_verification.g.dart';

@JsonSerializable()
class EmailVerificationRequest {
  final String email;

  const EmailVerificationRequest({
    required this.email,
  });

  factory EmailVerificationRequest.fromJson(Map<String, dynamic> json) =>
      _$EmailVerificationRequestFromJson(json);

  Map<String, dynamic> toJson() => _$EmailVerificationRequestToJson(this);
}

@JsonSerializable()
class EmailVerificationResponse {
  final bool success;
  final String message;
  @JsonKey(name: 'expires_in_minutes')
  final int? expiresInMinutes;
  @JsonKey(name: 'bonus_coins')
  final int? bonusCoins;
  @JsonKey(name: 'new_balance')
  final int? newBalance;

  const EmailVerificationResponse({
    required this.success,
    required this.message,
    this.expiresInMinutes,
    this.bonusCoins,
    this.newBalance,
  });

  factory EmailVerificationResponse.fromJson(Map<String, dynamic> json) =>
      _$EmailVerificationResponseFromJson(json);

  Map<String, dynamic> toJson() => _$EmailVerificationResponseToJson(this);
}
