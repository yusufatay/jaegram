import 'package:flutter/material.dart';

class GradientBackground extends StatelessWidget {
  final Widget child;
  final List<Color>? colors;
  final AlignmentGeometry begin;
  final AlignmentGeometry end;

  const GradientBackground({
    super.key,
    required this.child,
    this.colors,
    this.begin = Alignment.topCenter,
    this.end = Alignment.bottomCenter,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: colors ?? [
            const Color(0xFF833AB4),
            const Color(0xFFE1306C),
            const Color(0xFFFD1D1D),
            const Color(0xFFF77737),
          ],
          begin: begin,
          end: end,
        ),
      ),
      child: child,
    );
  }
}
