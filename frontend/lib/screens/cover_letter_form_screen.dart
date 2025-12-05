import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_client.dart';
import '../services/pdf_download_web.dart';

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

  // PDF export state
  bool _exporting = false;
  String _pdfTemplate = 'classic';
  final List<Map<String, String>> _pdfTemplates = [
    {'value': 'classic', 'name': 'Classic'},
    {'value': 'modern', 'name': 'Modern'},
  ];

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

  Future<void> _exportPdf() async {
    if (_coverLetter == null || _coverLetter!.isEmpty) return;
    
    setState(() {
      _exporting = true;
    });
    
    try {
      final pdfBytes = await ApiClient().exportPdf(
        documentType: 'cover_letter',
        content: _coverLetter!,
        template: _pdfTemplate,
      );
      
      // Generate filename and trigger download
      final filename = generatePdfFilename('cover', _nameController.text);
      downloadPdfInBrowser(pdfBytes, filename);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('PDF downloaded: $filename'),
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Failed to export PDF: $e';
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          _exporting = false;
        });
      }
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
                      const SizedBox(width: 16),
                      // PDF Export dropdown button
                      Container(
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(20),
                          color: Theme.of(context).colorScheme.primaryContainer,
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            ElevatedButton.icon(
                              onPressed: _exporting ? null : _exportPdf,
                              icon: _exporting
                                  ? const SizedBox(
                                      width: 16,
                                      height: 16,
                                      child: CircularProgressIndicator(strokeWidth: 2),
                                    )
                                  : const Icon(Icons.picture_as_pdf),
                              label: const Text('Download PDF'),
                              style: ElevatedButton.styleFrom(
                                shape: const RoundedRectangleBorder(
                                  borderRadius: BorderRadius.horizontal(left: Radius.circular(20)),
                                ),
                              ),
                            ),
                            PopupMenuButton<String>(
                              initialValue: _pdfTemplate,
                              onSelected: (value) {
                                setState(() => _pdfTemplate = value);
                              },
                              itemBuilder: (context) => _pdfTemplates
                                  .map((t) => PopupMenuItem<String>(
                                        value: t['value'],
                                        child: Row(
                                          children: [
                                            if (_pdfTemplate == t['value'])
                                              const Icon(Icons.check, size: 18)
                                            else
                                              const SizedBox(width: 18),
                                            const SizedBox(width: 8),
                                            Text(t['name']!),
                                          ],
                                        ),
                                      ))
                                  .toList(),
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Text(
                                      _pdfTemplates.firstWhere((t) => t['value'] == _pdfTemplate)['name']!,
                                      style: TextStyle(
                                        color: Theme.of(context).colorScheme.primary,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                    Icon(
                                      Icons.arrow_drop_down,
                                      color: Theme.of(context).colorScheme.primary,
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
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
