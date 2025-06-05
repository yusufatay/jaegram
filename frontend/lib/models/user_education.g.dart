// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_education.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

UserEducation _$UserEducationFromJson(Map<String, dynamic> json) =>
    UserEducation(
      id: (json['id'] as num).toInt(),
      userId: (json['user_id'] as num).toInt(),
      moduleType: json['module_type'] as String,
      contentId: json['content_id'] as String,
      completed: json['completed'] as bool,
      progressPercentage: (json['progress_percentage'] as num).toDouble(),
      timeSpentMinutes: (json['time_spent_minutes'] as num).toInt(),
      quizScore: (json['quiz_score'] as num?)?.toDouble(),
      completedAt: json['completed_at'] == null
          ? null
          : DateTime.parse(json['completed_at'] as String),
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );

Map<String, dynamic> _$UserEducationToJson(UserEducation instance) =>
    <String, dynamic>{
      'id': instance.id,
      'user_id': instance.userId,
      'module_type': instance.moduleType,
      'content_id': instance.contentId,
      'completed': instance.completed,
      'progress_percentage': instance.progressPercentage,
      'time_spent_minutes': instance.timeSpentMinutes,
      'quiz_score': instance.quizScore,
      'completed_at': instance.completedAt?.toIso8601String(),
      'created_at': instance.createdAt.toIso8601String(),
      'updated_at': instance.updatedAt.toIso8601String(),
    };

EducationModule _$EducationModuleFromJson(Map<String, dynamic> json) =>
    EducationModule(
      id: json['id'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      content: json['content'] as String,
      type: json['type'] as String,
      estimatedDuration: (json['estimated_duration'] as num).toInt(),
      difficulty: json['difficulty'] as String,
      quizQuestions: (json['quiz_questions'] as List<dynamic>?)
          ?.map((e) => QuizQuestion.fromJson(e as Map<String, dynamic>))
          .toList(),
      isMandatory: json['is_mandatory'] as bool,
      prerequisiteModules: (json['prerequisite_modules'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
    );

Map<String, dynamic> _$EducationModuleToJson(EducationModule instance) =>
    <String, dynamic>{
      'id': instance.id,
      'title': instance.title,
      'description': instance.description,
      'content': instance.content,
      'type': instance.type,
      'estimated_duration': instance.estimatedDuration,
      'difficulty': instance.difficulty,
      'quiz_questions': instance.quizQuestions,
      'is_mandatory': instance.isMandatory,
      'prerequisite_modules': instance.prerequisiteModules,
    };

QuizQuestion _$QuizQuestionFromJson(Map<String, dynamic> json) => QuizQuestion(
      question: json['question'] as String,
      options:
          (json['options'] as List<dynamic>).map((e) => e as String).toList(),
      correctAnswer: (json['correct_answer'] as num).toInt(),
      explanation: json['explanation'] as String,
    );

Map<String, dynamic> _$QuizQuestionToJson(QuizQuestion instance) =>
    <String, dynamic>{
      'question': instance.question,
      'options': instance.options,
      'correct_answer': instance.correctAnswer,
      'explanation': instance.explanation,
    };
