import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Update this URL to match your backend
  static const String baseUrl = 'http://localhost:5000';

  Future<Map<String, dynamic>> generateResume({
    required String name,
    required String education,
    required String experience,
    required String skills,
    String template = 'chronological',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/generate-resume'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'name': name,
          'education': education,
          'experience': experience,
          'skills': skills,
          'template': template,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (data['success'] == true) {
          return {
            'resume': data['resume'],
            'template': data['template'],
          };
        } else {
          throw Exception(data['error'] ?? 'Failed to generate resume');
        }
      } else {
        throw Exception('Server error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to connect to server: $e');
    }
  }
}
