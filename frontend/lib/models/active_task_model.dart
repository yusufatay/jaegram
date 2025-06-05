import 'package:freezed_annotation/freezed_annotation.dart';

part 'active_task_model.freezed.dart';
part 'active_task_model.g.dart';

@freezed
class ActiveTaskModel with _$ActiveTaskModel {
  const factory ActiveTaskModel({
    required int id,
    required int orderId,
    required String orderPostUrl,
    required String orderType, // 'like', 'follow', 'comment'
    String? commentText, // Yalnızca comment görevleri için
    required String status,
    DateTime? assignedAt,
    DateTime? expiresAt,
  }) = _ActiveTaskModel;

  factory ActiveTaskModel.fromJson(Map<String, dynamic> json) =>
      _$ActiveTaskModelFromJson(json);
} 