import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:shimmer/shimmer.dart';
import '../core/constants.dart';
import '../core/api_service.dart';
import 'influencer_report_screen.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<Map<String, dynamic>> _allInfluencers = [];
  List<Map<String, dynamic>> _filtered = [];
  bool _loading = true;
  String _searchQuery = '';
  String _platformFilter = 'all'; // 'all', 'instagram', 'tiktok'
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadInfluencers();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadInfluencers() async {
    setState(() => _loading = true);
    try {
      final data = await ApiService().getInfluencers();
      if (mounted) {
        setState(() {
          _allInfluencers = data;
          _loading = false;
          _applyFilters();
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _loading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Erreur lors du chargement',
              style: GoogleFonts.inter(color: Colors.white),
            ),
            backgroundColor: AppColors.danger,
          ),
        );
      }
    }
  }

  void _applyFilters() {
    setState(() {
      _filtered = _allInfluencers.where((item) {
        final username = (item['username'] ?? '').toString().toLowerCase();
        final name = (item['name'] ?? item['full_name'] ?? '').toString().toLowerCase();
        final platform = (item['platform'] ?? '').toString().toLowerCase();
        final query = _searchQuery.toLowerCase();

        final matchesSearch = query.isEmpty ||
            username.contains(query) ||
            name.contains(query);
        final matchesPlatform =
            _platformFilter == 'all' || platform == _platformFilter;

        return matchesSearch && matchesPlatform;
      }).toList();
    });
  }

  Future<void> _deleteInfluencer(int id, int index) async {
    try {
      await ApiService().deleteInfluencer(id);
      if (mounted) {
        setState(() {
          _allInfluencers.removeWhere((item) => item['id'] == id);
          _applyFilters();
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Influenceur supprime',
              style: GoogleFonts.inter(color: Colors.white),
            ),
            backgroundColor: AppColors.success,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Erreur lors de la suppression',
              style: GoogleFonts.inter(color: Colors.white),
            ),
            backgroundColor: AppColors.danger,
          ),
        );
      }
    }
  }

  String _formatFollowers(dynamic count) {
    if (count == null) return '—';
    final n = count is int ? count : int.tryParse(count.toString()) ?? 0;
    if (n >= 1000000) return '${(n / 1000000).toStringAsFixed(1)}M';
    if (n >= 1000) return '${(n / 1000).toStringAsFixed(1)}K';
    return n.toString();
  }

  String _formatDate(String dateStr) {
    try {
      final date = DateTime.parse(dateStr);
      final now = DateTime.now();
      final diff = now.difference(date);
      if (diff.inMinutes < 60) return 'il y a ${diff.inMinutes}min';
      if (diff.inHours < 24) return 'il y a ${diff.inHours}h';
      if (diff.inDays < 7) return 'il y a ${diff.inDays}j';
      return '${date.day.toString().padLeft(2, '0')}/${date.month.toString().padLeft(2, '0')}/${date.year}';
    } catch (_) {
      return '';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          color: AppColors.primary,
          backgroundColor: AppColors.surface,
          onRefresh: _loadInfluencers,
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
                        'Historique',
                        style: GoogleFonts.inter(
                          fontSize: 28,
                          fontWeight: FontWeight.w800,
                          color: AppColors.text,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Tous les influenceurs analyses',
                        style: GoogleFonts.inter(
                          fontSize: 14,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // ─── Search Bar ─────────────────────────
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 16, 20, 0),
                  child: SizedBox(
                    height: 48,
                    child: TextField(
                      controller: _searchController,
                      onChanged: (value) {
                        _searchQuery = value;
                        _applyFilters();
                      },
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        color: AppColors.text,
                      ),
                      decoration: InputDecoration(
                        hintText: 'Rechercher un influenceur...',
                        prefixIcon: const Icon(Icons.search_rounded,
                            color: AppColors.textSecondary, size: 20),
                        suffixIcon: _searchQuery.isNotEmpty
                            ? IconButton(
                                icon: const Icon(Icons.clear_rounded,
                                    color: AppColors.textSecondary, size: 18),
                                onPressed: () {
                                  _searchController.clear();
                                  _searchQuery = '';
                                  _applyFilters();
                                },
                              )
                            : null,
                        contentPadding:
                            const EdgeInsets.symmetric(vertical: 12),
                      ),
                    ),
                  ),
                ),
              ),

              // ─── Platform Filter Chips ──────────────
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(20, 12, 20, 16),
                  child: Row(
                    children: [
                      _filterChip('all', 'Tous'),
                      const SizedBox(width: 8),
                      _filterChip('instagram', 'Instagram'),
                      const SizedBox(width: 8),
                      _filterChip('tiktok', 'TikTok'),
                    ],
                  ),
                ),
              ),

              // ─── List ───────────────────────────────
              if (_loading)
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Column(
                      children: List.generate(
                        6,
                        (i) => Padding(
                          padding: const EdgeInsets.only(bottom: 10),
                          child: Shimmer.fromColors(
                            baseColor: AppColors.surface,
                            highlightColor: AppColors.border,
                            child: Container(
                              height: 88,
                              decoration: BoxDecoration(
                                color: AppColors.surface,
                                borderRadius: BorderRadius.circular(14),
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                )
              else if (_filtered.isEmpty)
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.fromLTRB(20, 32, 20, 0),
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
                            _searchQuery.isNotEmpty
                                ? Icons.search_off_rounded
                                : Icons.people_outline_rounded,
                            size: 48,
                            color: AppColors.textSecondary.withValues(alpha: 0.5),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            _searchQuery.isNotEmpty
                                ? 'Aucun resultat'
                                : 'Aucun influenceur analyse',
                            style: GoogleFonts.inter(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: AppColors.text,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _searchQuery.isNotEmpty
                                ? 'Essayez un autre terme de recherche.'
                                : 'Commencez par analyser un influenceur.',
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
                      final item = _filtered[index];
                      return Padding(
                        padding: const EdgeInsets.fromLTRB(20, 0, 20, 10),
                        child: _influencerCard(item, index),
                      );
                    },
                    childCount: _filtered.length,
                  ),
                ),

              const SliverToBoxAdapter(child: SizedBox(height: 100)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _filterChip(String value, String label) {
    final selected = _platformFilter == value;
    return GestureDetector(
      onTap: () {
        _platformFilter = value;
        _applyFilters();
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: selected
              ? AppColors.primary.withValues(alpha: 0.15)
              : AppColors.surface,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: selected ? AppColors.primary : AppColors.border,
          ),
        ),
        child: Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 13,
            fontWeight: selected ? FontWeight.w600 : FontWeight.w500,
            color: selected ? AppColors.primary : AppColors.textSecondary,
          ),
        ),
      ),
    );
  }

  Widget _influencerCard(Map<String, dynamic> item, int index) {
    final id = item['id'];
    final intId = id is int ? id : int.parse(id.toString());
    final score = (item['score'] ?? 0).toDouble();
    final platform = (item['platform'] ?? '').toString();
    final profilePic = (item['profile_pic'] ?? item['profile_picture'] ?? '').toString();
    final username = (item['username'] ?? '').toString();
    final name = (item['name'] ?? item['full_name'] ?? username).toString();
    final followers = item['followers'] ?? item['followers_count'];
    final engagement = item['engagement_rate'] ?? item['engagement'];
    final date = (item['analyzed_at'] ?? item['created_at'] ?? '').toString();

    return Dismissible(
      key: ValueKey(intId),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        decoration: BoxDecoration(
          color: AppColors.danger.withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(14),
        ),
        child: const Icon(Icons.delete_outline_rounded,
            color: AppColors.danger, size: 24),
      ),
      confirmDismiss: (direction) async {
        return await showDialog<bool>(
          context: context,
          builder: (ctx) => AlertDialog(
            backgroundColor: AppColors.surface,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            title: Text(
              'Supprimer ?',
              style: GoogleFonts.inter(
                color: AppColors.text,
                fontWeight: FontWeight.w700,
              ),
            ),
            content: Text(
              'Voulez-vous supprimer @$username de votre historique ?',
              style: GoogleFonts.inter(color: AppColors.textSecondary),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx, false),
                child: Text('Annuler',
                    style: GoogleFonts.inter(color: AppColors.textSecondary)),
              ),
              TextButton(
                onPressed: () => Navigator.pop(ctx, true),
                child: Text('Supprimer',
                    style: GoogleFonts.inter(color: AppColors.danger)),
              ),
            ],
          ),
        );
      },
      onDismissed: (_) => _deleteInfluencer(intId, index),
      child: GestureDetector(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => InfluencerReportScreen(influencerId: intId),
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
              // Profile pic
              ClipRRect(
                borderRadius: BorderRadius.circular(22),
                child: SizedBox(
                  width: 44,
                  height: 44,
                  child: profilePic.isNotEmpty
                      ? CachedNetworkImage(
                          imageUrl: profilePic,
                          fit: BoxFit.cover,
                          placeholder: (_, __) => _avatarPlaceholder(username),
                          errorWidget: (_, __, ___) =>
                              _avatarPlaceholder(username),
                        )
                      : _avatarPlaceholder(username),
                ),
              ),
              const SizedBox(width: 12),

              // Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Flexible(
                          child: Text(
                            name,
                            style: GoogleFonts.inter(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: AppColors.text,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(width: 6),
                        _platformBadge(platform),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Text(
                          '@$username',
                          style: GoogleFonts.inter(
                            fontSize: 12,
                            color: AppColors.textSecondary,
                          ),
                        ),
                        if (followers != null) ...[
                          const SizedBox(width: 10),
                          Icon(Icons.people_outline_rounded,
                              size: 12, color: AppColors.textSecondary.withValues(alpha: 0.6)),
                          const SizedBox(width: 3),
                          Text(
                            _formatFollowers(followers),
                            style: AppTextStyles.dataSmall(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                        if (engagement != null) ...[
                          const SizedBox(width: 10),
                          Icon(Icons.favorite_outline_rounded,
                              size: 12, color: AppColors.textSecondary.withValues(alpha: 0.6)),
                          const SizedBox(width: 3),
                          Text(
                            '${(engagement is double ? engagement : double.tryParse(engagement.toString()) ?? 0).toStringAsFixed(1)}%',
                            style: AppTextStyles.dataSmall(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ],
                    ),
                    if (date.isNotEmpty) ...[
                      const SizedBox(height: 2),
                      Text(
                        _formatDate(date),
                        style: GoogleFonts.inter(
                          fontSize: 11,
                          color: AppColors.textSecondary.withValues(alpha: 0.5),
                        ),
                      ),
                    ],
                  ],
                ),
              ),

              const SizedBox(width: 8),

              // Score
              Column(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: AppColors.scoreColor(score)
                          .withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      score.toStringAsFixed(1),
                      style: AppTextStyles.dataSmall(
                        color: AppColors.scoreColor(score),
                      ),
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    AppColors.scoreLabel(score),
                    style: GoogleFonts.inter(
                      fontSize: 9,
                      fontWeight: FontWeight.w600,
                      color: AppColors.scoreColor(score),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _avatarPlaceholder(String username) {
    return Container(
      width: 44,
      height: 44,
      alignment: Alignment.center,
      color: AppColors.primary.withValues(alpha: 0.15),
      child: Text(
        username.isNotEmpty ? username[0].toUpperCase() : '?',
        style: GoogleFonts.inter(
          fontWeight: FontWeight.w700,
          fontSize: 16,
          color: AppColors.primary,
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
}
