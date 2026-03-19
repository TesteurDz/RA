import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../core/constants.dart';

class ScoreBadge extends StatelessWidget {
  final double score;
  final double size;
  final bool showLabel;

  const ScoreBadge({
    super.key,
    required this.score,
    this.size = 60,
    this.showLabel = true,
  });

  @override
  Widget build(BuildContext context) {
    final color = AppColors.scoreColor(score);
    final label = AppColors.scoreLabel(score);
    final clampedScore = score.clamp(0.0, 10.0);

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        TweenAnimationBuilder<double>(
          tween: Tween(begin: 0, end: clampedScore / 10),
          duration: const Duration(milliseconds: 1200),
          curve: Curves.easeOutCubic,
          builder: (context, value, child) {
            return SizedBox(
              width: size,
              height: size,
              child: CustomPaint(
                painter: _ScoreRingPainter(
                  progress: value,
                  color: color,
                  strokeWidth: size * 0.08,
                ),
                child: Center(
                  child: Text(
                    clampedScore.toStringAsFixed(1),
                    style: AppTextStyles.scoreValue(
                      fontSize: size * 0.32,
                      color: color,
                    ),
                  ),
                ),
              ),
            );
          },
        ),
        if (showLabel) ...[
          SizedBox(height: size * 0.1),
          Text(
            label,
            style: AppTextStyles.dataSmall(color: color).copyWith(
              fontSize: size * 0.15,
              fontWeight: FontWeight.w700,
              letterSpacing: 1.5,
            ),
          ),
        ],
      ],
    );
  }
}

class _ScoreRingPainter extends CustomPainter {
  final double progress;
  final Color color;
  final double strokeWidth;

  _ScoreRingPainter({
    required this.progress,
    required this.color,
    required this.strokeWidth,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width - strokeWidth) / 2;

    // Fond du cercle
    final bgPaint = Paint()
      ..color = color.withValues(alpha: 0.12)
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, bgPaint);

    // Arc de progression
    final fgPaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2,
      2 * math.pi * progress,
      false,
      fgPaint,
    );
  }

  @override
  bool shouldRepaint(_ScoreRingPainter oldDelegate) =>
      oldDelegate.progress != progress || oldDelegate.color != color;
}
