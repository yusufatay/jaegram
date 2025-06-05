import 'package:json_annotation/json_annotation.dart';

part 'instagram_integration.g.dart';

@JsonSerializable()
class InstagramProfile {
  final String username;
  @JsonKey(name: 'full_name')
  final String fullName;
  final String biography;
  @JsonKey(name: 'profile_pic_url')
  final String profilePicUrl;
  @JsonKey(name: 'posts_count')
  final int postsCount;
  @JsonKey(name: 'is_verified')
  final bool isVerified;
  @JsonKey(name: 'is_private')
  final bool isPrivate;
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  InstagramProfile({
    required this.username,
    required this.fullName,
    required this.biography,
    required this.profilePicUrl,
    required this.postsCount,
    required this.isVerified,
    required this.isPrivate,
    required this.updatedAt,
  });

  factory InstagramProfile.fromJson(Map<String, dynamic> json) => _$InstagramProfileFromJson(json);
  Map<String, dynamic> toJson() => _$InstagramProfileToJson(this);
}

@JsonSerializable()
class InstagramPost {
  final String id;
  @JsonKey(name: 'media_type')
  final String mediaType;
  @JsonKey(name: 'media_url')
  final String mediaUrl;
  final String caption;
  @JsonKey(name: 'like_count')
  final int likeCount;
  @JsonKey(name: 'comment_count')
  final int commentCount;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  InstagramPost({
    required this.id,
    required this.mediaType,
    required this.mediaUrl,
    required this.caption,
    required this.likeCount,
    required this.commentCount,
    required this.createdAt,
  });

  factory InstagramPost.fromJson(Map<String, dynamic> json) => _$InstagramPostFromJson(json);
  Map<String, dynamic> toJson() => _$InstagramPostToJson(this);
}

@JsonSerializable()
class InstagramCredential {
  final int id;
  @JsonKey(name: 'user_id')
  final int userId;
  final String username;
  @JsonKey(name: 'is_verified')
  final bool isVerified;
  @JsonKey(name: 'verification_date')
  final DateTime? verificationDate;
  @JsonKey(name: 'last_sync')
  final DateTime? lastSync;
  @JsonKey(name: 'sync_status')
  final String syncStatus;
  @JsonKey(name: 'error_message')
  final String? errorMessage;

  InstagramCredential({
    required this.id,
    required this.userId,
    required this.username,
    required this.isVerified,
    this.verificationDate,
    this.lastSync,
    required this.syncStatus,
    this.errorMessage,
  });

  factory InstagramCredential.fromJson(Map<String, dynamic> json) => _$InstagramCredentialFromJson(json);
  Map<String, dynamic> toJson() => _$InstagramCredentialToJson(this);
}

@JsonSerializable()
class InstagramChallenge {
  final String id;
  @JsonKey(name: 'challenge_type')
  final String challengeType;
  final String message;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @JsonKey(name: 'expires_at')
  final DateTime expiresAt;
  @JsonKey(name: 'is_resolved')
  final bool isResolved;
  @JsonKey(name: 'attempts_left')
  final int attemptsLeft;

  InstagramChallenge({
    required this.id,
    required this.challengeType,
    required this.message,
    required this.createdAt,
    required this.expiresAt,
    required this.isResolved,
    required this.attemptsLeft,
  });

  factory InstagramChallenge.fromJson(Map<String, dynamic> json) => _$InstagramChallengeFromJson(json);
  Map<String, dynamic> toJson() => _$InstagramChallengeToJson(this);
}

@JsonSerializable()
class InstagramConnectionStatus {
  @JsonKey(name: 'is_connected')
  final bool isConnected;
  @JsonKey(name: 'connection_status')
  final String connectionStatus;
  @JsonKey(name: 'last_verified')
  final DateTime? lastVerified;
  @JsonKey(name: 'requires_challenge')
  final bool requiresChallenge;
  @JsonKey(name: 'challenge_info')
  final InstagramChallenge? challengeInfo;
  @JsonKey(name: 'error_message')
  final String? errorMessage;

  InstagramConnectionStatus({
    required this.isConnected,
    required this.connectionStatus,
    this.lastVerified,
    required this.requiresChallenge,
    this.challengeInfo,
    this.errorMessage,
  });

  factory InstagramConnectionStatus.fromJson(Map<String, dynamic> json) => _$InstagramConnectionStatusFromJson(json);
  Map<String, dynamic> toJson() => _$InstagramConnectionStatusToJson(this);
}

@JsonSerializable()
class InstagramTaskValidation {
  @JsonKey(name: 'task_id')
  final int taskId;
  @JsonKey(name: 'is_valid')
  final bool isValid;
  @JsonKey(name: 'validation_status')
  final String validationStatus;
  @JsonKey(name: 'coins_earned')
  final int coinsEarned;
  @JsonKey(name: 'validated_at')
  final DateTime? validatedAt;
  @JsonKey(name: 'error_reason')
  final String? errorReason;

  InstagramTaskValidation({
    required this.taskId,
    required this.isValid,
    required this.validationStatus,
    required this.coinsEarned,
    this.validatedAt,
    this.errorReason,
  });

  factory InstagramTaskValidation.fromJson(Map<String, dynamic> json) => _$InstagramTaskValidationFromJson(json);
  Map<String, dynamic> toJson() => _$InstagramTaskValidationToJson(this);
}
