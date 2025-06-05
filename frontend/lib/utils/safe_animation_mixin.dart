import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter/foundation.dart';

/// A mixin that provides safe animation controller management to prevent
/// KeyUpEvent exceptions and memory leaks in Flutter desktop applications.
/// 
/// Usage: Instead of using `TickerProviderStateMixin`, use `SafeTickerProviderMixin`
mixin SafeTickerProviderMixin<T extends StatefulWidget> on State<T>
    implements TickerProvider {
  Set<AnimationController>? _animationControllers;

  @override
  Ticker createTicker(TickerCallback onTick) {
    return Ticker(onTick, debugLabel: 'created by ${describeIdentity(this)}');
  }

  /// Register an animation controller for automatic disposal
  void registerAnimationController(AnimationController controller) {
    _animationControllers ??= <AnimationController>{};
    _animationControllers!.add(controller);
  }

  /// Unregister an animation controller (if manually disposed early)
  void unregisterAnimationController(AnimationController controller) {
    _animationControllers?.remove(controller);
  }

  /// Create and automatically register an animation controller for safe disposal
  AnimationController createSafeAnimationController({
    required Duration duration,
    Duration? reverseDuration,
    String? debugLabel,
    double lowerBound = 0.0,
    double upperBound = 1.0,
    AnimationBehavior animationBehavior = AnimationBehavior.normal,
    required TickerProvider vsync,
  }) {
    final controller = AnimationController(
      duration: duration,
      reverseDuration: reverseDuration,
      debugLabel: debugLabel,
      lowerBound: lowerBound,
      upperBound: upperBound,
      animationBehavior: animationBehavior,
      vsync: vsync,
    );
    registerAnimationController(controller);
    return controller;
  }

  @override
  void dispose() {
    // Safely dispose all registered animation controllers
    if (_animationControllers != null) {
      for (final controller in _animationControllers!.toList()) {
        try {
          // Just try to dispose - if already disposed, it will be caught
          controller.dispose();
        } catch (e) {
          // Silently handle any dispose errors - they're usually harmless
          if (kDebugMode) {
            debugPrint('Info: Animation controller dispose handled: ${e.toString().contains('disposed') ? 'already disposed' : e}');
          }
        }
      }
      _animationControllers!.clear();
      _animationControllers = null; // Ensure the set is nullified
    }
    super.dispose();
  }
}

/// A widget that safely handles keyboard events to prevent KeyUpEvent exceptions
class SafeKeyboardHandler extends StatefulWidget {
  final Widget child;
  final VoidCallback? onEscape;
  final VoidCallback? onEnter;

  const SafeKeyboardHandler({
    super.key,
    required this.child,
    this.onEscape,
    this.onEnter,
  });

  @override
  State<SafeKeyboardHandler> createState() => _SafeKeyboardHandlerState();
}

class _SafeKeyboardHandlerState extends State<SafeKeyboardHandler> {
  final FocusNode _focusNode = FocusNode();

  @override
  void initState() {
    super.initState();
    // Request focus after the first frame
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        _focusNode.requestFocus();
      }
    });
  }

  @override
  void dispose() {
    _focusNode.dispose();
    super.dispose();
  }

  bool _handleKeyEvent(KeyEvent event) {
    if (event is KeyDownEvent) {
      if (event.logicalKey == LogicalKeyboardKey.escape && widget.onEscape != null) {
        widget.onEscape!();
        return true;
      }
      if (event.logicalKey == LogicalKeyboardKey.enter && widget.onEnter != null) {
        widget.onEnter!();
        return true;
      }
    }
    return false;
  }

  @override
  Widget build(BuildContext context) {
    return Focus(
      focusNode: _focusNode,
      onKeyEvent: (node, event) {
        try {
          return _handleKeyEvent(event) ? KeyEventResult.handled : KeyEventResult.ignored;
        } catch (e) {
          debugPrint('Error handling key event: $e');
          return KeyEventResult.ignored;
        }
      },
      child: widget.child,
    );
  }
}

/// Extension for safe animation controller creation
extension SafeAnimationControllerExtension on State {
  AnimationController createSafeAnimationController({
    Duration? duration,
    Duration? reverseDuration,
    String? debugLabel,
    double lowerBound = 0.0,
    double upperBound = 1.0,
    AnimationBehavior animationBehavior = AnimationBehavior.normal,
    required TickerProvider vsync,
  }) {
    final controller = AnimationController(
      duration: duration,
      reverseDuration: reverseDuration,
      debugLabel: debugLabel,
      lowerBound: lowerBound,
      upperBound: upperBound,
      animationBehavior: animationBehavior,
      vsync: vsync,
    );

    // Register for automatic disposal if using SafeTickerProviderMixin
    if (this is SafeTickerProviderMixin) {
      (this as SafeTickerProviderMixin).registerAnimationController(controller);
    }

    return controller;
  }
}
