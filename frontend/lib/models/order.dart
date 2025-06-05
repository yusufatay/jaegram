import 'package:freezed_annotation/freezed_annotation.dart';

part 'order.freezed.dart';
part 'order.g.dart';

/// Sipariş modelini temsil eder.
/// Backend API ile birebir uyumludur.
@freezed
class Order with _$Order {
  const factory Order({
    required int id,
    required String type, // 'followers' veya 'likes'
    required String target, // username veya post_id
    required int amount,
    required int paidWithCoins,
    @Default('pending') String status,
    DateTime? createdAt,
    DateTime? updatedAt,
    @Default(false) bool isDeleted,
  }) = _Order;

  factory Order.fromJson(Map<String, dynamic> json) => _$OrderFromJson(json);
}
