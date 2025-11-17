import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_client.dart';

class CoverLetterFormScreen extends StatefulWidget {
  const CoverLetterFormScreen({super.key});

  @override
  State<CoverLetterFormScreen> createState() => _CoverLetterFormScreenState();
}

class _CoverLetterFormScreenState extends State<CoverLetterFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _companyController = TextEditingController();
  final _roleController = TextEditingController();
  final _jobDescController = TextEditingController();
  final _experienceController = TextEditingController();
  final _skillsController = TextEditingController();

  bool _loading = false;
  String? _coverLetter;
  String? _error;
  bool _copied = false;

  @override
  void dispose() {
    _nameController.dispose();
    _companyController.dispose();
    _roleController.dispose();
    _jobDescController.dispose();
    _experienceController.dispose();
    _skillsController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _loading = true;
      _coverLetter = null;
      _error = null;
      _copied = false;
    });
    if (!_formKey.currentState!.validate()) {
      setState(() {
        _loading = false;
      });
      return;
    }
    try {
      final result = await ApiClient().generateCoverLetter(
        name: _nameController.text.trim(),
        company: _companyController.text.trim(),
        role: _roleController.text.trim(),
        jobDescription: _jobDescController.text.trim(),
        experience: _experienceController.text.trim(),
        skills: _skillsController.text.trim(),
      );
      if (result['success'] == true) {
        setState(() {
          _coverLetter = result['cover_letter'] as String?;
        });
      } else {
        setState(() {
          _error = result['error']?.toString() ?? 'Unknown error';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Network error: $e';
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (_error != null)
              Container(
                margin: const EdgeInsets.only(bottom: 12),
                child: MaterialBanner(
                  content: Text(_error!),
                  backgroundColor: Colors.red[100],
                  actions: [
                    TextButton(
                      onPressed: () => setState(() => _error = null),
                      child: const Text('DISMISS'),
                    ),
                  ],
                ),
              ),
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(labelText: 'Name'),
              validator: (v) => v == null || v.trim().isEmpty ? 'Name is required' : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _companyController,
              decoration: const InputDecoration(labelText: 'Company'),
              validator: (v) => v == null || v.trim().isEmpty ? 'Company is required' : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _roleController,
              decoration: const InputDecoration(labelText: 'Role'),
              validator: (v) => v == null || v.trim().isEmpty ? 'Role is required' : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _jobDescController,
              decoration: const InputDecoration(labelText: 'Job Description'),
              minLines: 3,
              maxLines: 6,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _experienceController,
              decoration: const InputDecoration(labelText: 'Experience'),
              minLines: 2,
              maxLines: 4,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _skillsController,
              decoration: const InputDecoration(labelText: 'Skills (comma or multiline)'),
              minLines: 1,
              maxLines: 3,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _loading ? null : _submit,
              child: _loading
                  ? const SizedBox(
                      width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Generate Cover Letter'),
            ),
            const SizedBox(height: 24),
            if (_coverLetter != null)
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    'Generated Cover Letter:',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.grey[100],
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: SelectableText(
                      _coverLetter!,
                      style: const TextStyle(fontFamily: 'monospace'),
                      showCursor: true,
                      cursorWidth: 2,
                      cursorColor: Colors.blue,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      ElevatedButton.icon(
                        onPressed: () async {
                          await Clipboard.setData(ClipboardData(text: _coverLetter!));
                          setState(() => _copied = true);
                          Future.delayed(const Duration(seconds: 2), () {
                            if (mounted) setState(() => _copied = false);
                          });
                        },
                        icon: const Icon(Icons.copy),
                        label: const Text('Copy'),
                      ),
                      if (_copied)
                        const Padding(
                          padding: EdgeInsets.only(left: 12),
                          child: Text('Copied!', style: TextStyle(color: Colors.green)),
                        ),
                    ],
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
