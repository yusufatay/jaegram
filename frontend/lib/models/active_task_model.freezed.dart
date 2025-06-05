// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'active_task_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

ActiveTaskModel _$ActiveTaskModelFromJson(Map<String, dynamic> json) {
  return _ActiveTaskModel.fromJson(json);
}

/// @nodoc
mixin _$ActiveTaskModel {
  int get id => throw _privateConstructorUsedError;
  int get orderId => throw _privateConstructorUsedError;
  String get orderPostUrl => throw _privateConstructorUsedError;
  String get orderType =>
      throw _privateConstructorUsedError; // 'like', 'follow', 'comment'
  String? get commentText =>
      throw _privateConstructorUsedError; // Yalnızca comment görevleri için
  String get status => throw _privateConstructorUsedError;
  DateTime? get assignedAt => throw _privateConstructorUsedError;
  DateTime? get expiresAt => throw _privateConstructorUsedError;

  /// Serializes this ActiveTaskModel to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ActiveTaskModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ActiveTaskModelCopyWith<ActiveTaskModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ActiveTaskModelCopyWith<$Res> {
  factory $ActiveTaskModelCopyWith(
          ActiveTaskModel value, $Res Function(ActiveTaskModel) then) =
      _$ActiveTaskModelCopyWithImpl<$Res, ActiveTaskModel>;
  @useResult
  $Res call(
      {int id,
      int orderId,
      String orderPostUrl,
      String orderType,
      String? commentText,
      String status,
      DateTime? assignedAt,
      DateTime? expiresAt});
}

/// @nodoc
class _$ActiveTaskModelCopyWithImpl<$Res, $Val extends ActiveTaskModel>
    implements $ActiveTaskModelCopyWith<$Res> {
  _$ActiveTaskModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ActiveTaskModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? orderId = null,
    Object? orderPostUrl = null,
    Object? orderType = null,
    Object? commentText = freezed,
    Object? status = null,
    Object? assignedAt = freezed,
    Object? expiresAt = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      orderId: null == orderId
          ? _value.orderId
          : orderId // ignore: cast_nullable_to_non_nullable
              as int,
      orderPostUrl: null == orderPostUrl
          ? _value.orderPostUrl
          : orderPostUrl // ignore: cast_nullable_to_non_nullable
              as String,
      orderType: null == orderType
          ? _value.orderType
          : orderType // ignore: cast_nullable_to_non_nullable
              as String,
      commentText: freezed == commentText
          ? _value.commentText
          : commentText // ignore: cast_nullable_to_non_nullable
              as String?,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      assignedAt: freezed == assignedAt
          ? _value.assignedAt
          : assignedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      expiresAt: freezed == expiresAt
          ? _value.expiresAt
          : expiresAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ActiveTaskModelImplCopyWith<$Res>
    implements $ActiveTaskModelCopyWith<$Res> {
  factory _$$ActiveTaskModelImplCopyWith(_$ActiveTaskModelImpl value,
          $Res Function(_$ActiveTaskModelImpl) then) =
      __$$ActiveTaskModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int id,
      int orderId,
      String orderPostUrl,
      String orderType,
      String? commentText,
      String status,
      DateTime? assignedAt,
      DateTime? expiresAt});
}

/// @nodoc
class __$$ActiveTaskModelImplCopyWithImpl<$Res>
    extends _$ActiveTaskModelCopyWithImpl<$Res, _$ActiveTaskModelImpl>
    implements _$$ActiveTaskModelImplCopyWith<$Res> {
  __$$ActiveTaskModelImplCopyWithImpl(
      _$ActiveTaskModelImpl _value, $Res Function(_$ActiveTaskModelImpl) _then)
      : super(_value, _then);

  /// Create a copy of ActiveTaskModel
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? orderId = null,
    Object? orderPostUrl = null,
    Object? orderType = null,
    Object? commentText = freezed,
    Object? status = null,
    Object? assignedAt = freezed,
    Object? expiresAt = freezed,
  }) {
    return _then(_$ActiveTaskModelImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as int,
      orderId: null == orderId
          ? _value.orderId
          : orderId // ignore: cast_nullable_to_non_nullable
              as int,
      orderPostUrl: null == orderPostUrl
          ? _value.orderPostUrl
          : orderPostUrl // ignore: cast_nullable_to_non_nullable
              as String,
      orderType: null == orderType
          ? _value.orderType
          : orderType // ignore: cast_nullable_to_non_nullable
              as String,
      commentText: freezed == commentText
          ? _value.commentText
          : commentText // ignore: cast_nullable_to_non_nullable
              as String?,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      assignedAt: freezed == assignedAt
          ? _value.assignedAt
          : assignedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      expiresAt: freezed == expiresAt
          ? _value.expiresAt
          : expiresAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ActiveTaskModelImpl implements _ActiveTaskModel {
  const _$ActiveTaskModelImpl(
      {required this.id,
      required this.orderId,
      required this.orderPostUrl,
      required this.orderType,
      this.commentText,
      required this.status,
      this.assignedAt,
      this.expiresAt});

  factory _$ActiveTaskModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$ActiveTaskModelImplFromJson(json);

  @override
  final int id;
  @override
  final int orderId;
  @override
  final String orderPostUrl;
  @override
  final String orderType;
// 'like', 'follow', 'comment'
  @override
  final String? commentText;
// Yalnızca comment görevleri için
  @override
  final String status;
  @override
  final DateTime? assignedAt;
  @override
  final DateTime? expiresAt;

  @override
  String toString() {
    return 'ActiveTaskModel(id: $id, orderId: $orderId, orderPostUrl: $orderPostUrl, orderType: $orderType, commentText: $commentText, status: $status, assignedAt: $assignedAt, expiresAt: $expiresAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ActiveTaskModelImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.orderId, orderId) || other.orderId == orderId) &&
            (identical(other.orderPostUrl, orderPostUrl) ||
                other.orderPostUrl == orderPostUrl) &&
            (identical(other.orderType, orderType) ||
                other.orderType == orderType) &&
            (identical(other.commentText, commentText) ||
                other.commentText == commentText) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.assignedAt, assignedAt) ||
                other.assignedAt == assignedAt) &&
            (identical(other.expiresAt, expiresAt) ||
                other.expiresAt == expiresAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, orderId, orderPostUrl,
      orderType, commentText, status, assignedAt, expiresAt);

  /// Create a copy of ActiveTaskModel
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ActiveTaskModelImplCopyWith<_$ActiveTaskModelImpl> get copyWith =>
      __$$ActiveTaskModelImplCopyWithImpl<_$ActiveTaskModelImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ActiveTaskModelImplToJson(
      this,
    );
  }
}

abstract class _ActiveTaskModel implements ActiveTaskModel {
  const factory _ActiveTaskModel(
      {required final int id,
      required final int orderId,
      required final String orderPostUrl,
      required final String orderType,
      final String? commentText,
      required final String status,
      final DateTime? assignedAt,
      final DateTime? expiresAt}) = _$ActiveTaskModelImpl;

  factory _ActiveTaskModel.fromJson(Map<String, dynamic> json) =
      _$ActiveTaskModelImpl.fromJson;

  @override
  int get id;
  @override
  int get orderId;
  @override
  String get orderPostUrl;
  @override
  String get orderType; // 'like', 'follow', 'comment'
  @override
  String? get commentText; // Yalnızca comment görevleri için
  @override
  String get status;
  @override
  DateTime? get assignedAt;
  @override
  DateTime? get expiresAt;

  /// Create a copy of ActiveTaskModel
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ActiveTaskModelImplCopyWith<_$ActiveTaskModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
