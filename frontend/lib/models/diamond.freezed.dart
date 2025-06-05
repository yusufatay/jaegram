// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'diamond.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

Diamond _$DiamondFromJson(Map<String, dynamic> json) {
  return _Diamond.fromJson(json);
}

/// @nodoc
mixin _$Diamond {
  int get diamond => throw _privateConstructorUsedError;

  /// Serializes this Diamond to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of Diamond
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $DiamondCopyWith<Diamond> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DiamondCopyWith<$Res> {
  factory $DiamondCopyWith(Diamond value, $Res Function(Diamond) then) =
      _$DiamondCopyWithImpl<$Res, Diamond>;
  @useResult
  $Res call({int diamond});
}

/// @nodoc
class _$DiamondCopyWithImpl<$Res, $Val extends Diamond>
    implements $DiamondCopyWith<$Res> {
  _$DiamondCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of Diamond
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? diamond = null,
  }) {
    return _then(_value.copyWith(
      diamond: null == diamond
          ? _value.diamond
          : diamond // ignore: cast_nullable_to_non_nullable
              as int,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DiamondImplCopyWith<$Res> implements $DiamondCopyWith<$Res> {
  factory _$$DiamondImplCopyWith(
          _$DiamondImpl value, $Res Function(_$DiamondImpl) then) =
      __$$DiamondImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({int diamond});
}

/// @nodoc
class __$$DiamondImplCopyWithImpl<$Res>
    extends _$DiamondCopyWithImpl<$Res, _$DiamondImpl>
    implements _$$DiamondImplCopyWith<$Res> {
  __$$DiamondImplCopyWithImpl(
      _$DiamondImpl _value, $Res Function(_$DiamondImpl) _then)
      : super(_value, _then);

  /// Create a copy of Diamond
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? diamond = null,
  }) {
    return _then(_$DiamondImpl(
      diamond: null == diamond
          ? _value.diamond
          : diamond // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DiamondImpl implements _Diamond {
  const _$DiamondImpl({required this.diamond});

  factory _$DiamondImpl.fromJson(Map<String, dynamic> json) =>
      _$$DiamondImplFromJson(json);

  @override
  final int diamond;

  @override
  String toString() {
    return 'Diamond(diamond: $diamond)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DiamondImpl &&
            (identical(other.diamond, diamond) || other.diamond == diamond));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, diamond);

  /// Create a copy of Diamond
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$DiamondImplCopyWith<_$DiamondImpl> get copyWith =>
      __$$DiamondImplCopyWithImpl<_$DiamondImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DiamondImplToJson(
      this,
    );
  }
}

abstract class _Diamond implements Diamond {
  const factory _Diamond({required final int diamond}) = _$DiamondImpl;

  factory _Diamond.fromJson(Map<String, dynamic> json) = _$DiamondImpl.fromJson;

  @override
  int get diamond;

  /// Create a copy of Diamond
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$DiamondImplCopyWith<_$DiamondImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
