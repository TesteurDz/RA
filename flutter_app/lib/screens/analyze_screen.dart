import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:image_picker/image_picker.dart';
import '../core/constants.dart';
import '../core/api_service.dart';
import 'influencer_report_screen.dart';

String _formatNum(num n) {
  if (n >= 1000000) return "${(n / 1000000).toStringAsFixed(1)}M";
  if (n >= 1000) return "${(n / 1000).toStringAsFixed(1)}K";
  return n.toString();
}

class AnalyzeScreen extends StatefulWidget {
  const AnalyzeScreen({super.key});

  @override
  State<AnalyzeScreen> createState() => _AnalyzeScreenState();
}

class _AnalyzeScreenState extends State<AnalyzeScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _usernameController = TextEditingController();
  String _platform = 'instagram';
  bool _analyzing = false;
  List<File> _screenshotFiles = [];
  bool _uploadingScreenshot = false;
  List<Map<String, dynamic>> _screenshotResults = [];
  String _screenshotProgress = '';
  List<Map<String, dynamic>> _recentAnalyses = [];
  bool _loadingRecent = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _tabController.addListener(() {
      if (mounted) setState(() {});
    });
    _loadRecentAnalyses();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _usernameController.dispose();
    super.dispose();
  }

  Future<void> _loadRecentAnalyses() async {
    try {
      final data = await ApiService().getDashboardRecent();
      if (mounted) {
        setState(() {
          _recentAnalyses = data;
          _loadingRecent = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() => _loadingRecent = false);
    }
  }

  Future<void> _analyzeUsername() async {
    final username = _usernameController.text.trim();
    if (username.isEmpty) return;

    setState(() => _analyzing = true);
    try {
      final result = await ApiService().analyzeInfluencer(username, _platform);
      if (mounted) {
        final id = result['id'];
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => InfluencerReportScreen(influencerId: id is int ? id : int.parse(id.toString())),
          ),
        );
        _loadRecentAnalyses();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              e.toString().replaceFirst('Exception: ', '').replaceFirst(RegExp(r'^ApiException\(\d+\): '), ''),
              style: GoogleFonts.inter(color: Colors.white),
            ),
            backgroundColor: AppColors.danger,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _analyzing = false);
    }
  }

  Future<void> _pickScreenshots() async {
    final picker = ImagePicker();
    final xFiles = await picker.pickMultiImage();
    if (xFiles.isNotEmpty && mounted) {
      setState(() {
        _screenshotFiles.addAll(xFiles.map((x) => File(x.path)));
        _screenshotResults = [];
      });
    }
  }

  Future<void> _analyzeScreenshots() async {
    if (_screenshotFiles.isEmpty) return;

    setState(() {
      _uploadingScreenshot = true;
      _screenshotResults = [];
      _screenshotProgress = '';
    });

    final total = _screenshotFiles.length;
    final List<Map<String, dynamic>> results = [];

    for (int i = 0; i < total; i++) {
      if (!mounted) break;
      setState(() {
        _screenshotProgress = 'Analyse ${i + 1}/$total...';
      });

      try {
        final result = await ApiService().uploadScreenshot(
          _screenshotFiles[i],
        );
        final id = result['influencer_id'] ?? result['id'];
        final ocr = result['ocr_data'] as Map<String, dynamic>? ?? {};
        results.add({
          'id': id,
          'username': result['username'] ?? ocr['username'] ?? '',
          'followers_count': result['followers_count'] ?? ocr['followers'] ?? 0,
          'engagement_rate': result['engagement_rate'] ?? 0,
          'overall_score': result['overall_score'],
          'filename': _screenshotFiles[i].path.split('/').last,
        });
      } catch (e) {
        results.add({
          'error': e.toString().replaceFirst('Exception: ', '').replaceFirst(RegExp(r'^ApiException\(\d+\): '), ''),
          'filename': _screenshotFiles[i].path.split('/').last,
        });
      }

      // Update partial results in real-time
      if (mounted) {
        setState(() => _screenshotResults = List.from(results));
      }
    }

    if (mounted) {
      setState(() {
        _uploadingScreenshot = false;
        _screenshotProgress = '';
        _screenshotResults = results;
      });
      _loadRecentAnalyses();
    }
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
                'Analyser',
                style: GoogleFonts.inter(
                  fontSize: 28,
                  fontWeight: FontWeight.w800,
                  color: AppColors.text,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                'Verifiez l\'authenticite d\'un influenceur',
                style: GoogleFonts.inter(
                  fontSize: 14,
                  color: AppColors.textSecondary,
                ),
              ),
              const SizedBox(height: 24),

              // ─── Tab Selector ───────────────────────
              Container(
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.border),
                ),
                child: TabBar(
                  controller: _tabController,
                  indicator: BoxDecoration(
                    color: AppColors.primary,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  indicatorSize: TabBarIndicatorSize.tab,
                  labelColor: Colors.white,
                  unselectedLabelColor: AppColors.textSecondary,
                  labelStyle: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                  unselectedLabelStyle: GoogleFonts.inter(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                  dividerHeight: 0,
                  padding: const EdgeInsets.all(4),
                  tabs: const [
                    Tab(text: 'Nom d\'utilisateur'),
                    Tab(text: 'Capture d\'ecran'),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // ─── Tab Content ────────────────────────
              if (_tabController.index == 0) _buildUsernameMode() else _buildScreenshotMode(),

              const SizedBox(height: 32),

              // ─── Recent analyses ────────────────────
              _buildRecentSection(),
            ],
          ),
        ),
      ),
    );
  }

  // ─── USERNAME MODE ──────────────────────────────────────────
  Widget _buildUsernameMode() {
    final username = _usernameController.text.trim();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Platform selector
        Row(
          children: [
            _platformChip('instagram', 'Instagram', Icons.camera_alt_rounded),
            const SizedBox(width: 12),
            _platformChip('tiktok', 'TikTok', Icons.music_note_rounded),
          ],
        ),
        const SizedBox(height: 20),

        // Username field
        SizedBox(
          height: 56,
          child: TextField(
            controller: _usernameController,
            textInputAction: TextInputAction.search,
            onSubmitted: (_) => _analyzeUsername(),
            onChanged: (_) => setState(() {}),
            inputFormatters: [
              FilteringTextInputFormatter.deny(RegExp(r'\s')),
            ],
            style: GoogleFonts.inter(
              fontSize: 16,
              color: AppColors.text,
            ),
            decoration: InputDecoration(
              prefixIcon: Padding(
                padding: const EdgeInsets.only(left: 16, right: 4),
                child: Text(
                  '@',
                  style: GoogleFonts.jetBrainsMono(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: AppColors.primary,
                  ),
                ),
              ),
              prefixIconConstraints: const BoxConstraints(minWidth: 0),
              hintText: 'nom_utilisateur',
              suffixIcon: username.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear_rounded,
                          color: AppColors.textSecondary, size: 20),
                      onPressed: () {
                        _usernameController.clear();
                        setState(() {});
                      },
                    )
                  : null,
              contentPadding: const EdgeInsets.symmetric(vertical: 16),
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Analyze button
        SizedBox(
          height: 56,
          child: ElevatedButton(
            onPressed: username.isNotEmpty && !_analyzing ? _analyzeUsername : null,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              disabledBackgroundColor: AppColors.primary.withValues(alpha: 0.3),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
            ),
            child: _analyzing
                ? const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(
                      strokeWidth: 2.5,
                      color: Colors.white,
                    ),
                  )
                : Text(
                    'Analyser',
                    style: GoogleFonts.inter(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                    ),
                  ),
          ),
        ),
      ],
    );
  }

  Widget _platformChip(String value, String label, IconData icon) {
    final selected = _platform == value;
    return Expanded(
      child: GestureDetector(
        onTap: () => setState(() => _platform = value),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          height: 48,
          decoration: BoxDecoration(
            color: selected
                ? AppColors.primary.withValues(alpha: 0.15)
                : AppColors.surface,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: selected ? AppColors.primary : AppColors.border,
              width: selected ? 1.5 : 1,
            ),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 18,
                color: selected ? AppColors.primary : AppColors.textSecondary,
              ),
              const SizedBox(width: 8),
              Text(
                label,
                style: GoogleFonts.inter(
                  fontSize: 14,
                  fontWeight: selected ? FontWeight.w600 : FontWeight.w500,
                  color: selected ? AppColors.primary : AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ─── SCREENSHOT MODE ────────────────────────────────────────
  Widget _buildScreenshotMode() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Upload area
        GestureDetector(
          onTap: _pickScreenshots,
          child: Container(
            height: _screenshotFiles.isEmpty ? 220 : null,
            constraints: _screenshotFiles.isNotEmpty ? const BoxConstraints(minHeight: 120) : null,
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: _screenshotFiles.isNotEmpty ? AppColors.primary : AppColors.border,
                width: _screenshotFiles.isNotEmpty ? 1.5 : 1,
              ),
            ),
            child: _screenshotFiles.isNotEmpty
                ? Padding(
                    padding: const EdgeInsets.all(8),
                    child: Column(
                      children: [
                        // Thumbnails grid
                        Wrap(
                          spacing: 8,
                          runSpacing: 8,
                          children: [
                            ..._screenshotFiles.asMap().entries.map((entry) {
                              final idx = entry.key;
                              final file = entry.value;
                              return Stack(
                                children: [
                                  ClipRRect(
                                    borderRadius: BorderRadius.circular(10),
                                    child: Image.file(file, width: 90, height: 90, fit: BoxFit.cover),
                                  ),
                                  Positioned(
                                    top: 2, right: 2,
                                    child: GestureDetector(
                                      onTap: () => setState(() {
                                        _screenshotFiles.removeAt(idx);
                                        _screenshotResults = [];
                                      }),
                                      child: Container(
                                        padding: const EdgeInsets.all(4),
                                        decoration: const BoxDecoration(
                                          color: Colors.black54,
                                          shape: BoxShape.circle,
                                        ),
                                        child: const Icon(Icons.close_rounded, size: 14, color: Colors.white),
                                      ),
                                    ),
                                  ),
                                ],
                              );
                            }),
                            // Add more button
                            GestureDetector(
                              onTap: _pickScreenshots,
                              child: Container(
                                width: 90, height: 90,
                                decoration: BoxDecoration(
                                  color: AppColors.primary.withValues(alpha: 0.08),
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(color: AppColors.primary.withValues(alpha: 0.3)),
                                ),
                                child: const Icon(Icons.add_rounded, size: 28, color: AppColors.primary),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '${_screenshotFiles.length} capture${_screenshotFiles.length > 1 ? 's' : ''} selectionnee${_screenshotFiles.length > 1 ? 's' : ''}',
                          style: GoogleFonts.inter(fontSize: 12, color: AppColors.textSecondary),
                        ),
                      ],
                    ),
                  )
                : Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: AppColors.primary.withValues(alpha: 0.1),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.add_photo_alternate_rounded,
                          size: 32,
                          color: AppColors.primary,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Appuyez pour choisir des captures',
                        style: GoogleFonts.inter(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                          color: AppColors.text,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Une ou plusieurs captures de profils IG/TikTok',
                        style: GoogleFonts.inter(
                          fontSize: 13,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
          ),
        ),
        const SizedBox(height: 16),

        // Analyze button
        SizedBox(
          height: 56,
          child: ElevatedButton(
            onPressed: _screenshotFiles.isNotEmpty && !_uploadingScreenshot
                ? _analyzeScreenshots
                : null,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              disabledBackgroundColor: AppColors.primary.withValues(alpha: 0.3),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
            ),
            child: _uploadingScreenshot
                ? Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const SizedBox(
                        width: 24, height: 24,
                        child: CircularProgressIndicator(strokeWidth: 2.5, color: Colors.white),
                      ),
                      const SizedBox(width: 12),
                      Text(
                        _screenshotProgress.isNotEmpty ? _screenshotProgress : 'Analyse en cours...',
                        style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.w600, color: Colors.white),
                      ),
                    ],
                  )
                : Text(
                    _screenshotFiles.length > 1
                        ? 'Analyser ${_screenshotFiles.length} captures'
                        : 'Analyser la capture',
                    style: GoogleFonts.inter(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                    ),
                  ),
          ),
        ),

        // Results from multi-screenshot
        if (_screenshotResults.isNotEmpty) ...[
          const SizedBox(height: 20),
          Text('RESULTATS', style: AppTextStyles.sectionLabel),
          const SizedBox(height: 8),
          ..._screenshotResults.map((r) {
            final hasError = r['error'] != null;
            return GestureDetector(
              onTap: hasError ? null : () {
                final id = r['id'];
                if (id != null) {
                  Navigator.push(context, MaterialPageRoute(
                    builder: (_) => InfluencerReportScreen(
                      influencerId: id is int ? id : int.parse(id.toString()),
                    ),
                  ));
                }
              },
              child: Container(
                margin: const EdgeInsets.only(bottom: 8),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: hasError ? AppColors.danger.withValues(alpha: 0.3) : AppColors.border,
                  ),
                ),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 18,
                      backgroundColor: hasError
                          ? AppColors.danger.withValues(alpha: 0.15)
                          : AppColors.primary.withValues(alpha: 0.15),
                      child: Icon(
                        hasError ? Icons.error_outline : Icons.check_circle_outline,
                        size: 20,
                        color: hasError ? AppColors.danger : AppColors.primary,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            hasError
                                ? (r['filename'] ?? 'Erreur')
                                : '@${r['username'] ?? ''}',
                            style: GoogleFonts.inter(
                              fontSize: 14,
                              fontWeight: FontWeight.w600,
                              color: AppColors.text,
                            ),
                          ),
                          if (hasError)
                            Text(
                              r['error'].toString(),
                              style: GoogleFonts.inter(fontSize: 11, color: AppColors.danger),
                            )
                          else
                            Text(
                              '${_formatNum(r['followers_count'] ?? 0)} abonnes  •  ER: ${(r['engagement_rate'] ?? 0).toStringAsFixed(1)}%',
                              style: GoogleFonts.inter(fontSize: 11, color: AppColors.textSecondary),
                            ),
                        ],
                      ),
                    ),
                    if (!hasError && r['overall_score'] != null)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.scoreColor((r['overall_score'] as num).toDouble()).withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          (r['overall_score'] as num).toStringAsFixed(1),
                          style: GoogleFonts.inter(
                            fontSize: 13,
                            fontWeight: FontWeight.w700,
                            color: AppColors.scoreColor((r['overall_score'] as num).toDouble()),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            );
          }),
        ],
      ],
    );
  }

  // ─── RECENT ANALYSES ────────────────────────────────────────
  Widget _buildRecentSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('ANALYSES RECENTES', style: AppTextStyles.sectionLabel),
        const SizedBox(height: 12),
        if (_loadingRecent) ...[
          for (int i = 0; i < 3; i++) ...[
            _shimmerCard(),
            if (i < 2) const SizedBox(height: 8),
          ],
        ] else if (_recentAnalyses.isEmpty)
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.border),
            ),
            child: Center(
              child: Text(
                'Aucune analyse recente',
                style: GoogleFonts.inter(
                  fontSize: 14,
                  color: AppColors.textSecondary,
                ),
              ),
            ),
          )
        else
          ...List.generate(_recentAnalyses.length, (i) {
            final item = _recentAnalyses[i];
            return Padding(
              padding: EdgeInsets.only(bottom: i < _recentAnalyses.length - 1 ? 8 : 0),
              child: _recentCard(item),
            );
          }),
      ],
    );
  }

  Widget _recentCard(Map<String, dynamic> item) {
    final score = (item['overall_score'] ?? item['score'] ?? 0).toDouble();
    final username = item['username'] ?? '';
    final platform = (item['platform'] ?? '').toString();

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
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.border),
        ),
        child: Row(
          children: [
            CircleAvatar(
              radius: 20,
              backgroundColor: AppColors.primary.withValues(alpha: 0.15),
              child: Text(
                username.isNotEmpty ? username[0].toUpperCase() : '?',
                style: GoogleFonts.inter(
                  fontWeight: FontWeight.w700,
                  color: AppColors.primary,
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '@$username',
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppColors.text,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Row(
                    children: [
                      _platformBadge(platform),
                    ],
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
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

  Widget _shimmerCard() {
    return Container(
      height: 64,
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
    );
  }
}
