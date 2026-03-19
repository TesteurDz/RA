import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppColors {
  AppColors._();

  static const Color background = Color(0xFF0F0F14);
  static const Color surface = Color(0xFF1A1A24);
  static const Color primary = Color(0xFF6366F1);
  static const Color primaryLight = Color(0xFF818CF8);
  static const Color success = Color(0xFF22C55E);
  static const Color warning = Color(0xFFEAB308);
  static const Color danger = Color(0xFFEF4444);
  static const Color text = Color(0xFFFAFAFA);
  static const Color textSecondary = Color(0xFFA1A1AA);
  static const Color border = Color(0xFF2A2A36);
  static const Color surfaceLight = Color(0xFF252533);

  /// Retourne la couleur du score selon la valeur (0-10)
  static Color scoreColor(double score) {
    if (score <= 3) return danger;
    if (score <= 5) return warning;
    if (score <= 7) return primary;
    return success;
  }

  /// Label du score en francais
  static String scoreLabel(double score) {
    if (score <= 2) return 'SUSPECT';
    if (score <= 4) return 'FAIBLE';
    if (score <= 6) return 'MOYEN';
    if (score <= 8) return 'BON';
    return 'EXCELLENT';
  }
}

class AppSpacing {
  AppSpacing._();

  static const double xs = 4;
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 20;
  static const double xxl = 24;
  static const double xxxl = 32;

  static const EdgeInsets pagePadding = EdgeInsets.symmetric(horizontal: 20);
  static const EdgeInsets cardPadding = EdgeInsets.all(16);
  static const double cardRadius = 16;
  static const double buttonRadius = 12;
  static const double inputRadius = 12;
}

class AppTextStyles {
  AppTextStyles._();

  /// Police monospace pour les chiffres/donnees
  static TextStyle dataNumber({
    double fontSize = 20,
    FontWeight fontWeight = FontWeight.w700,
    Color color = AppColors.text,
  }) {
    return GoogleFonts.jetBrainsMono(
      fontSize: fontSize,
      fontWeight: fontWeight,
      color: color,
    );
  }

  /// Police monospace pour les petits chiffres
  static TextStyle dataSmall({
    Color color = AppColors.text,
  }) {
    return GoogleFonts.jetBrainsMono(
      fontSize: 12,
      fontWeight: FontWeight.w500,
      color: color,
    );
  }

  /// Police monospace pour le score
  static TextStyle scoreValue({
    double fontSize = 24,
    Color color = AppColors.text,
  }) {
    return GoogleFonts.jetBrainsMono(
      fontSize: fontSize,
      fontWeight: FontWeight.w800,
      color: color,
    );
  }

  /// Label de section
  static TextStyle sectionLabel = GoogleFonts.inter(
    fontSize: 11,
    fontWeight: FontWeight.w600,
    color: AppColors.textSecondary,
    letterSpacing: 1.2,
  );
}
