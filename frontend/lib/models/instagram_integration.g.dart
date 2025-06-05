// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'instagram_integration.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

InstagramProfile _$InstagramProfileFromJson(Map<String, dynamic> json) =>
    InstagramProfile(
      username: json['username'] as String,
      fullName: json['full_name'] as String,
      biography: json['biography'] as String,
      profilePicUrl: json['profile_pic_url'] as String,
      postsCount: (json['posts_count'] as num).toInt(),
      isVerified: json['is_verified'] as bool,
      isPrivate: json['is_private'] as bool,
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );

Map<String, dynamic> _$InstagramProfileToJson(InstagramProfile instance) =>
    <String, dynamic>{
      'username': instance.username,
      'full_name': instance.fullName,
      'biography': instance.biography,
      'profile_pic_url': instance.profilePicUrl,
      'posts_count': instance.postsCount,
      'is_verified': instance.isVerified,
      'is_private': instance.isPrivate,
      'updated_at': instance.updatedAt.toIso8601String(),
    };

InstagramPost _$InstagramPostFromJson(Map<String, dynamic> json) =>
    InstagramPost(
      id: json['id'] as String,
      mediaType: json['media_type'] as String,
      mediaUrl: json['media_url'] as String,
      caption: json['caption'] as String,
      likeCount: (json['like_count'] as num).toInt(),
      commentCount: (json['comment_count'] as num).toInt(),
      createdAt: DateTime.parse(json['created_at'] as String),
    );

Map<String, dynamic> _$InstagramPostToJson(InstagramPost instance) =>
    <String, dynamic>{
      'id': instance.id,
      'media_type': instance.mediaType,
      'media_url': instance.mediaUrl,
      'caption': instance.caption,
      'like_count': instance.likeCount,
      'comment_count': instance.commentCount,
      'created_at': instance.createdAt.toIso8601String(),
    };

InstagramCredential _$InstagramCredentialFromJson(Map<String, dynamic> json) =>
    InstagramCredential(
      id: (json['id'] as num).toInt(),
      userId: (json['user_id'] as num).toInt(),
      username: json['username'] as String,
      isVerified: json['is_verified'] as bool,
      verificationDate: json['verification_date'] == null
          ? null
          : DateTime.parse(json['verification_date'] as String),
      lastSync: json['last_sync'] == null
          ? null
          : DateTime.parse(json['last_sync'] as String),
      syncStatus: json['sync_status'] as String,
      errorMessage: json['error_message'] as String?,
    );

Map<String, dynamic> _$InstagramCredentialToJson(
        InstagramCredential instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'username': instance.username,
      'is_verified': instance.isVerified,
      'verification_date': instance.verificationDate?.toIso8601String(),
      'last_sync': instance.lastSync?.toIso8601String(),
      'sync_status': instance.syncStatus,
      'error_message': instance.errorMessage,
    };

InstagramChallenge _$InstagramChallengeFromJson(Map<String, dynamic> json) =>
    InstagramChallenge(
      id: json['id'] as String,
      challengeType: json['challenge_type'] as String,
      message: json['message'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
      expiresAt: DateTime.parse(json['expires_at'] as String),
      isResolved: json['is_resolved'] as bool,
      attemptsLeft: (json['attempts_left'] as num).toInt(),
    );

Map<String, dynamic> _$InstagramChallengeToJson(InstagramChallenge instance) =>
    <String, dynamic>{
      'id': instance.id,
      'challenge_type': instance.challengeType,
      'message': instance.message,
      'created_at': instance.createdAt.toIso8601String(),
      'expires_at': instance.expiresAt.toIso8601String(),
      'is_resolved': instance.isResolved,
      'attempts_left': instance.attemptsLeft,
    };

InstagramConnectionStatus _$InstagramConnectionStatusFromJson(
        Map<String, dynamic> json) =>
    InstagramConnectionStatus(
      isConnected: json['is_connected'] as bool,
      connectionStatus: json['connection_status'] as String,
      lastVerified: json['last_verified'] == null
          ? null
          : DateTime.parse(json['last_verified'] as String),
      requiresChallenge: json['requires_challenge'] as bool,
      challengeInfo: json['challenge_info'] == null
          ? null
          : InstagramChallenge.fromJson(
              json['challenge_info'] as Map<String, dynamic>),
      errorMessage: json['error_message'] as String?,
    );

Map<String, dynamic> _$InstagramConnectionStatusToJson(
        InstagramConnectionStatus instance) =>
    <String, dynamic>{
      'is_connected': instance.isConnected,
      'connection_status': instance.connectionStatus,
      'last_verified': instance.lastVerified?.toIso8601String(),
      'requires_challenge': instance.requiresChallenge,
      'challenge_info': instance.challengeInfo,
      'error_message': instance.errorMessage,
    };

InstagramTaskValidation _$InstagramTaskValidationFromJson(
        Map<String, dynamic> json) =>
    InstagramTaskValidation(
      taskId: (json['task_id'] as num).toInt(),
      isValid: json['is_valid'] as bool,
      validationStatus: json['validation_status'] as String,
      coinsEarned: (json['coins_earned'] as num).toInt(),
      validatedAt: json['validated_at'] == null
          ? null
          : DateTime.parse(json['validated_at'] as String),
      errorReason: json['error_reason'] as String?,
    );

Map<String, dynamic> _$InstagramTaskValidationToJson(
        InstagramTaskValidation instance) =>
    <String, dynamic>{
      'task_id': instance.taskId,
      'is_valid': instance.isValid,
      'validation_status': instance.validationStatus,
      'coins_earned': instance.coinsEarned,
      'validated_at': instance.validatedAt?.toIso8601String(),
      'error_reason': instance.errorReason,
    };
