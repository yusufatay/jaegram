import 'package:flutter/material.dart';
import 'package:instagram_puan_app/widgets/instagram_challenge_dialog.dart';

/// Helper function to show Instagram challenge dialog
Future<Map<String, dynamic>?> showInstagramChallengeDialog({
  required BuildContext context,
  required String challengeId,
  required String challengeType,
  required String message,
  required Map<String, dynamic> challengeData,
  String? userToken,
}) {
  return showDialog<Map<String, dynamic>>(
    context: context,
    barrierDismissible: false,
    builder: (context) => InstagramChallengeDialog(
      challengeId: challengeId,
      challengeType: challengeType,
      message: message,
      challengeData: challengeData,
      userToken: userToken,
    ),
  );
}

/// Helper function to show Instagram challenge dialog for login flow
Future<Map<String, dynamic>?> showInstagramLoginChallengeDialog({
  required BuildContext context,
  required String username,
  required String password,
  required Map<String, dynamic> challengeInfo,
}) {
  return showDialog<Map<String, dynamic>>(
    context: context,
    barrierDismissible: false,
    builder: (context) => InstagramChallengeDialog.forLogin(
      username: username,
      password: password,
      challengeInfo: challengeInfo,
    ),
  );
}
