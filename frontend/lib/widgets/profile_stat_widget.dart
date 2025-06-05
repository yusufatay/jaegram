import 'package:flutter/material.dart';

class ProfileStatWidget extends StatelessWidget {
  final String label;
  final String value;
  final Color? color;
  final IconData? icon;

  const ProfileStatWidget({
    super.key,
    required this.label,
    required this.value,
    this.color,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (icon != null)
          Icon(icon, color: color ?? Theme.of(context).colorScheme.primary, size: 28),
        if (icon != null) const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 20,
            color: color ?? Theme.of(context).colorScheme.primary,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: TextStyle(color: Colors.grey[600], fontSize: 13),
        ),
      ],
    );
  }
} 