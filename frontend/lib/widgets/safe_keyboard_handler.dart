import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// A widget that safely handles keyboard events to prevent Flutter keyboard assertion errors
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
  final Set<PhysicalKeyboardKey> _pressedKeys = <PhysicalKeyboardKey>{};

  @override
  Widget build(BuildContext context) {
    return Focus(
      onKeyEvent: (FocusNode node, KeyEvent event) {
        // Handle keyboard events safely to prevent assertion errors
        if (event is KeyDownEvent) {
          if (_pressedKeys.contains(event.physicalKey)) {
            // Key is already pressed, ignore duplicate event
            return KeyEventResult.handled;
          }
          _pressedKeys.add(event.physicalKey);
        } else if (event is KeyUpEvent) {
          _pressedKeys.remove(event.physicalKey);
        }
        
        return KeyEventResult.ignored;
      },
      child: widget.child,
    );
  }
}
