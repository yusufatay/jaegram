import 'package:freezed_annotation/freezed_annotation.dart';

part 'task.freezed.dart';
part 'task.g.dart';

/// Görev modelini temsil eder.
/// Backend API ile birebir uyumludur.
@freezed
class Task with _$Task {
  const factory Task({
    required int id,
    required String type, // 'follow' veya 'like'
    required String target, // username veya post_id
    required int assignedTo,
    @Default('pending') String status, // 'pending' veya 'completed'
    DateTime? createdAt,
    DateTime? updatedAt,
    @Default(false) bool isDeleted,
  }) = _Task;

  factory Task.fromJson(Map<String, dynamic> json) => _$TaskFromJson(json);
}
