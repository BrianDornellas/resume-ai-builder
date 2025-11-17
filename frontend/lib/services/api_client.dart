import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiClient {
  static const String _baseUrl = 'http://127.0.0.1:5000';

  Future<Map<String, dynamic>> generateResume({
    required String name,
    required String education,
    required String experience,
    required String skills,
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

  Map<String, dynamic> _decodeResponse(http.Response response) {
    try {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } catch (_) {
      return {'success': false, 'error': 'Invalid server response'};
    }
  }
}
