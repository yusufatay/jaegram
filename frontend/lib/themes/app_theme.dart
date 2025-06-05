import 'package:flutter/material.dart';

class AppTheme {
  // Color constants
  static const Color primaryColor = Color(0xFFDD2A7B);
  static const Color secondaryColor = Color(0xFF8134AF);
  static const Color accentColor = Color(0xFFF77737);
  static const Color yellowColor = Color(0xFFFCAF45);
  
  // Light theme colors
  static const Color lightBackgroundColor = Color(0xFFFAFAFA);
  static const Color lightSurfaceColor = Colors.white;
  static const Color lightOnSurfaceColor = Color(0xFF262626);
  static const Color lightOnPrimaryColor = Colors.white;
  
  // Dark theme colors
  static const Color darkBackgroundColor = Color(0xFF121212);
  static const Color darkSurfaceColor = Color(0xFF1E1E1E);
  static const Color darkOnSurfaceColor = Color(0xFFE1E1E1);
  static const Color darkOnPrimaryColor = Colors.white;

  // Gradient definitions
  static const LinearGradient instagramGradient = LinearGradient(
    colors: [primaryColor, secondaryColor, accentColor, yellowColor],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient primaryGradient = LinearGradient(
    colors: [primaryColor, secondaryColor],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient backgroundGradient = LinearGradient(
    colors: [Color(0xFFF8F9FA), Color(0xFFE9ECEF)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  static const LinearGradient darkBackgroundGradient = LinearGradient(
    colors: [Color(0xFF1A1A1A), Color(0xFF0D1117)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  // Enhanced Light Theme
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      
      // Color Scheme
      colorScheme: const ColorScheme.light(
        primary: primaryColor,
        secondary: secondaryColor,
        tertiary: accentColor,
        surface: lightSurfaceColor,
        onPrimary: lightOnPrimaryColor,
        onSecondary: lightOnPrimaryColor,
        onSurface: lightOnSurfaceColor,
        error: Color(0xFFE53E3E),
        onError: Colors.white,
        outline: Color(0xFFDBDBDB),
        surfaceContainerHighest: Color(0xFFF7F7F7),
        inverseSurface: Color(0xFF2D2D2D),
        onInverseSurface: Colors.white,
        inversePrimary: Color(0xFFFFB3D9),
      ),

      // Scaffold background
      scaffoldBackgroundColor: lightBackgroundColor,

      // App Bar Theme
      appBarTheme: const AppBarTheme(
        elevation: 0,
        scrolledUnderElevation: 1,
        backgroundColor: Colors.transparent,
        foregroundColor: lightOnSurfaceColor,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: lightOnSurfaceColor,
          fontSize: 20,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.5,
        ),
        iconTheme: IconThemeData(color: lightOnSurfaceColor, size: 24),
        actionsIconTheme: IconThemeData(color: lightOnSurfaceColor, size: 24),
      ),

      // Card Theme
      cardTheme: CardThemeData(
        elevation: 4,
        shadowColor: Colors.black.withValues(alpha: 0.08),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        color: lightSurfaceColor,
        surfaceTintColor: Colors.transparent,
        margin: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
      ),

      // Elevated Button Theme
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          elevation: 6,
          shadowColor: primaryColor.withValues(alpha: 0.4),
          backgroundColor: primaryColor,
          foregroundColor: lightOnPrimaryColor,
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 18),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w700,
            letterSpacing: 0.8,
          ),
        ),
      ),

      // Gradient Elevated Button (Custom)
      extensions: [
        _GradientButtonTheme(
          gradient: primaryGradient,
          borderRadius: BorderRadius.circular(16),
          elevation: 8,
          shadowColor: primaryColor.withValues(alpha: 0.3),
        ),
      ],

      // Text Button Theme
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primaryColor,
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          textStyle: const TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.3,
          ),
        ),
      ),

      // Outlined Button Theme
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primaryColor,
          side: const BorderSide(color: primaryColor, width: 2),
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 18),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.5,
          ),
        ),
      ),

      // Input Decoration Theme
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: const Color(0xFFF8F9FA),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFFE1E5E9), width: 1.5),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFFE1E5E9), width: 1.5),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: primaryColor, width: 2.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFFE53E3E), width: 1.5),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFFE53E3E), width: 2.5),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
        hintStyle: TextStyle(
          color: lightOnSurfaceColor.withValues(alpha: 0.6),
          fontSize: 16,
          fontWeight: FontWeight.w400,
        ),
        labelStyle: TextStyle(
          color: lightOnSurfaceColor.withValues(alpha: 0.8),
          fontSize: 16,
          fontWeight: FontWeight.w500,
        ),
        prefixIconColor: primaryColor,
        suffixIconColor: primaryColor,
      ),

      // Bottom Navigation Bar Theme
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: lightSurfaceColor,
        selectedItemColor: primaryColor,
        unselectedItemColor: Color(0xFF8E8E8E),
        type: BottomNavigationBarType.fixed,
        elevation: 12,
        selectedLabelStyle: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w700,
        ),
        unselectedLabelStyle: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w500,
        ),
      ),

      // Floating Action Button Theme
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: primaryColor,
        foregroundColor: lightOnPrimaryColor,
        elevation: 8,
        shape: CircleBorder(),
      ),

      // Snack Bar Theme
      snackBarTheme: SnackBarThemeData(
        backgroundColor: lightOnSurfaceColor,
        contentTextStyle: const TextStyle(color: lightSurfaceColor, fontWeight: FontWeight.w500),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        behavior: SnackBarBehavior.floating,
        elevation: 8,
      ),

      // Chip Theme
      chipTheme: ChipThemeData(
        backgroundColor: const Color(0xFFF1F3F4),
        selectedColor: primaryColor.withValues(alpha: 0.2),
        labelStyle: const TextStyle(color: lightOnSurfaceColor, fontWeight: FontWeight.w500),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        elevation: 2,
      ),

      // Switch Theme
      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) return primaryColor;
          return const Color(0xFFDBDBDB);
        }),
        trackColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) return primaryColor.withValues(alpha: 0.5);
          return const Color(0xFFE1E5E9);
        }),
      ),

      // Slider Theme
      sliderTheme: SliderThemeData(
        activeTrackColor: primaryColor,
        inactiveTrackColor: primaryColor.withValues(alpha: 0.3),
        thumbColor: primaryColor,
        overlayColor: primaryColor.withValues(alpha: 0.2),
        trackHeight: 6,
        thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 10),
      ),

      // Progress Indicator Theme
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: primaryColor,
        linearTrackColor: Color(0xFFE1E5E9),
        circularTrackColor: Color(0xFFE1E5E9),
      ),

      // Divider Theme
      dividerTheme: const DividerThemeData(
        color: Color(0xFFE1E5E9),
        thickness: 1,
        space: 1,
      ),

      // Enhanced Text Theme
      textTheme: const TextTheme(
        displayLarge: TextStyle(
          fontSize: 36,
          fontWeight: FontWeight.w800,
          color: lightOnSurfaceColor,
          height: 1.1,
          letterSpacing: -0.5,
        ),
        displayMedium: TextStyle(
          fontSize: 30,
          fontWeight: FontWeight.w700,
          color: lightOnSurfaceColor,
          height: 1.2,
          letterSpacing: -0.25,
        ),
        displaySmall: TextStyle(
          fontSize: 26,
          fontWeight: FontWeight.w700,
          color: lightOnSurfaceColor,
          height: 1.3,
        ),
        headlineLarge: TextStyle(
          fontSize: 24,
          fontWeight: FontWeight.w700,
          color: lightOnSurfaceColor,
          height: 1.3,
          letterSpacing: 0.25,
        ),
        headlineMedium: TextStyle(
          fontSize: 22,
          fontWeight: FontWeight.w600,
          color: lightOnSurfaceColor,
          height: 1.4,
          letterSpacing: 0.25,
        ),
        headlineSmall: TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: lightOnSurfaceColor,
          height: 1.4,
          letterSpacing: 0.15,
        ),
        titleLarge: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.w700,
          color: lightOnSurfaceColor,
          height: 1.4,
          letterSpacing: 0.15,
        ),
        titleMedium: TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w600,
          color: lightOnSurfaceColor,
          height: 1.5,
          letterSpacing: 0.15,
        ),
        titleSmall: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: lightOnSurfaceColor,
          height: 1.5,
          letterSpacing: 0.1,
        ),
        bodyLarge: TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w400,
          color: lightOnSurfaceColor,
          height: 1.6,
          letterSpacing: 0.5,
        ),
        bodyMedium: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w400,
          color: lightOnSurfaceColor,
          height: 1.6,
          letterSpacing: 0.25,
        ),
        bodySmall: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w400,
          color: lightOnSurfaceColor,
          height: 1.6,
          letterSpacing: 0.4,
        ),
        labelLarge: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: lightOnSurfaceColor,
          letterSpacing: 0.1,
        ),
        labelMedium: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: lightOnSurfaceColor,
          letterSpacing: 0.5,
        ),
        labelSmall: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w500,
          color: lightOnSurfaceColor,
          letterSpacing: 1.5,
        ),
      ),

      // Icon Theme
      iconTheme: const IconThemeData(
        color: lightOnSurfaceColor,
        size: 24,
      ),

      // Primary Icon Theme
      primaryIconTheme: const IconThemeData(
        color: lightOnPrimaryColor,
        size: 24,
      ),

      // List Tile Theme
      listTileTheme: const ListTileThemeData(
        contentPadding: EdgeInsets.symmetric(horizontal: 20, vertical: 8),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(12))),
        tileColor: lightSurfaceColor,
        textColor: lightOnSurfaceColor,
        iconColor: primaryColor,
      ),

      // Tab Bar Theme
      tabBarTheme: const TabBarThemeData(
        labelColor: primaryColor,
        unselectedLabelColor: Color(0xFF8E8E8E),
        indicatorColor: primaryColor,
        labelStyle: TextStyle(fontWeight: FontWeight.w600),
        unselectedLabelStyle: TextStyle(fontWeight: FontWeight.w400),
      ),
    );
  }

  // Enhanced Dark Theme
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      
      // Color Scheme
      colorScheme: const ColorScheme.dark(
        primary: primaryColor,
        secondary: secondaryColor,
        tertiary: accentColor,
        surface: darkSurfaceColor,
        onPrimary: darkOnPrimaryColor,
        onSecondary: darkOnPrimaryColor,
        onSurface: darkOnSurfaceColor,
        error: Color(0xFFFF6B6B),
        onError: Colors.white,
        outline: Color(0xFF484848),
        surfaceContainerHighest: Color(0xFF2A2A2A),
        inverseSurface: Color(0xFFE1E1E1),
        onInverseSurface: Color(0xFF1A1A1A),
        inversePrimary: Color(0xFF8B1538),
      ),

      // Scaffold background
      scaffoldBackgroundColor: darkBackgroundColor,

      // App Bar Theme
      appBarTheme: const AppBarTheme(
        elevation: 0,
        scrolledUnderElevation: 1,
        backgroundColor: Colors.transparent,
        foregroundColor: darkOnSurfaceColor,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: darkOnSurfaceColor,
          fontSize: 20,
          fontWeight: FontWeight.w700,
          letterSpacing: 0.5,
        ),
        iconTheme: IconThemeData(color: darkOnSurfaceColor, size: 24),
        actionsIconTheme: IconThemeData(color: darkOnSurfaceColor, size: 24),
      ),

      // Card Theme
      cardTheme: CardThemeData(
        elevation: 6,
        shadowColor: Colors.black.withValues(alpha: 0.3),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        color: darkSurfaceColor,
        surfaceTintColor: Colors.transparent,
        margin: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
      ),

      // Similar theme properties adapted for dark mode...
      // (I'll continue with key dark theme properties)

      // Input Decoration Theme for Dark
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: const Color(0xFF2A2A2A),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFF484848), width: 1.5),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFF484848), width: 1.5),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: primaryColor, width: 2.5),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
        hintStyle: TextStyle(
          color: darkOnSurfaceColor.withValues(alpha: 0.6),
          fontSize: 16,
          fontWeight: FontWeight.w400,
        ),
        labelStyle: TextStyle(
          color: darkOnSurfaceColor.withValues(alpha: 0.8),
          fontSize: 16,
          fontWeight: FontWeight.w500,
        ),
        prefixIconColor: primaryColor,
        suffixIconColor: primaryColor,
      ),

      // Bottom Navigation Bar Theme for Dark
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: darkSurfaceColor,
        selectedItemColor: primaryColor,
        unselectedItemColor: Color(0xFF8E8E8E),
        type: BottomNavigationBarType.fixed,
        elevation: 12,
        selectedLabelStyle: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w700,
        ),
        unselectedLabelStyle: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w500,
        ),
      ),

      // Text Theme for Dark
      textTheme: const TextTheme(
        displayLarge: TextStyle(
          fontSize: 36,
          fontWeight: FontWeight.w800,
          color: darkOnSurfaceColor,
          height: 1.1,
          letterSpacing: -0.5,
        ),
        displayMedium: TextStyle(
          fontSize: 30,
          fontWeight: FontWeight.w700,
          color: darkOnSurfaceColor,
          height: 1.2,
          letterSpacing: -0.25,
        ),
        // ... other text styles adapted for dark theme
      ),

      // Icon themes for dark
      iconTheme: const IconThemeData(
        color: darkOnSurfaceColor,
        size: 24,
      ),
      primaryIconTheme: const IconThemeData(
        color: darkOnPrimaryColor,
        size: 24,
      ),
    );
  }

  // Helper methods for custom gradients
  static BoxDecoration getInstagramGradientDecoration({
    BorderRadius? borderRadius,
    double opacity = 1.0,
  }) {
    return BoxDecoration(
      gradient: LinearGradient(
        colors: instagramGradient.colors
            .map((color) => color.withValues(alpha: opacity))
            .toList(),
        begin: instagramGradient.begin,
        end: instagramGradient.end,
      ),
      borderRadius: borderRadius ?? BorderRadius.circular(12),
    );
  }

  static BoxDecoration getPrimaryGradientDecoration({
    BorderRadius? borderRadius,
    double opacity = 1.0,
  }) {
    return BoxDecoration(
      gradient: LinearGradient(
        colors: primaryGradient.colors
            .map((color) => color.withValues(alpha: opacity))
            .toList(),
        begin: primaryGradient.begin,
        end: primaryGradient.end,
      ),
      borderRadius: borderRadius ?? BorderRadius.circular(12),
    );
  }
}

// Custom theme extension for gradient buttons
class _GradientButtonTheme extends ThemeExtension<_GradientButtonTheme> {
  final Gradient gradient;
  final BorderRadius borderRadius;
  final double elevation;
  final Color shadowColor;

  const _GradientButtonTheme({
    required this.gradient,
    required this.borderRadius,
    required this.elevation,
    required this.shadowColor,
  });

  @override
  ThemeExtension<_GradientButtonTheme> copyWith({
    Gradient? gradient,
    BorderRadius? borderRadius,
    double? elevation,
    Color? shadowColor,
  }) {
    return _GradientButtonTheme(
      gradient: gradient ?? this.gradient,
      borderRadius: borderRadius ?? this.borderRadius,
      elevation: elevation ?? this.elevation,
      shadowColor: shadowColor ?? this.shadowColor,
    );
  }

  @override
  ThemeExtension<_GradientButtonTheme> lerp(
    ThemeExtension<_GradientButtonTheme>? other,
    double t,
  ) {
    if (other is! _GradientButtonTheme) return this;
    return _GradientButtonTheme(
      gradient: Gradient.lerp(gradient, other.gradient, t)!,
      borderRadius: BorderRadius.lerp(borderRadius, other.borderRadius, t)!,
      elevation: (elevation * (1 - t)) + (other.elevation * t),
      shadowColor: Color.lerp(shadowColor, other.shadowColor, t)!,
    );
  }
}
