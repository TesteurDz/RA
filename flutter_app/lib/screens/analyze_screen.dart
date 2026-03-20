import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:image_picker/image_picker.dart';
import '../core/constants.dart';
import '../core/api_service.dart';
import 'influencer_report_screen.dart';

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
  File? _screenshotFile;
  bool _uploadingScreenshot = false;
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

  Future<void> _pickScreenshot() async {
    final picker = ImagePicker();
    final xFile = await picker.pickImage(source: ImageSource.gallery);
    if (xFile != null && mounted) {
      setState(() => _screenshotFile = File(xFile.path));
    }
  }

  Future<void> _analyzeScreenshot() async {
    if (_screenshotFile == null) return;

    setState(() => _uploadingScreenshot = true);
    try {
      final result = await ApiService().uploadScreenshot(_screenshotFile!);
      if (mounted) {
        final id = result['influencer_id'] ?? result['id'];
        if (id == null) { setState(() => _uploadingScreenshot = false); return; }
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
      if (mounted) setState(() => _uploadingScreenshot = false);
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
          onTap: _pickScreenshot,
          child: Container(
            height: 220,
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: _screenshotFile != null ? AppColors.primary : AppColors.border,
                width: _screenshotFile != null ? 1.5 : 1,
              ),
            ),
            child: _screenshotFile != null
                ? ClipRRect(
                    borderRadius: BorderRadius.circular(15),
                    child: Stack(
                      fit: StackFit.expand,
                      children: [
                        Image.file(_screenshotFile!, fit: BoxFit.cover),
                        Positioned(
                          top: 8,
                          right: 8,
                          child: GestureDetector(
                            onTap: () => setState(() => _screenshotFile = null),
                            child: Container(
                              padding: const EdgeInsets.all(6),
                              decoration: const BoxDecoration(
                                color: Colors.black54,
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(Icons.close_rounded,
                                  size: 18, color: Colors.white),
                            ),
                          ),
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
                        'Appuyez pour choisir une capture',
                        style: GoogleFonts.inter(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                          color: AppColors.text,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Capture d\'ecran du profil Instagram ou TikTok',
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

        // Analyze screenshot button
        SizedBox(
          height: 56,
          child: ElevatedButton(
            onPressed: _screenshotFile != null && !_uploadingScreenshot
                ? _analyzeScreenshot
                : null,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              disabledBackgroundColor: AppColors.primary.withValues(alpha: 0.3),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
            ),
            child: _uploadingScreenshot
                ? const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(
                      strokeWidth: 2.5,
                      color: Colors.white,
                    ),
                  )
                : Text(
                    'Analyser la capture',
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
