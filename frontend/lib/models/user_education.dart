import 'package:json_annotation/json_annotation.dart';

part 'user_education.g.dart';

@JsonSerializable()
class UserEducation {
  final int id;
  @JsonKey(name: 'user_id')
  final int userId;
  @JsonKey(name: 'module_type')
  final String moduleType;
  @JsonKey(name: 'content_id')
  final String contentId;
  final bool completed;
  @JsonKey(name: 'progress_percentage')
  final double progressPercentage;
  @JsonKey(name: 'time_spent_minutes')
  final int timeSpentMinutes;
  @JsonKey(name: 'quiz_score')
  final double? quizScore;
  @JsonKey(name: 'completed_at')
  final DateTime? completedAt;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;
  @JsonKey(name: 'updated_at')
  final DateTime updatedAt;

  UserEducation({
    required this.id,
    required this.userId,
    required this.moduleType,
    required this.contentId,
    required this.completed,
    required this.progressPercentage,
    required this.timeSpentMinutes,
    this.quizScore,
    this.completedAt,
    required this.createdAt,
    required this.updatedAt,
  });

  factory UserEducation.fromJson(Map<String, dynamic> json) => _$UserEducationFromJson(json);
  Map<String, dynamic> toJson() => _$UserEducationToJson(this);
}

@JsonSerializable()
class EducationModule {
  final String id;
  final String title;
  final String description;
  final String content;
  final String type;
  @JsonKey(name: 'estimated_duration')
  final int estimatedDuration;
  final String difficulty;
  @JsonKey(name: 'quiz_questions')
  final List<QuizQuestion>? quizQuestions;
  @JsonKey(name: 'is_mandatory')
  final bool isMandatory;
  @JsonKey(name: 'prerequisite_modules')
  final List<String> prerequisiteModules;

  EducationModule({
    required this.id,
    required this.title,
    required this.description,
    required this.content,
    required this.type,
    required this.estimatedDuration,
    required this.difficulty,
    this.quizQuestions,
    required this.isMandatory,
    required this.prerequisiteModules,
  });

  factory EducationModule.fromJson(Map<String, dynamic> json) => _$EducationModuleFromJson(json);
  Map<String, dynamic> toJson() => _$EducationModuleToJson(this);
}

@JsonSerializable()
class QuizQuestion {
  final String question;
  final List<String> options;
  @JsonKey(name: 'correct_answer')
  final int correctAnswer;
  final String explanation;

  QuizQuestion({
    required this.question,
    required this.options,
    required this.correctAnswer,
    required this.explanation,
  });

  factory QuizQuestion.fromJson(Map<String, dynamic> json) => _$QuizQuestionFromJson(json);
  Map<String, dynamic> toJson() => _$QuizQuestionToJson(this);
}
