class Influencer {
  final int id;
  final String username;
  final String platform;
  final String? fullName;
  final String? bio;
  final String? profilePicUrl;
  final int followersCount;
  final int followingCount;
  final int postsCount;
  final bool isVerified;
  final String? zoneOperation;
  final double engagementRate;
  final double fakeFollowersPct;
  final double overallScore;
  final Map<String, dynamic>? demographics;
  final int? snapshotId;

  const Influencer({
    required this.id,
    required this.username,
    required this.platform,
    this.fullName,
    this.bio,
    this.profilePicUrl,
    this.followersCount = 0,
    this.followingCount = 0,
    this.postsCount = 0,
    this.isVerified = false,
    this.zoneOperation,
    this.engagementRate = 0.0,
    this.fakeFollowersPct = 0.0,
    this.overallScore = 0.0,
    this.demographics,
    this.snapshotId,
  });

  factory Influencer.fromJson(Map<String, dynamic> json) {
    return Influencer(
      id: json['id'] ?? 0,
      username: json['username'] ?? '',
      platform: json['platform'] ?? 'instagram',
      fullName: json['full_name'] ?? json['fullName'],
      bio: json['bio'],
      profilePicUrl: json['profile_pic_url'] ?? json['profilePicUrl'],
      followersCount: _toInt(json['followers_count'] ?? json['followersCount']),
      followingCount: _toInt(json['following_count'] ?? json['followingCount']),
      postsCount: _toInt(json['posts_count'] ?? json['postsCount']),
      isVerified: json['is_verified'] ?? json['isVerified'] ?? false,
      zoneOperation: json['zone_operation'] ?? json['zoneOperation'],
      engagementRate:
          _toDouble(json['engagement_rate'] ?? json['engagementRate']),
      fakeFollowersPct:
          _toDouble(json['fake_followers_pct'] ?? json['fakeFollowersPct']),
      overallScore: _toDouble(json['overall_score'] ?? json['overallScore']),
      demographics: json['demographics'] is Map<String, dynamic>
          ? json['demographics']
          : null,
      snapshotId: json['snapshot_id'] ?? json['snapshotId'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'platform': platform,
      'full_name': fullName,
      'bio': bio,
      'profile_pic_url': profilePicUrl,
      'followers_count': followersCount,
      'following_count': followingCount,
      'posts_count': postsCount,
      'is_verified': isVerified,
      'zone_operation': zoneOperation,
      'engagement_rate': engagementRate,
      'fake_followers_pct': fakeFollowersPct,
      'overall_score': overallScore,
      'demographics': demographics,
      'snapshot_id': snapshotId,
    };
  }

  /// Nom affiche : fullName si disponible, sinon @username
  String get displayName => fullName?.isNotEmpty == true ? fullName! : '@$username';

  /// Nombre de followers formate (ex: 12.5K, 1.2M)
  String get followersFormatted => _formatCount(followersCount);

  /// Nombre de following formate
  String get followingFormatted => _formatCount(followingCount);

  /// Nombre de posts formate
  String get postsFormatted => _formatCount(postsCount);

  static int _toInt(dynamic value) {
    if (value == null) return 0;
    if (value is int) return value;
    if (value is double) return value.toInt();
    if (value is String) return int.tryParse(value) ?? 0;
    return 0;
  }

  static double _toDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? 0.0;
    return 0.0;
  }

  static String _formatCount(int count) {
    if (count >= 1000000) {
      return '${(count / 1000000).toStringAsFixed(1)}M';
    }
    if (count >= 1000) {
      return '${(count / 1000).toStringAsFixed(1)}K';
    }
    return count.toString();
  }
}
