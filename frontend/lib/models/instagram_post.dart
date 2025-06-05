import 'package:json_annotation/json_annotation.dart';

part 'instagram_post.g.dart';

@JsonSerializable()
class InstagramPost {
  final String id;
  final String url;
  @JsonKey(name: 'image_url')
  final String? imageUrl;
  @JsonKey(name: 'video_url')
  final String? videoUrl;
  final String? caption;
  @JsonKey(name: 'like_count')
  final int? likeCount;
  @JsonKey(name: 'comment_count')
  final int? commentCount;
  @JsonKey(name: 'created_at')
  final DateTime? createdAt;

  const InstagramPost({
    required this.id,
    required this.url,
    this.imageUrl,
    this.videoUrl,
    this.caption,
    this.likeCount,
    this.commentCount,
    this.createdAt,
  });

  factory InstagramPost.fromJson(Map<String, dynamic> json) => _$InstagramPostFromJson(json);
  Map<String, dynamic> toJson() => _$InstagramPostToJson(this);
}
