import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:shimmer/shimmer.dart';
import '../core/constants.dart';
import '../core/api_service.dart';
import 'influencer_report_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? _stats;
  List<Map<String, dynamic>> _recent = [];
  bool _loadingStats = true;
  bool _loadingRecent = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _loadingStats = true;
      _loadingRecent = true;
    });
    await Future.wait([_loadStats(), _loadRecent()]);
  }

  Future<void> _loadStats() async {
    try {
      final data = await ApiService().getDashboardStats();
      if (mounted) setState(() { _stats = data; _loadingStats = false; });
    } catch (e) {
      if (mounted) setState(() => _loadingStats = false);
    }
  }

  Future<void> _loadRecent() async {
    try {
      final data = await ApiService().getDashboardRecent();
      if (mounted) setState(() { _recent = data; _loadingRecent = false; });
    } catch (e) {
      if (mounted) setState(() => _loadingRecent = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          color: AppColors.primary,
          backgroundColor: AppColors.surface,
          onRefresh: _loadData,
          child: CustomScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            slivers: [
              // ─── Header ─────────────────────────────
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 24, 20, 8),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Dashboard',
                        style: GoogleFonts.inter(
                          fontSize: 28,
                          fontWeight: FontWeight.w800,
                          color: AppColors.text,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Vue d\'ensemble de vos analyses',
                        style: GoogleFonts.inter(
                          fontSize: 14,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // ─── Stats Grid ─────────────────────────
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
                  child: _loadingStats ? _buildShimmerStats() : _buildStatsGrid(),
                ),
              ),

              // ─── Recent Header ──────────────────────
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 28, 20, 12),
                  child: Text('ANALYSES RECENTES', style: AppTextStyles.sectionLabel),
                ),
              ),

              // ─── Recent List ────────────────────────
              if (_loadingRecent)
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Column(
                      children: List.generate(
                        4,
                        (i) => Padding(
                          padding: const EdgeInsets.only(bottom: 10),
                          child: _shimmerCard(),
                        ),
                      ),
                    ),
                  ),
                )
              else if (_recent.isEmpty)
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 48),
                      decoration: BoxDecoration(
                        color: AppColors.surface,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: AppColors.border),
                      ),
                      child: Column(
                        children: [
                          Icon(
                            Icons.analytics_outlined,
                            size: 48,
                            color: AppColors.textSecondary.withValues(alpha: 0.5),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'Aucune analyse',
                            style: GoogleFonts.inter(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: AppColors.text,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Commencez par analyser un influenceur.',
                            style: GoogleFonts.inter(
                              fontSize: 14,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                )
              else
                SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, index) {
                      final item = _recent[index];
                      return Padding(
                        padding: const EdgeInsets.fromLTRB(20, 0, 20, 10),
                        child: _recentCard(item),
                      );
                    },
                    childCount: _recent.length,
                  ),
                ),

              const SliverToBoxAdapter(child: SizedBox(height: 100)),
            ],
          ),
        ),
      ),
    );
  }

  // ─── STATS GRID ──────────────────────────────────────────────
  Widget _buildStatsGrid() {
    final total = _stats?['total'] ?? _stats?['total_analyses'] ?? _stats?['total_analyzed'] ?? 0;
    final avgScore = (_stats?['avg_score'] ?? _stats?['average_score'] ?? _stats?['avg_overall_score'] ?? 0).toDouble();
    final avgEngagement = (_stats?['avg_engagement'] ?? _stats?['average_engagement'] ?? _stats?['avg_engagement_rate'] ?? 0).toDouble();
    final avgFake = (_stats?['avg_fake_followers'] ?? _stats?['average_fake'] ?? _stats?['avg_fake_followers_pct'] ?? 0).toDouble();

    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: _statTile(
                label: 'Total Analyses',
                value: total.toString(),
                icon: Icons.analytics_rounded,
                color: AppColors.primary,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _statTile(
                label: 'Score Moyen',
                value: avgScore.toStringAsFixed(1),
                icon: Icons.star_rounded,
                color: AppColors.scoreColor(avgScore),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _statTile(
                label: 'Engagement',
                value: '${avgEngagement.toStringAsFixed(1)}%',
                icon: Icons.favorite_rounded,
                color: AppColors.success,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _statTile(
                label: 'Faux Followers',
                value: '${avgFake.toStringAsFixed(0)}%',
                icon: Icons.person_off_rounded,
                color: AppColors.danger,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _statTile({
    required String label,
    required String value,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, size: 20, color: color),
          ),
          const SizedBox(height: 14),
          Text(
            value,
            style: AppTextStyles.dataNumber(
              fontSize: 22,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: GoogleFonts.inter(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  // ─── SHIMMER ─────────────────────────────────────────────────
  Widget _buildShimmerStats() {
    return Shimmer.fromColors(
      baseColor: AppColors.surface,
      highlightColor: AppColors.border,
      child: Column(
        children: [
          Row(
            children: [
              Expanded(child: _shimmerTile()),
              const SizedBox(width: 12),
              Expanded(child: _shimmerTile()),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(child: _shimmerTile()),
              const SizedBox(width: 12),
              Expanded(child: _shimmerTile()),
            ],
          ),
        ],
      ),
    );
  }

  Widget _shimmerTile() {
    return Container(
      height: 120,
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
      ),
    );
  }

  Widget _shimmerCard() {
    return Shimmer.fromColors(
      baseColor: AppColors.surface,
      highlightColor: AppColors.border,
      child: Container(
        height: 72,
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }

  // ─── RECENT CARD ─────────────────────────────────────────────
  Widget _recentCard(Map<String, dynamic> item) {
    final score = (item['overall_score'] ?? item['score'] ?? 0).toDouble();
    final platform = (item['platform'] ?? '').toString();
    final profilePic = item['profile_pic'] as String?;
    final username = (item['username'] ?? '').toString();
    final name = (item['name'] ?? item['full_name'] ?? username).toString();
    final date = (item['analyzed_at'] ?? item['created_at'] ?? '').toString();

    return GestureDetector(
      onTap: () {
        final id = item['id'];
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => InfluencerReportScreen(
              influencerId: id is int ? id : int.parse(id.toString()),
            ),
          ),
        );
      },
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppColors.border),
        ),
        child: Row(
          children: [
            // Avatar
            CircleAvatar(
              radius: 22,
              backgroundColor: AppColors.primary.withValues(alpha: 0.15),
              backgroundImage: profilePic != null && profilePic.isNotEmpty
                  ? NetworkImage(profilePic)
                  : null,
              child: profilePic == null || profilePic.isEmpty
                  ? Text(
                      username.isNotEmpty ? username[0].toUpperCase() : '?',
                      style: GoogleFonts.inter(
                        fontWeight: FontWeight.w700,
                        fontSize: 16,
                        color: AppColors.primary,
                      ),
                    )
                  : null,
            ),
            const SizedBox(width: 12),

            // Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppColors.text,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 3),
                  Row(
                    children: [
                      _platformBadge(platform),
                      const SizedBox(width: 8),
                      Flexible(
                        child: Text(
                          '@$username',
                          style: GoogleFonts.inter(
                            fontSize: 12,
                            color: AppColors.textSecondary,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      if (date.isNotEmpty) ...[
                        const SizedBox(width: 8),
                        Text(
                          _formatDate(date),
                          style: GoogleFonts.inter(
                            fontSize: 11,
                            color: AppColors.textSecondary.withValues(alpha: 0.6),
                          ),
                        ),
                      ],
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(width: 8),

            // Score badge
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(
                color: AppColors.scoreColor(score).withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                score.toStringAsFixed(1),
                style: AppTextStyles.dataSmall(
                  color: AppColors.scoreColor(score),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _platformBadge(String platform) {
    final isInstagram = platform.toLowerCase() == 'instagram';
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: (isInstagram ? Colors.pinkAccent : Colors.cyanAccent)
            .withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        isInstagram ? 'IG' : 'TT',
        style: GoogleFonts.jetBrainsMono(
          fontSize: 10,
          fontWeight: FontWeight.w700,
          color: isInstagram ? Colors.pinkAccent : Colors.cyanAccent,
        ),
      ),
    );
  }

  String _formatDate(String dateStr) {
    try {
      final date = DateTime.parse(dateStr);
      final now = DateTime.now();
      final diff = now.difference(date);
      if (diff.inMinutes < 60) return 'il y a ${diff.inMinutes}min';
      if (diff.inHours < 24) return 'il y a ${diff.inHours}h';
      if (diff.inDays < 7) return 'il y a ${diff.inDays}j';
      return '${date.day}/${date.month}/${date.year}';
    } catch (_) {
      return '';
    }
  }
}
