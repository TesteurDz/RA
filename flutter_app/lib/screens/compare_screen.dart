import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:shimmer/shimmer.dart';
import '../core/constants.dart';
import '../core/api_service.dart';


class CompareScreen extends StatefulWidget {
  const CompareScreen({super.key});

  @override
  State<CompareScreen> createState() => _CompareScreenState();
}

class _CompareScreenState extends State<CompareScreen> {
  List<Map<String, dynamic>> _allInfluencers = [];
  final List<Map<String, dynamic>> _selectedInfluencers = [];
  Map<String, dynamic>? _comparisonResult;
  bool _loadingInfluencers = true;
  bool _comparing = false;

  @override
  void initState() {
    super.initState();
    _loadInfluencers();
  }

  Future<void> _loadInfluencers() async {
    try {
      final data = await ApiService().getInfluencers();
      if (mounted) {
        setState(() {
          _allInfluencers = data;
          _loadingInfluencers = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _loadingInfluencers = false);
    }
  }

  Future<void> _compare() async {
    if (_selectedInfluencers.length < 2) return;

    setState(() {
      _comparing = true;
      _comparisonResult = null;
    });

    try {
      final ids = _selectedInfluencers
          .map((e) {
            final id = e['id'];
            return id is int ? id : int.parse(id.toString());
          })
          .toList();
      final result = await ApiService().compareInfluencers(ids);
      if (mounted) setState(() { _comparisonResult = result; _comparing = false; });
    } catch (e) {
      if (mounted) {
        setState(() => _comparing = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Erreur lors de la comparaison',
              style: GoogleFonts.inter(color: Colors.white),
            ),
            backgroundColor: AppColors.danger,
          ),
        );
      }
    }
  }

  void _addInfluencer() {
    if (_selectedInfluencers.length >= 4) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Maximum 4 influenceurs',
            style: GoogleFonts.inter(color: Colors.white),
          ),
          backgroundColor: AppColors.warning,
        ),
      );
      return;
    }

    final available = _allInfluencers
        .where((inf) => !_selectedInfluencers.any((s) => s['id'] == inf['id']))
        .toList();

    if (available.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Aucun influenceur disponible',
            style: GoogleFonts.inter(color: Colors.white),
          ),
          backgroundColor: AppColors.textSecondary,
        ),
      );
      return;
    }

    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Container(
          constraints: BoxConstraints(
            maxHeight: MediaQuery.of(context).size.height * 0.5,
          ),
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: AppColors.border,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'Choisir un influenceur',
                style: GoogleFonts.inter(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: AppColors.text,
                ),
              ),
              const SizedBox(height: 12),
              Flexible(
                child: ListView.separated(
                  shrinkWrap: true,
                  itemCount: available.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (_, i) {
                    final inf = available[i];
                    final username = (inf['username'] ?? '').toString();
                    final platform = (inf['platform'] ?? '').toString();
                    final score = (inf['score'] ?? 0).toDouble();

                    return ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: CircleAvatar(
                        radius: 18,
                        backgroundColor:
                            AppColors.primary.withValues(alpha: 0.15),
                        child: Text(
                          username.isNotEmpty ? username[0].toUpperCase() : '?',
                          style: GoogleFonts.inter(
                            fontWeight: FontWeight.w700,
                            color: AppColors.primary,
                            fontSize: 14,
                          ),
                        ),
                      ),
                      title: Text(
                        '@$username',
                        style: GoogleFonts.inter(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: AppColors.text,
                        ),
                      ),
                      subtitle: Text(
                        platform.toUpperCase(),
                        style: GoogleFonts.inter(
                          fontSize: 11,
                          color: AppColors.textSecondary,
                        ),
                      ),
                      trailing: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: AppColors.scoreColor(score)
                              .withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          score.toStringAsFixed(1),
                          style: AppTextStyles.dataSmall(
                            color: AppColors.scoreColor(score),
                          ),
                        ),
                      ),
                      onTap: () {
                        Navigator.pop(ctx);
                        setState(() {
                          _selectedInfluencers.add(inf);
                          _comparisonResult = null;
                        });
                      },
                    );
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  String _formatFollowers(dynamic count) {
    if (count == null) return '—';
    final n = count is int ? count : int.tryParse(count.toString()) ?? 0;
    if (n >= 1000000) return '${(n / 1000000).toStringAsFixed(1)}M';
    if (n >= 1000) return '${(n / 1000).toStringAsFixed(1)}K';
    return n.toString();
  }

  List<double> _extractValues(double Function(Map<String, dynamic>) extractor) {
    return _selectedInfluencers.map(extractor).toList();
  }

  int? _findBestIndex() {
    if (_selectedInfluencers.length < 2) return null;
    double best = -1;
    int bestIdx = 0;
    for (int i = 0; i < _selectedInfluencers.length; i++) {
      final score = (_selectedInfluencers[i]['score'] ?? 0).toDouble();
      if (score > best) {
        best = score;
        bestIdx = i;
      }
    }
    return bestIdx;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 24, 20, 100),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ─── Header ─────────────────────────────
              Text(
                'Comparer',
                style: GoogleFonts.inter(
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                  color: AppColors.text,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Comparez jusqu\'a 4 influenceurs',
                style: GoogleFonts.inter(
                  fontSize: 14,
                  color: AppColors.textSecondary,
                ),
              ),
              const SizedBox(height: 24),

              // ─── Not enough influencers ─────────────
              if (_loadingInfluencers)
                _buildLoadingState()
              else if (_allInfluencers.length < 2)
                _buildNotEnoughState()
              else ...[
                // Selected influencers chips
                _buildSelectedChips(),
                const SizedBox(height: 16),

                // Add button
                if (_selectedInfluencers.length < 4)
                  GestureDetector(
                    onTap: _addInfluencer,
                    child: Container(
                      height: 48,
                      decoration: BoxDecoration(
                        color: AppColors.surface,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: AppColors.border,
                          style: BorderStyle.solid,
                        ),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.add_rounded,
                              color: AppColors.primary, size: 20),
                          const SizedBox(width: 8),
                          Text(
                            'Ajouter un influenceur',
                            style: GoogleFonts.inter(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: AppColors.primary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                const SizedBox(height: 20),

                // Compare button
                if (_selectedInfluencers.length >= 2)
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton(
                      onPressed: _comparing ? null : _compare,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        disabledBackgroundColor:
                            AppColors.primary.withValues(alpha: 0.3),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                      child: _comparing
                          ? const SizedBox(
                              width: 24,
                              height: 24,
                              child: CircularProgressIndicator(
                                strokeWidth: 2.5,
                                color: Colors.white,
                              ),
                            )
                          : Text(
                              'Comparer',
                              style: GoogleFonts.inter(
                                fontSize: 16,
                                fontWeight: FontWeight.w700,
                                color: Colors.white,
                              ),
                            ),
                    ),
                  ),
                const SizedBox(height: 24),

                // Comparison results
                if (_comparisonResult != null || _selectedInfluencers.length >= 2)
                  _buildComparisonCards(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLoadingState() {
    return Shimmer.fromColors(
      baseColor: AppColors.surface,
      highlightColor: AppColors.border,
      child: Column(
        children: List.generate(
          3,
          (i) => Padding(
            padding: const EdgeInsets.only(bottom: 10),
            child: Container(
              height: 56,
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildNotEnoughState() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 48),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Center(
        child: Column(
          children: [
            Icon(
              Icons.compare_arrows_rounded,
              size: 48,
              color: AppColors.textSecondary.withValues(alpha: 0.5),
            ),
            const SizedBox(height: 16),
            Text(
              'Pas assez de donnees',
              style: GoogleFonts.inter(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: AppColors.text,
              ),
            ),
            const SizedBox(height: 4),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: Text(
                'Analysez au moins 2 influenceurs pour pouvoir les comparer.',
                textAlign: TextAlign.center,
                style: GoogleFonts.inter(
                  fontSize: 14,
                  color: AppColors.textSecondary,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSelectedChips() {
    if (_selectedInfluencers.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.border),
        ),
        child: Center(
          child: Text(
            'Selectionnez des influenceurs a comparer',
            style: GoogleFonts.inter(
              fontSize: 14,
              color: AppColors.textSecondary,
            ),
          ),
        ),
      );
    }

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: _selectedInfluencers.map((inf) {
        final username = (inf['username'] ?? '').toString();
        final platform = (inf['platform'] ?? '').toString();
        return Container(
          padding: const EdgeInsets.fromLTRB(12, 8, 4, 8),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: AppColors.primary.withValues(alpha: 0.3)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircleAvatar(
                radius: 12,
                backgroundColor: AppColors.primary.withValues(alpha: 0.15),
                child: Text(
                  username.isNotEmpty ? username[0].toUpperCase() : '?',
                  style: GoogleFonts.inter(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                    color: AppColors.primary,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Text(
                '@$username',
                style: GoogleFonts.inter(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: AppColors.text,
                ),
              ),
              const SizedBox(width: 4),
              _platformBadge(platform),
              IconButton(
                icon: const Icon(Icons.close_rounded, size: 16),
                color: AppColors.textSecondary,
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(
                  minWidth: 28,
                  minHeight: 28,
                ),
                onPressed: () {
                  setState(() {
                    _selectedInfluencers.remove(inf);
                    _comparisonResult = null;
                  });
                },
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildComparisonCards() {
    final bestIdx = _findBestIndex();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('COMPARAISON', style: AppTextStyles.sectionLabel),
        const SizedBox(height: 12),

        // Metric rows
        _comparisonMetric(
          'Score',
          _extractValues((e) => (e['score'] ?? 0).toDouble()),
          (v) => v.toStringAsFixed(1),
          bestIdx,
          higherIsBetter: true,
        ),
        const SizedBox(height: 8),
        _comparisonMetric(
          'Followers',
          _extractValues((e) => (e['followers'] ?? e['followers_count'] ?? 0).toDouble()),
          (v) => _formatFollowers(v.toInt()),
          bestIdx,
          higherIsBetter: true,
        ),
        const SizedBox(height: 8),
        _comparisonMetric(
          'Engagement',
          _extractValues((e) => (e['engagement_rate'] ?? e['engagement'] ?? 0).toDouble()),
          (v) => '${v.toStringAsFixed(1)}%',
          bestIdx,
          higherIsBetter: true,
        ),
        const SizedBox(height: 8),
        _comparisonMetric(
          'Faux %',
          _extractValues((e) => (e['fake_followers'] ?? e['fake_percentage'] ?? 0).toDouble()),
          (v) => '${v.toStringAsFixed(0)}%',
          bestIdx,
          higherIsBetter: false,
        ),

        if (bestIdx != null) ...[
          const SizedBox(height: 24),
          _bestChoiceCard(bestIdx),
        ],
      ],
    );
  }

  Widget _comparisonMetric(
    String label,
    List<double> values,
    String Function(double) formatter,
    int? bestIdx, {
    bool higherIsBetter = true,
  }) {
    // Find best value for this specific metric
    int? metricBestIdx;
    if (values.isNotEmpty) {
      double bestVal = values[0];
      metricBestIdx = 0;
      for (int i = 1; i < values.length; i++) {
        if (higherIsBetter ? values[i] > bestVal : values[i] < bestVal) {
          bestVal = values[i];
          metricBestIdx = i;
        }
      }
    }

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: GoogleFonts.inter(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 10),
          Row(
            children: List.generate(_selectedInfluencers.length, (i) {
              final isBest = metricBestIdx == i;
              final username =
                  (_selectedInfluencers[i]['username'] ?? '').toString();
              return Expanded(
                child: Padding(
                  padding: EdgeInsets.only(
                      right: i < _selectedInfluencers.length - 1 ? 8 : 0),
                  child: Column(
                    children: [
                      Text(
                        formatter(values[i]),
                        style: AppTextStyles.dataNumber(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: isBest ? AppColors.success : AppColors.text,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '@$username',
                        style: GoogleFonts.inter(
                          fontSize: 10,
                          color: AppColors.textSecondary,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      if (isBest) ...[
                        const SizedBox(height: 2),
                        Container(
                          width: 6,
                          height: 6,
                          decoration: const BoxDecoration(
                            color: AppColors.success,
                            shape: BoxShape.circle,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              );
            }),
          ),
        ],
      ),
    );
  }

  Widget _bestChoiceCard(int bestIdx) {
    final best = _selectedInfluencers[bestIdx];
    final username = (best['username'] ?? '').toString();
    final score = (best['score'] ?? 0).toDouble();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.success.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppColors.success.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: AppColors.success.withValues(alpha: 0.15),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.emoji_events_rounded,
                color: AppColors.success, size: 24),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Meilleur choix',
                  style: GoogleFonts.inter(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: AppColors.success,
                    letterSpacing: 0.5,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  '@$username',
                  style: GoogleFonts.inter(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: AppColors.text,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: AppColors.scoreColor(score).withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              score.toStringAsFixed(1),
              style: AppTextStyles.scoreValue(
                fontSize: 18,
                color: AppColors.scoreColor(score),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _platformBadge(String platform) {
    final isInstagram = platform.toLowerCase() == 'instagram';
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
      decoration: BoxDecoration(
        color: (isInstagram ? Colors.pinkAccent : Colors.cyanAccent)
            .withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        isInstagram ? 'IG' : 'TT',
        style: GoogleFonts.jetBrainsMono(
          fontSize: 9,
          fontWeight: FontWeight.w700,
          color: isInstagram ? Colors.pinkAccent : Colors.cyanAccent,
        ),
      ),
    );
  }
}
