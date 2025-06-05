import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'dart:developer' as developer;

/// Helper class to navigate an admin user directly to the admin panel.
/// This bypasses the normal routing system when needed.
class AdminRouteHelper {
  /// Force navigate to admin panel
  static void navigateToAdminPanel(BuildContext context) {
    developer.log('Force navigating to admin panel', name: 'AdminRouteHelper', level: 1000);
    
    // Small delay to ensure state updates have propagated
    Future.delayed(const Duration(milliseconds: 100), () {
      try {
        GoRouter.of(context).go('/admin');
        developer.log('Admin panel navigation triggered', name: 'AdminRouteHelper', level: 1000);
      } catch (e) {
        developer.log('Failed to navigate to admin panel: $e', name: 'AdminRouteHelper', level: 1000);
      }
    });
  }
}
