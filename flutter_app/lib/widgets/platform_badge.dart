import 'package:flutter/material.dart';
import '../core/constants.dart';

class PlatformBadge extends StatelessWidget {
  final String platform;

  const PlatformBadge({super.key, required this.platform});

  @override
  Widget build(BuildContext context) {
    final isInstagram = platform.toLowerCase() == 'instagram';
    final isTikTok = platform.toLowerCase() == 'tiktok';

    return Container(
      height: 28,
      padding: const EdgeInsets.symmetric(horizontal: 10),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(14),
        gradient: isInstagram
            ? const LinearGradient(
                colors: [
                  Color(0xFFF58529),
                  Color(0xFFDD2A7B),
                  Color(0xFF8134AF),
                ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              )
            : null,
        color: isInstagram
            ? null
            : isTikTok
                ? const Color(0xFF010101)
                : AppColors.surface,
        border: !isInstagram
            ? Border.all(color: AppColors.border, width: 1)
            : null,
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            _platformIcon,
            size: 14,
            color: isInstagram
                ? Colors.white
                : isTikTok
                    ? const Color(0xFF69C9D0)
                    : AppColors.textSecondary,
          ),
          const SizedBox(width: 4),
          Text(
            _platformLabel,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: isInstagram || isTikTok
                  ? Colors.white
                  : AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  IconData get _platformIcon {
    switch (platform.toLowerCase()) {
      case 'instagram':
        return Icons.camera_alt_rounded;
      case 'tiktok':
        return Icons.music_note_rounded;
      case 'youtube':
        return Icons.play_circle_rounded;
      case 'twitter':
      case 'x':
        return Icons.tag_rounded;
      default:
        return Icons.public_rounded;
    }
  }

  String get _platformLabel {
    switch (platform.toLowerCase()) {
      case 'instagram':
        return 'Instagram';
      case 'tiktok':
        return 'TikTok';
      case 'youtube':
        return 'YouTube';
      case 'twitter':
      case 'x':
        return 'X';
      default:
        return platform;
    }
  }
}
