import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// A safe keyboard handler that prevents assertion failures
/// and properly manages keyboard events for the application
class SafeKeyboardHandler extends StatefulWidget {
  final Widget child;
  
  const SafeKeyboardHandler({
    super.key,
    required this.child,
  });

  @override
  State<SafeKeyboardHandler> createState() => _SafeKeyboardHandlerState();
}

class _SafeKeyboardHandlerState extends State<SafeKeyboardHandler> {
  late FocusNode _focusNode;
  
  @override
  void initState() {
    super.initState();
    _focusNode = FocusNode();
  }
  
  @override
  void dispose() {
    _focusNode.dispose();
    super.dispose();
  }
  
  KeyEventResult _handleKeyEvent(FocusNode node, KeyEvent event) {
    // Handle keyboard events safely
    try {
      // Check if the event is a key down event
      if (event is KeyDownEvent) {
        // Handle specific keys if needed
        if (event.logicalKey == LogicalKeyboardKey.escape) {
          // Handle escape key
          return KeyEventResult.handled;
        }
        
        // Handle back button on Android
        if (event.logicalKey == LogicalKeyboardKey.goBack) {
          return KeyEventResult.handled;
        }
      }
      
      // Let other widgets handle the event
      return KeyEventResult.ignored;
    } catch (e) {
      // Safely handle any keyboard event errors
      debugPrint('SafeKeyboardHandler: Error handling key event: $e');
      return KeyEventResult.ignored;
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Focus(
      focusNode: _focusNode,
      onKeyEvent: _handleKeyEvent,
      child: widget.child,
    );
  }
}

/// Extension to provide safe keyboard handling utilities
extension SafeKeyboardUtils on BuildContext {
  /// Safely dismiss the keyboard
  void dismissKeyboard() {
    try {
      FocusScope.of(this).unfocus();
    } catch (e) {
      debugPrint('SafeKeyboardUtils: Error dismissing keyboard: $e');
    }
  }
  
  /// Safely request focus for a widget
  void safeFocus(FocusNode focusNode) {
    try {
      if (mounted) {
        FocusScope.of(this).requestFocus(focusNode);
      }
    } catch (e) {
      debugPrint('SafeKeyboardUtils: Error requesting focus: $e');
    }
  }
}
