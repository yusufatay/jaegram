// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'instagram_post.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

InstagramPost _$InstagramPostFromJson(Map<String, dynamic> json) =>
    InstagramPost(
      id: json['id'] as String,
      url: json['url'] as String,
      imageUrl: json['image_url'] as String?,
      videoUrl: json['video_url'] as String?,
      caption: json['caption'] as String?,
      likeCount: (json['like_count'] as num?)?.toInt(),
      commentCount: (json['comment_count'] as num?)?.toInt(),
      createdAt: json['created_at'] == null
          ? null
          : DateTime.parse(json['created_at'] as String),
    );

Map<String, dynamic> _$InstagramPostToJson(InstagramPost instance) =>
    <String, dynamic>{
      'id': instance.id,
      'url': instance.url,
      'image_url': instance.imageUrl,
      'video_url': instance.videoUrl,
      'caption': instance.caption,
      'like_count': instance.likeCount,
      'comment_count': instance.commentCount,
      'created_at': instance.createdAt?.toIso8601String(),
    };
