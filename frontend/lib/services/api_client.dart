
import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;

class ApiClient {
  static const String _baseUrl = 'http://127.0.0.1:5000';

  Future<Map<String, dynamic>> optimizeResume({
    required String resumeText,
    required String jobDescription,
  }) async {
    final url = Uri.parse('$_baseUrl/optimize-resume');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'resume_text': resumeText,
        'job_description': jobDescription,
      }),
    );
    return _decodeResponse(response);
  }

  Future<Map<String, dynamic>> generateResume({
    required String name,
    required String education,
    required String experience,
    required String skills,
    required String template,
  }) async {
    final url = Uri.parse('$_baseUrl/generate-resume');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name,
        'education': education,
        'experience': experience,
        'skills': skills,
        'template': template,
      }),
    );
    return _decodeResponse(response);
  }

  Future<Map<String, dynamic>> generateCoverLetter({
    required String name,
    required String company,
    required String role,
    required String jobDescription,
    required String experience,
    required String skills,
  }) async {
    final url = Uri.parse('$_baseUrl/generate-cover-letter');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name,
        'company': company,
        'role': role,
        'job_description': jobDescription,
        'experience': experience,
        'skills': skills,
      }),
    );
    return _decodeResponse(response);
  }

  /// Export content to PDF.
  /// Returns the PDF bytes on success, or throws an exception on error.
  Future<Uint8List> exportPdf({
    required String documentType,
    required String content,
    required String template,
  }) async {
    final url = Uri.parse('$_baseUrl/export-pdf');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'document_type': documentType,
        'content': content,
        'template': template,
      }),
    );
    
    if (response.statusCode == 200) {
      return response.bodyBytes;
    } else {
      // Try to parse error message from JSON
      try {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(data['error'] ?? 'Failed to export PDF');
      } catch (e) {
        if (e is Exception && e.toString().contains('Failed to export PDF')) {
          rethrow;
        }
        throw Exception('Server error: ${response.statusCode}');
      }
    }
  }

  Map<String, dynamic> _decodeResponse(http.Response response) {
    try {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } catch (_) {
      return {'success': false, 'error': 'Invalid server response'};
    }
  }
}
