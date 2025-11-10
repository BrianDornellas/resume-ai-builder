import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../services/api_service.dart';

class ResumeFormScreen extends StatefulWidget {
  const ResumeFormScreen({super.key});

  @override
  State<ResumeFormScreen> createState() => _ResumeFormScreenState();
}

class _ResumeFormScreenState extends State<ResumeFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _educationController = TextEditingController();
  final _experienceController = TextEditingController();
  final _skillsController = TextEditingController();
  final _apiService = ApiService();

  String? _generatedResume;
  String _selectedTemplate = 'chronological';
  bool _isLoading = false;

  // Template options
  final List<Map<String, String>> _templates = [
    {
      'value': 'chronological',
      'name': 'Chronological',
      'description': 'Traditional format emphasizing work history in reverse chronological order. Best for those with consistent career progression.',
    },
    {
      'value': 'functional',
      'name': 'Functional',
      'description': 'Skills-based format emphasizing competencies over work timeline. Best for career changers or those with employment gaps.',
    },
  ];

  @override
  void dispose() {
    _nameController.dispose();
    _educationController.dispose();
    _experienceController.dispose();
    _skillsController.dispose();
    super.dispose();
  }

  Future<void> _generateResume() async {
    if (_formKey.currentState!.validate()) {
      setState(() {
        _isLoading = true;
        _generatedResume = null;
      });

      try {
        final result = await _apiService.generateResume(
          name: _nameController.text,
          education: _educationController.text,
          experience: _experienceController.text,
          skills: _skillsController.text,
          template: _selectedTemplate,
        );

        setState(() {
          _generatedResume = result['resume'];
          _isLoading = false;
        });
      } catch (e) {
        setState(() {
          _isLoading = false;
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error: ${e.toString()}'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: const Text('AI Resume Builder'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        'Enter Your Information',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _nameController,
                        decoration: const InputDecoration(
                          labelText: 'Name',
                          border: OutlineInputBorder(),
                          hintText: 'John Doe',
                        ),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Please enter your name';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _educationController,
                        decoration: const InputDecoration(
                          labelText: 'Education',
                          border: OutlineInputBorder(),
                          hintText: 'Bachelor of Science in Computer Science, XYZ University, 2020',
                        ),
                        maxLines: 3,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Please enter your education';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _experienceController,
                        decoration: const InputDecoration(
                          labelText: 'Experience',
                          border: OutlineInputBorder(),
                          hintText: 'Software Engineer at ABC Corp (2020-2023): Developed web applications...',
                        ),
                        maxLines: 5,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Please enter your experience';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _skillsController,
                        decoration: const InputDecoration(
                          labelText: 'Skills',
                          border: OutlineInputBorder(),
                          hintText: 'Python, JavaScript, React, Node.js',
                        ),
                        maxLines: 2,
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Please enter your skills';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 24),
                      Text(
                        'Select Resume Template',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: 8),
                      DropdownButtonFormField<String>(
                        value: _selectedTemplate,
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                          contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        ),
                        items: _templates.map((template) {
                          return DropdownMenuItem<String>(
                            value: template['value'],
                            child: Text(template['name']!),
                          );
                        }).toList(),
                        onChanged: (value) {
                          setState(() {
                            _selectedTemplate = value!;
                          });
                        },
                      ),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.blue.shade50,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.blue.shade200),
                        ),
                        child: Text(
                          _templates.firstWhere(
                            (t) => t['value'] == _selectedTemplate,
                          )['description']!,
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.blue.shade900,
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      ElevatedButton(
                        onPressed: _isLoading ? null : _generateResume,
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.all(16),
                        ),
                        child: _isLoading
                            ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Text(
                                'Generate Resume',
                                style: TextStyle(fontSize: 16),
                              ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            if (_generatedResume != null) ...[
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Generated Resume',
                            style: Theme.of(context).textTheme.headlineSmall,
                          ),
                          Chip(
                            label: Text(
                              _templates.firstWhere(
                                (t) => t['value'] == _selectedTemplate,
                              )['name']!,
                              style: const TextStyle(fontSize: 12),
                            ),
                            backgroundColor: Colors.blue.shade100,
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.grey.shade300),
                        ),
                        child: MarkdownBody(
                          data: _generatedResume!,
                          styleSheet: MarkdownStyleSheet(
                            h1: const TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                              color: Colors.black87,
                            ),
                            h2: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Colors.black87,
                            ),
                            p: const TextStyle(
                              fontSize: 14,
                              color: Colors.black87,
                              height: 1.5,
                            ),
                            listBullet: const TextStyle(
                              fontSize: 14,
                              color: Colors.black87,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
