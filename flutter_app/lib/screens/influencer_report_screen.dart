import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:shimmer/shimmer.dart';
import '../core/constants.dart';
import '../core/api_service.dart';
import '../widgets/score_badge.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════════

String formatNumber(num n) {
  if (n >= 1000000) return '${(n / 1000000).toStringAsFixed(1)}M';
  if (n >= 1000) return '${(n / 1000).toStringAsFixed(1)}K';
  return n.toString();
}

Color getScoreColor(double score) {
  if (score <= 3) return AppColors.danger;
  if (score <= 5) return AppColors.warning;
  if (score <= 7) return AppColors.primary;
  return AppColors.success;
}

String getScoreLabel(double score) {
  if (score <= 3) return 'SUSPECT';
  if (score <= 5) return 'FAIBLE';
  if (score <= 7) return 'MOYEN';
  if (score <= 9) return 'BON';
  return 'EXCELLENT';
}

String getVerdictTitle(double score) {
  if (score <= 3) return 'PRÉOCCUPANT';
  if (score <= 5) return 'ATTENTION';
  if (score <= 7) return 'CORRECT';
  return 'FIABLE';
}

String getVerdict(Map<String, dynamic> data) {
  final score = (data['score'] as num?)?.toDouble() ?? 0;
  final username = data['username'] as String? ?? 'cet influenceur';
  final engagement = (data['engagement_rate'] as num?)?.toDouble();
  final fakePct = (data['fake_followers_pct'] as num?)?.toDouble();

  final buf = StringBuffer();

  if (score <= 3) {
    buf.write(
        'Le profil de @$username présente des signaux très préoccupants. ');
    if (fakePct != null && fakePct > 50) {
      buf.write(
          'Plus de ${fakePct.round()}% des abonnés sont suspectés d\'être faux. ');
    }
    if (engagement != null && engagement < 1) {
      buf.write(
          'Le taux d\'engagement de ${engagement.toStringAsFixed(2)}% est anormalement bas. ');
    }
    buf.write(
        'Nous déconseillons fortement toute collaboration avec ce profil.');
  } else if (score <= 5) {
    buf.write('Le profil de @$username montre des indicateurs mitigés. ');
    if (fakePct != null) {
      buf.write(
          'Environ ${fakePct.round()}% des abonnés pourraient être artificiels. ');
    }
    buf.write(
        'Une vérification approfondie est recommandée avant toute collaboration.');
  } else if (score <= 7) {
    buf.write('Le profil de @$username est globalement correct. ');
    if (engagement != null) {
      buf.write(
          'Le taux d\'engagement de ${engagement.toStringAsFixed(2)}% est dans la moyenne. ');
    }
    buf.write(
        'Ce profil peut être envisagé pour une collaboration avec prudence.');
  } else {
    buf.write('Le profil de @$username est fiable et authentique. ');
    if (engagement != null) {
      buf.write(
          'Avec un taux d\'engagement de ${engagement.toStringAsFixed(2)}%, ');
    }
    if (fakePct != null) {
      buf.write(
          'et seulement ${fakePct.round()}% d\'abonnés suspects, ');
    }
    buf.write('ce profil est recommandé pour une collaboration.');
  }

  return buf.toString();
}

// ═══════════════════════════════════════════════════════════════════════════════
// Screen
// ═══════════════════════════════════════════════════════════════════════════════

class InfluencerReportScreen extends StatefulWidget {
  final int influencerId;
  const InfluencerReportScreen({super.key, required this.influencerId});

  @override
  State<InfluencerReportScreen> createState() => _InfluencerReportScreenState();
}

class _InfluencerReportScreenState extends State<InfluencerReportScreen> {
  Map<String, dynamic>? _data;
  bool _loading = true;
  String? _error;

  // ── Lifecycle ────────────────────────────────────────────────

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final data = await ApiService().getInfluencer(widget.influencerId);
      if (mounted) {
        setState(() {
          _data = data;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  // ── Data getters (null-safe) ─────────────────────────────────

  double get _score => (_data?['latest_snapshot']?['overall_score'] as num?)?.toDouble() ?? (_data?['overall_score'] as num?)?.toDouble() ?? (_data?['score'] as num?)?.toDouble() ?? 0;

  String get _name =>
      _data?['full_name'] as String? ??
      _data?['name'] as String? ??
      _data?['username'] as String? ??
      'Inconnu';

  String get _username => _data?['username'] as String? ?? '';

  String? get _profilePic =>
      _data?['profile_pic_url'] as String? ??
      _data?['profile_pic'] as String? ??
      _data?['avatar_url'] as String?;

  String get _platform => _data?['platform'] as String? ?? 'instagram';

  bool get _verified =>
      _data?['is_verified'] as bool? ?? _data?['verified'] as bool? ?? false;

  num get _followers => _data?['followers_count'] as num? ?? _data?['followers'] as num? ?? 0;
  num get _following => _data?['following_count'] as num? ?? _data?['following'] as num? ?? 0;

  num get _posts =>
      _data?['posts_count'] as num? ??
      _data?['posts'] as num? ??
      _data?['media_count'] as num? ??
      0;

  double get _engagementRate =>
      (_data?['latest_snapshot']?['engagement_rate'] as num?)?.toDouble() ?? (_data?['engagement_rate'] as num?)?.toDouble() ?? 0;

  double get _fakePct =>
      (_data?['latest_snapshot']?['fake_followers_pct'] as num?)?.toDouble() ?? (_data?['fake_followers_pct'] as num?)?.toDouble() ?? 0;

  String get _zone =>
      _data?['zone_operation'] as String? ?? _data?['zone'] as String? ?? _data?['location'] as String? ?? 'Algérie';

  Map<String, dynamic>? get _demographics =>
      _data?['latest_snapshot']?['audience_demographic'] as Map<String, dynamic>? ?? _data?['demographics'] as Map<String, dynamic>?;

  // ── Build ────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new, size: 20),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text(_loading ? 'Chargement...' : _name),
        actions: [
          IconButton(
            icon: const Icon(Icons.share_outlined),
            tooltip: 'Partager',
            onPressed: _data == null ? null : () {},
          ),
          IconButton(
            icon: const Icon(Icons.download_outlined),
            tooltip: 'Exporter',
            onPressed: _data == null ? null : () {},
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading) return _buildShimmer();
    if (_error != null) return _buildError();
    return _buildContent();
  }

  // ── Error state ──────────────────────────────────────────────

  Widget _buildError() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, color: AppColors.danger, size: 56),
            const SizedBox(height: 16),
            Text(
              'Erreur de chargement',
              style: GoogleFonts.inter(
                color: AppColors.text,
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _error ?? '',
              textAlign: TextAlign.center,
              style: GoogleFonts.inter(
                color: AppColors.textSecondary,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _loadData,
              icon: const Icon(Icons.refresh),
              label: const Text('Réessayer'),
            ),
          ],
        ),
      ),
    );
  }

  // ── Shimmer loading state ────────────────────────────────────

  Widget _buildShimmer() {
    return Shimmer.fromColors(
      baseColor: AppColors.surface,
      highlightColor: AppColors.border,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        physics: const NeverScrollableScrollPhysics(),
        child: Column(
          children: [
            _shimmerBox(100),
            const SizedBox(height: 16),
            _shimmerBox(160),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(child: _shimmerBox(80)),
                const SizedBox(width: 12),
                Expanded(child: _shimmerBox(80)),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: _shimmerBox(80)),
                const SizedBox(width: 12),
                Expanded(child: _shimmerBox(80)),
              ],
            ),
            const SizedBox(height: 16),
            _shimmerBox(200),
            const SizedBox(height: 16),
            _shimmerBox(260),
            const SizedBox(height: 16),
            _shimmerBox(220),
            const SizedBox(height: 16),
            _shimmerBox(120),
          ],
        ),
      ),
    );
  }

  Widget _shimmerBox(double height) {
    return Container(
      height: height,
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSpacing.cardRadius),
      ),
    );
  }

  // ── Main content ─────────────────────────────────────────────

  Widget _buildContent() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildProfileHeader(),
          const SizedBox(height: 16),
          _buildScoreSection(),
          const SizedBox(height: 16),
          _buildStatsGrid(),
          const SizedBox(height: 16),
          _buildEngagementCard(),
          const SizedBox(height: 16),
          _buildFakeFollowersCard(),
          const SizedBox(height: 16),
          _buildDemographicsCard(),
          const SizedBox(height: 16),
          _buildZoneCard(),
          const SizedBox(height: 16),
          _buildVerdictCard(),
          const SizedBox(height: 24),
          _buildActionButtons(),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // B. Profile Header
  // ═════════════════════════════════════════════════════════════════════════════

  Widget _buildProfileHeader() {
    return _card(
      child: Row(
        children: [
          // Avatar
          _profilePic != null && _profilePic!.isNotEmpty
              ? ClipOval(
                  child: CachedNetworkImage(
                    imageUrl: _profilePic!,
                    width: 56,
                    height: 56,
                    fit: BoxFit.cover,
                    placeholder: (_, __) => _avatarFallback(),
                    errorWidget: (_, __, ___) => _avatarFallback(),
                  ),
                )
              : _avatarFallback(),
          const SizedBox(width: 16),
          // Info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Flexible(
                      child: Text(
                        _name,
                        style: GoogleFonts.inter(
                          color: AppColors.text,
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    if (_verified) ...[
                      const SizedBox(width: 6),
                      const Icon(Icons.verified,
                          color: Color(0xFF3B82F6), size: 18),
                    ],
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  '@$_username',
                  style: GoogleFonts.inter(
                    color: AppColors.textSecondary,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 6,
                  children: [
                    _platformBadge(_platform),
                    if (_zone.isNotEmpty)
                      _chipTag(Icons.location_on_outlined, _zone),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _avatarFallback() {
    final letter = _name.isNotEmpty ? _name[0].toUpperCase() : '?';
    return Container(
      width: 56,
      height: 56,
      decoration: const BoxDecoration(
        shape: BoxShape.circle,
        color: AppColors.primary,
      ),
      alignment: Alignment.center,
      child: Text(
        letter,
        style: GoogleFonts.inter(
          color: Colors.white,
          fontSize: 22,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  Widget _platformBadge(String platform) {
    final label = platform.isNotEmpty
        ? platform[0].toUpperCase() + platform.substring(1)
        : 'Social';
    IconData icon;
    switch (platform.toLowerCase()) {
      case 'instagram':
        icon = Icons.camera_alt_outlined;
      case 'tiktok':
        icon = Icons.music_note_outlined;
      case 'youtube':
        icon = Icons.play_circle_outline;
      case 'facebook':
        icon = Icons.facebook_outlined;
      default:
        icon = Icons.public;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: AppColors.primary.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.primary.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: AppColors.primary),
          const SizedBox(width: 4),
          Text(
            label,
            style: GoogleFonts.inter(
              color: AppColors.primary,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _chipTag(IconData icon, String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: AppColors.textSecondary),
          const SizedBox(width: 4),
          Text(
            text,
            style: GoogleFonts.inter(
              color: AppColors.textSecondary,
              fontSize: 11,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // C. Score Section
  // ═════════════════════════════════════════════════════════════════════════════

  Widget _buildScoreSection() {
    return _card(
      child: Column(
        children: [
          Text(
            'Score de Fiabilité',
            style: GoogleFonts.inter(
              color: AppColors.textSecondary,
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 16),
          ScoreBadge(score: _score, size: 100, showLabel: true),
        ],
      ),
    );
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // D. Stats Grid (2x2)
  // ═════════════════════════════════════════════════════════════════════════════

  Widget _buildStatsGrid() {
    return Column(
      children: [
        Row(
          children: [
            Expanded(child: _statCard('Abonnés', formatNumber(_followers))),
            const SizedBox(width: 12),
            Expanded(
                child: _statCard('Abonnements', formatNumber(_following))),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
                child: _statCard('Publications', formatNumber(_posts))),
            const SizedBox(width: 12),
            Expanded(
              child: _statCard(
                'Engagement',
                '${_engagementRate.toStringAsFixed(2)}%',
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _statCard(String label, String value) {
    return _card(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
      child: Column(
        children: [
          Text(value, style: AppTextStyles.dataNumber()),
          const SizedBox(height: 4),
          Text(
            label,
            style: GoogleFonts.inter(
              color: AppColors.textSecondary,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // E1. Engagement Card
  // ═════════════════════════════════════════════════════════════════════════════

  Widget _buildEngagementCard() {
    final engagement = _data?['engagement'] as Map<String, dynamic>?;
    final likes = (engagement?['likes'] as num?)?.toDouble();
    final comments = (engagement?['comments'] as num?)?.toDouble();
    final shares = (engagement?['shares'] as num?)?.toDouble();
    final hasBreakdown = likes != null || comments != null || shares != null;

    return _card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _sectionHeader(Icons.trending_up, 'Engagement'),
          const SizedBox(height: 16),
          Center(
            child: Column(
              children: [
                Text(
                  '${_engagementRate.toStringAsFixed(2)}%',
                  style: AppTextStyles.scoreValue(
                    fontSize: 36,
                    color: AppColors.primary,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Taux d\'engagement',
                  style: GoogleFonts.inter(
                    color: AppColors.textSecondary,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
          if (hasBreakdown) ...[
            const SizedBox(height: 20),
            const Divider(color: AppColors.border),
            const SizedBox(height: 16),
            if (likes != null) _barRow('Likes', likes, AppColors.primary),
            if (comments != null)
              _barRow('Commentaires', comments, AppColors.success),
            if (shares != null)
              _barRow('Partages', shares, AppColors.warning),
          ],
        ],
      ),
    );
  }

  Widget _barRow(String label, double value, Color color) {
    final pct = (value / 100).clamp(0.0, 1.0);
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                label,
                style: GoogleFonts.inter(
                  color: AppColors.textSecondary,
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                '${value.toStringAsFixed(1)}%',
                style: AppTextStyles.dataSmall(),
              ),
            ],
          ),
          const SizedBox(height: 6),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: Stack(
              children: [
                Container(
                  height: 6,
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
                FractionallySizedBox(
                  widthFactor: pct,
                  child: Container(
                    height: 6,
                    decoration: BoxDecoration(
                      color: color,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // E2. Faux Abonnés Card (PieChart)
  // ═════════════════════════════════════════════════════════════════════════════

  Widget _buildFakeFollowersCard() {
    final fake = _fakePct;
    final real = (100 - fake).clamp(0.0, 100.0);
    final suspect = fake * 0.6;
    final bot = fake * 0.4;

    return _card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _sectionHeader(Icons.people_outline, 'Faux Abonnés'),
          const SizedBox(height: 16),
          SizedBox(
            height: 180,
            child: PieChart(
              PieChartData(
                sectionsSpace: 2,
                centerSpaceRadius: 40,
                sections: [
                  PieChartSectionData(
                    value: real,
                    color: AppColors.success,
                    title: '${real.round()}%',
                    titleStyle: GoogleFonts.jetBrainsMono(
                      color: Colors.white,
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                    ),
                    radius: 45,
                  ),
                  PieChartSectionData(
                    value: suspect,
                    color: AppColors.warning,
                    title: suspect >= 1 ? '${suspect.round()}%' : '',
                    titleStyle: GoogleFonts.jetBrainsMono(
                      color: Colors.white,
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                    ),
                    radius: 45,
                  ),
                  PieChartSectionData(
                    value: bot,
                    color: AppColors.danger,
                    title: bot >= 1 ? '${bot.round()}%' : '',
                    titleStyle: GoogleFonts.jetBrainsMono(
                      color: Colors.white,
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                    ),
                    radius: 45,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _legendDot(AppColors.success, 'Réels', '${real.round()}%'),
              _legendDot(
                  AppColors.warning, 'Suspects', '${suspect.round()}%'),
              _legendDot(AppColors.danger, 'Bots', '${bot.round()}%'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _legendDot(Color color, String label, String value) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 6),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: GoogleFonts.inter(
                color: AppColors.textSecondary,
                fontSize: 11,
                fontWeight: FontWeight.w500,
              ),
            ),
            Text(value, style: AppTextStyles.dataSmall()),
          ],
        ),
      ],
    );
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // E3. Démographie Card
  // ═════════════════════════════════════════════════════════════════════════════

  Widget _buildDemographicsCard() {
    final demo = _demographics;

    // Extraire les tranches d'age
    final ageData = <String, double>{};
    if (demo != null) {
      for (final key in demo.keys) {
        if (key.startsWith('age_')) {
          final rawLabel = key.replaceFirst('age_', '').replaceAll('_pct', '').replaceAll('_', '-').replaceAll('plus', '+');
          final label = '$rawLabel ans';
          ageData[label] = (demo[key] as num?)?.toDouble() ?? 0;
        }
      }
    }

    final male = (demo?['estimated_male_pct'] as num?)?.toDouble() ??
        (demo?['male'] as num?)?.toDouble() ??
        (demo?['gender_male'] as num?)?.toDouble();
    final female = (demo?['estimated_female_pct'] as num?)?.toDouble() ??
        (demo?['female'] as num?)?.toDouble() ??
        (demo?['gender_female'] as num?)?.toDouble();

    final countries = demo?['top_countries'] as List<dynamic>?;
    final cities = demo?['top_cities'] as List<dynamic>?;

    final hasData = ageData.isNotEmpty ||
        male != null ||
        countries != null ||
        cities != null;

    return _card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _sectionHeader(Icons.bar_chart, 'Démographie'),
          if (!hasData) ...[
            const SizedBox(height: 16),
            Center(
              child: Text(
                'Données démographiques non disponibles',
                style: GoogleFonts.inter(
                  color: AppColors.textSecondary,
                  fontSize: 13,
                ),
              ),
            ),
          ],
          // Répartition par âge
          if (ageData.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text(
              'Répartition par âge',
              style: GoogleFonts.inter(
                color: AppColors.textSecondary,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 10),
            ...ageData.entries.map((e) => _demoBar(e.key, e.value)),
          ],
          // Genre
          if (male != null && female != null) ...[
            const SizedBox(height: 20),
            Text(
              'Répartition par genre',
              style: GoogleFonts.inter(
                color: AppColors.textSecondary,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 10),
            _genderBar(male, female),
          ],
          // Pays
          if (countries != null && countries.isNotEmpty) ...[
            const SizedBox(height: 20),
            Text(
              'Pays principaux',
              style: GoogleFonts.inter(
                color: AppColors.textSecondary,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 6,
              children: countries.take(5).map((c) {
                final name =
                    c is Map ? (c['country'] ?? c['name'] ?? c.toString()) : c.toString();
                return _chipTag(Icons.flag_outlined, name.toString());
              }).toList(),
            ),
          ],
          // Villes
          if (cities != null && cities.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text(
              'Villes principales',
              style: GoogleFonts.inter(
                color: AppColors.textSecondary,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 6,
              children: cities.take(5).map((c) {
                final name =
                    c is Map ? (c['country'] ?? c['name'] ?? c.toString()) : c.toString();
                return _chipTag(
                    Icons.location_city_outlined, name.toString());
              }).toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _demoBar(String label, double pct) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(
        children: [
          SizedBox(
            width: 56,
            child: Text(
              label,
              style: GoogleFonts.inter(
                color: AppColors.textSecondary,
                fontSize: 12,
              ),
            ),
          ),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(4),
              child: Stack(
                children: [
                  Container(
                    height: 8,
                    decoration: BoxDecoration(
                      color: AppColors.primary.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                  FractionallySizedBox(
                    widthFactor: (pct / 100).clamp(0.0, 1.0),
                    child: Container(
                      height: 8,
                      decoration: BoxDecoration(
                        color: AppColors.primary,
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(
            width: 40,
            child: Text(
              '${pct.round()}%',
              textAlign: TextAlign.right,
              style: AppTextStyles.dataSmall(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _genderBar(double male, double female) {
    final total = male + female;
    final malePct = total > 0 ? male / total : 0.5;
    return Column(
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(6),
          child: SizedBox(
            height: 12,
            child: Row(
              children: [
                Expanded(
                  flex: (malePct * 100).round().clamp(1, 99),
                  child: Container(color: const Color(0xFF3B82F6)),
                ),
                Expanded(
                  flex: ((1 - malePct) * 100).round().clamp(1, 99),
                  child: Container(color: const Color(0xFFEC4899)),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            _genderLabel(const Color(0xFF3B82F6), 'Hommes', male),
            _genderLabel(const Color(0xFFEC4899), 'Femmes', female),
          ],
        ),
      ],
    );
  }

  Widget _genderLabel(Color color, String label, double pct) {
    return Row(
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 6),
        Text(
          '$label ${pct.round()}%',
          style: GoogleFonts.inter(
            color: AppColors.textSecondary,
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // E4. Zone d'Opération Card
  // ═════════════════════════════════════════════════════════════════════════════

  Widget _buildZoneCard() {
    final languages = _data?['languages'] as List<dynamic>?;

    return _card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _sectionHeader(Icons.map_outlined, 'Zone d\'Opération'),
          const SizedBox(height: 16),
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.location_on,
                    color: AppColors.primary, size: 22),
              ),
              const SizedBox(width: 12),
              Text(
                _zone,
                style: GoogleFonts.inter(
                  color: AppColors.text,
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            'Langues',
            style: GoogleFonts.inter(
              color: AppColors.textSecondary,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 6,
            children: (languages != null && languages.isNotEmpty)
                ? languages
                    .map((l) => _languageChip(l.toString()))
                    .toList()
                : [_languageChip('Arabe'), _languageChip('Français')],
          ),
        ],
      ),
    );
  }

  Widget _languageChip(String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.border),
      ),
      child: Text(
        text,
        style: GoogleFonts.inter(
          color: AppColors.text,
          fontSize: 12,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // F. Verdict Section
  // ═════════════════════════════════════════════════════════════════════════════

  Widget _buildVerdictCard() {
    final color = getScoreColor(_score);
    final title = getVerdictTitle(_score);
    final verdict = getVerdict({...?_data, "score": _score, "engagement_rate": _engagementRate, "fake_followers_pct": _fakePct, "username": _username});

    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSpacing.cardRadius),
        border: Border.all(color: AppColors.border),
      ),
      clipBehavior: Clip.antiAlias,
      child: IntrinsicHeight(
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Container(width: 4, color: color),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.gavel, color: color, size: 20),
                        const SizedBox(width: 8),
                        Text(
                          'Verdict : $title',
                          style: GoogleFonts.inter(
                            color: color,
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text(
                      verdict,
                      style: GoogleFonts.inter(
                        color: AppColors.textSecondary,
                        fontSize: 14,
                        height: 1.5,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // G. Action Buttons
  // ═════════════════════════════════════════════════════════════════════════════

  Widget _buildActionButtons() {
    return Row(
      children: [
        Expanded(
          child: OutlinedButton.icon(
            onPressed: _confirmDelete,
            icon: const Icon(Icons.delete_outline, color: AppColors.danger),
            label: Text(
              'Supprimer',
              style: GoogleFonts.inter(
                color: AppColors.danger,
                fontWeight: FontWeight.w600,
              ),
            ),
            style: OutlinedButton.styleFrom(
              side: const BorderSide(color: AppColors.danger),
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                borderRadius:
                    BorderRadius.circular(AppSpacing.buttonRadius),
              ),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: OutlinedButton.icon(
            onPressed: () {},
            icon:
                const Icon(Icons.share_outlined, color: AppColors.primary),
            label: Text(
              'Partager',
              style: GoogleFonts.inter(
                color: AppColors.primary,
                fontWeight: FontWeight.w600,
              ),
            ),
            style: OutlinedButton.styleFrom(
              side: const BorderSide(color: AppColors.primary),
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                borderRadius:
                    BorderRadius.circular(AppSpacing.buttonRadius),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _confirmDelete() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.cardRadius),
        ),
        title: Text(
          'Supprimer cet influenceur ?',
          style: GoogleFonts.inter(
            color: AppColors.text,
            fontSize: 18,
            fontWeight: FontWeight.w700,
          ),
        ),
        content: Text(
          'Cette action est irréversible. Toutes les données d\'analyse seront supprimées.',
          style: GoogleFonts.inter(
            color: AppColors.textSecondary,
            fontSize: 14,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text(
              'Annuler',
              style: GoogleFonts.inter(color: AppColors.textSecondary),
            ),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: Text(
              'Supprimer',
              style: GoogleFonts.inter(color: AppColors.danger),
            ),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      try {
        await ApiService().deleteInfluencer(widget.influencerId);
        if (mounted) {
          Navigator.of(context).pop(true);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Influenceur supprimé')),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Erreur : $e')),
          );
        }
      }
    }
  }

  // ═════════════════════════════════════════════════════════════════════════════
  // Shared UI components
  // ═════════════════════════════════════════════════════════════════════════════

  Widget _card({required Widget child, EdgeInsets? padding}) {
    return Container(
      padding: padding ?? const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppSpacing.cardRadius),
        border: Border.all(color: AppColors.border),
      ),
      child: child,
    );
  }

  Widget _sectionHeader(IconData icon, String title) {
    return Row(
      children: [
        Icon(icon, color: AppColors.primary, size: 20),
        const SizedBox(width: 8),
        Text(
          title,
          style: GoogleFonts.inter(
            color: AppColors.text,
            fontSize: 16,
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }
}
