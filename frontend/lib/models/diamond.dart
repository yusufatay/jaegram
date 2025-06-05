import 'package:freezed_annotation/freezed_annotation.dart';

part 'diamond.freezed.dart';
part 'diamond.g.dart';

/// Diamond (puan) modelini temsil eder.
/// Backend API ile birebir uyumludur.
@freezed
class Diamond with _$Diamond {
  const factory Diamond({
    required int diamond,
  }) = _Diamond;

  factory Diamond.fromJson(Map<String, dynamic> json) => _$DiamondFromJson(json);
}
