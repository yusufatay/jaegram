import 'package:flutter/material.dart';
import 'package:instagram_puan_app/themes/app_theme.dart';

class GradientButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final EdgeInsetsGeometry? padding;
  final double? width;
  final double? height;
  final bool isLoading;
  final IconData? icon;
  final bool useInstagramGradient;
  final double borderRadius;
  final TextStyle? textStyle;

  const GradientButton({
    super.key,
    required this.text,
    this.onPressed,
    this.padding,
    this.width,
    this.height,
    this.isLoading = false,
    this.icon,
    this.useInstagramGradient = true,
    this.borderRadius = 12.0,
    this.textStyle,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    final gradient = useInstagramGradient 
        ? AppTheme.instagramGradient 
        : AppTheme.primaryGradient;
    
    final defaultTextStyle = const TextStyle(
      fontSize: 16,
      fontWeight: FontWeight.w600,
      color: Colors.white,
    );

    return Container(
      width: width,
      height: height ?? 48,
      decoration: BoxDecoration(
        gradient: onPressed != null ? gradient : null,
        color: onPressed == null ? Colors.grey.shade400 : null,
        borderRadius: BorderRadius.circular(borderRadius),
        boxShadow: onPressed != null ? [
          BoxShadow(
            color: useInstagramGradient 
                ? const Color(0xFFDD2A7B).withValues(alpha: 0.3)
                : theme.primaryColor.withValues(alpha: 0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ] : null,
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: isLoading ? null : onPressed,
          borderRadius: BorderRadius.circular(borderRadius),
          child: Container(
            padding: padding ?? const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            child: isLoading
                ? const Center(
                    child: SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        color: Colors.white,
                        strokeWidth: 2,
                      ),
                    ),
                  )
                : Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      if (icon != null) ...[
                        Icon(
                          icon,
                          color: Colors.white,
                          size: 16, // Further reduced size
                        ),
                        const SizedBox(width: 4), // Further reduced spacing
                      ],
                      Flexible(
                        child: Text(
                          text,
                          style: textStyle ?? defaultTextStyle,
                          textAlign: TextAlign.center,
                          overflow: TextOverflow.ellipsis,
                          maxLines: 1,
                        ),
                      ),
                    ],
                  ),
          ),
        ),
      ),
    );
  }
}

class OutlineGradientButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final EdgeInsetsGeometry? padding;
  final double? width;
  final double? height;
  final bool isLoading;
  final IconData? icon;
  final bool useInstagramGradient;
  final double borderRadius;
  final double borderWidth;
  final TextStyle? textStyle;

  const OutlineGradientButton({
    super.key,
    required this.text,
    this.onPressed,
    this.padding,
    this.width,
    this.height,
    this.isLoading = false,
    this.icon,
    this.useInstagramGradient = true,
    this.borderRadius = 12.0,
    this.borderWidth = 2.0,
    this.textStyle,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    final gradient = useInstagramGradient 
        ? AppTheme.instagramGradient 
        : AppTheme.primaryGradient;
    
    final defaultTextStyle = TextStyle(
      fontSize: 16,
      fontWeight: FontWeight.w600,
      color: useInstagramGradient 
          ? const Color(0xFFDD2A7B) 
          : theme.primaryColor,
    );

    return Container(
      width: width,
      height: height ?? 48,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(borderRadius),
      ),
      child: CustomPaint(
        painter: GradientBorderPainter(
          gradient: gradient,
          borderWidth: borderWidth,
          borderRadius: borderRadius,
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: isLoading ? null : onPressed,
            borderRadius: BorderRadius.circular(borderRadius),
            child: Container(
              padding: padding ?? const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              child: isLoading
                  ? Center(
                      child: SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          color: useInstagramGradient 
                              ? const Color(0xFFDD2A7B) 
                              : theme.primaryColor,
                          strokeWidth: 2,
                        ),
                      ),
                    )
                  : Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        if (icon != null) ...[
                          Icon(
                            icon,
                            color: useInstagramGradient 
                                ? const Color(0xFFDD2A7B) 
                                : theme.primaryColor,
                            size: 16,
                          ),
                          const SizedBox(width: 4),
                        ],
                        Flexible(
                          child: Text(
                            text,
                            style: textStyle ?? defaultTextStyle,
                            textAlign: TextAlign.center,
                            overflow: TextOverflow.ellipsis,
                            maxLines: 1,
                          ),
                        ),
                      ],
                    ),
            ),
          ),
        ),
      ),
    );
  }
}

class GradientBorderPainter extends CustomPainter {
  final Gradient gradient;
  final double borderWidth;
  final double borderRadius;

  GradientBorderPainter({
    required this.gradient,
    required this.borderWidth,
    required this.borderRadius,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final rect = Rect.fromLTWH(0, 0, size.width, size.height);
    final rrect = RRect.fromRectAndRadius(rect, Radius.circular(borderRadius));
    
    final paint = Paint()
      ..shader = gradient.createShader(rect)
      ..style = PaintingStyle.stroke
      ..strokeWidth = borderWidth;
    
    canvas.drawRRect(rrect, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class IconGradientButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback? onPressed;
  final double size;
  final bool useInstagramGradient;
  final String? tooltip;

  const IconGradientButton({
    super.key,
    required this.icon,
    this.onPressed,
    this.size = 48.0,
    this.useInstagramGradient = true,
    this.tooltip,
  });

  @override
  Widget build(BuildContext context) {
    final gradient = useInstagramGradient 
        ? AppTheme.instagramGradient 
        : AppTheme.primaryGradient;

    final button = Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        gradient: onPressed != null ? gradient : null,
        color: onPressed == null ? Colors.grey.shade400 : null,
        shape: BoxShape.circle,
        boxShadow: onPressed != null ? [
          BoxShadow(
            color: useInstagramGradient 
                ? const Color(0xFFDD2A7B).withValues(alpha: 0.3)
                : Theme.of(context).primaryColor.withValues(alpha: 0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ] : null,
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onPressed,
          borderRadius: BorderRadius.circular(size / 2),
          child: Icon(
            icon,
            color: Colors.white,
            size: size * 0.5,
          ),
        ),
      ),
    );

    if (tooltip != null) {
      return Tooltip(
        message: tooltip!,
        child: button,
      );
    }

    return button;
  }
}
