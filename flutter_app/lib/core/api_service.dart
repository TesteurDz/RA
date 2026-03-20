import 'package:http_parser/http_parser.dart';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class ApiService {
  ApiService._internal();
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  static const Duration _timeout = Duration(seconds: 120);

  // URL du backend RA sur le VPS
  static const String _vpsBaseUrl = 'http://187.124.37.159:8001';

  String get baseUrl {
    // En dev Android emulator: 10.0.2.2, sinon VPS
    if (!kIsWeb && Platform.isAndroid) {
      return _vpsBaseUrl;
    }
    return _vpsBaseUrl;
  }

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

  /// Analyser un influenceur par username et plateforme
  Future<Map<String, dynamic>> analyzeInfluencer(
    String username,
    String platform,
  ) async {
    final uri = Uri.parse('$baseUrl/api/influencers/analyze').replace(
      queryParameters: {
        'username': username,
        'platform': platform,
      },
    );

    final response = await http.post(uri, headers: _headers).timeout(_timeout);
    return _handleResponse(response);
  }

  /// Uploader une capture d'ecran pour analyse
  Future<Map<String, dynamic>> uploadScreenshot(
    File file, {
    String platform = 'instagram',
  }) async {
    final uri = Uri.parse('$baseUrl/api/influencers/screenshot');
    final request = http.MultipartRequest('POST', uri);

    final filename = file.path.split('/').last;
    final ext = filename.split('.').last.toLowerCase();
    final mimeType = {
      'jpg': 'image/jpeg',
      'jpeg': 'image/jpeg',
      'png': 'image/png',
      'webp': 'image/webp',
    }[ext] ?? 'image/jpeg';
    request.files.add(
      await http.MultipartFile.fromPath(
        'file',
        file.path,
        filename: filename,
        contentType: MediaType.parse(mimeType),
      ),
    );
    request.fields['platform'] = platform;

    final streamedResponse = await request.send().timeout(_timeout);
    final response = await http.Response.fromStream(streamedResponse);
    return _handleResponse(response);
  }

  /// Recuperer la liste de tous les influenceurs
  Future<List<Map<String, dynamic>>> getInfluencers() async {
    final uri = Uri.parse('$baseUrl/api/influencers/');
    final response = await http.get(uri, headers: _headers).timeout(_timeout);
    final data = _handleResponse(response);

    // Backend peut retourner {influencers: []}, {items: []}, ou {data: []}
    for (final key in ['influencers', 'items', 'data']) {
      if (data[key] is List) {
        return List<Map<String, dynamic>>.from(data[key]);
      }
    }
    // Si la reponse est directement une liste
    final decoded = jsonDecode(response.body);
    if (decoded is List) {
      return List<Map<String, dynamic>>.from(decoded);
    }
    return [];
  }

  /// Recuperer un influenceur par ID avec details complets
  Future<Map<String, dynamic>> getInfluencer(int id) async {
    final uri = Uri.parse('$baseUrl/api/influencers/$id');
    final response = await http.get(uri, headers: _headers).timeout(_timeout);
    return _handleResponse(response);
  }

  /// Recuperer l'historique des snapshots d'un influenceur
  Future<List<Map<String, dynamic>>> getInfluencerHistory(int id) async {
    final uri = Uri.parse('$baseUrl/api/influencers/$id/history');
    final response = await http.get(uri, headers: _headers).timeout(_timeout);
    final decoded = jsonDecode(response.body);

    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (decoded is List) {
        return List<Map<String, dynamic>>.from(decoded);
      }
      if (decoded is Map) {
        // Backend peut retourner {recent: []}, {items: []}, ou {data: []}
        for (final key in ['recent', 'items', 'data']) {
          if (decoded.containsKey(key) && decoded[key] is List) {
            return List<Map<String, dynamic>>.from(decoded[key]);
          }
        }
      }
      return [];
    }

    throw ApiException(
      statusCode: response.statusCode,
      message: decoded is Map ? (decoded['detail'] ?? 'Erreur inconnue') : 'Erreur inconnue',
    );
  }

  /// Recuperer les statistiques du tableau de bord
  Future<Map<String, dynamic>> getDashboardStats() async {
    final uri = Uri.parse('$baseUrl/api/dashboard/stats');
    final response = await http.get(uri, headers: _headers).timeout(_timeout);
    return _handleResponse(response);
  }

  /// Recuperer les analyses recentes
  Future<List<Map<String, dynamic>>> getDashboardRecent() async {
    final uri = Uri.parse('$baseUrl/api/dashboard/recent');
    final response = await http.get(uri, headers: _headers).timeout(_timeout);
    final decoded = jsonDecode(response.body);

    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (decoded is List) {
        return List<Map<String, dynamic>>.from(decoded);
      }
      if (decoded is Map) {
        for (final key in ['recent', 'items', 'data']) {
          if (decoded.containsKey(key) && decoded[key] is List) {
            return List<Map<String, dynamic>>.from(decoded[key]);
          }
        }
      }
    }

    throw ApiException(
      statusCode: response.statusCode,
      message: decoded['detail'] ?? 'Erreur inconnue',
    );
  }

  /// Comparer plusieurs influenceurs
  Future<Map<String, dynamic>> compareInfluencers(List<int> ids) async {
    final uri = Uri.parse('$baseUrl/api/influencers/compare');
    final response = await http
        .post(
          uri,
          headers: _headers,
          body: jsonEncode({'ids': ids}),
        )
        .timeout(_timeout);
    return _handleResponse(response);
  }

  /// Supprimer un influenceur
  Future<void> deleteInfluencer(int id) async {
    final uri = Uri.parse('$baseUrl/api/influencers/$id');
    final response =
        await http.delete(uri, headers: _headers).timeout(_timeout);

    if (response.statusCode < 200 || response.statusCode >= 300) {
      final decoded = jsonDecode(response.body);
      throw ApiException(
        statusCode: response.statusCode,
        message: decoded['detail'] ?? 'Erreur lors de la suppression',
      );
    }
  }

  Map<String, dynamic> _handleResponse(http.Response response) {
    final decoded = jsonDecode(response.body);

    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (decoded is Map<String, dynamic>) {
        return decoded;
      }
      return {'data': decoded};
    }

    throw ApiException(
      statusCode: response.statusCode,
      message: decoded is Map
          ? (decoded['detail'] ?? 'Erreur inconnue')
          : 'Erreur inconnue',
    );
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException({required this.statusCode, required this.message});

  @override
  String toString() => 'ApiException($statusCode): $message';
}
