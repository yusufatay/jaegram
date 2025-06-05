// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'active_task_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ActiveTaskModelImpl _$$ActiveTaskModelImplFromJson(
        Map<String, dynamic> json) =>
    _$ActiveTaskModelImpl(
      id: (json['id'] as num).toInt(),
      orderId: (json['orderId'] as num).toInt(),
      orderPostUrl: json['orderPostUrl'] as String,
      orderType: json['orderType'] as String,
      commentText: json['commentText'] as String?,
      status: json['status'] as String,
      assignedAt: json['assignedAt'] == null
          ? null
          : DateTime.parse(json['assignedAt'] as String),
      expiresAt: json['expiresAt'] == null
          ? null
          : DateTime.parse(json['expiresAt'] as String),
    );

Map<String, dynamic> _$$ActiveTaskModelImplToJson(
        _$ActiveTaskModelImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'orderId': instance.orderId,
      'orderPostUrl': instance.orderPostUrl,
      'orderType': instance.orderType,
      'commentText': instance.commentText,
      'status': instance.status,
      'assignedAt': instance.assignedAt?.toIso8601String(),
      'expiresAt': instance.expiresAt?.toIso8601String(),
    };
