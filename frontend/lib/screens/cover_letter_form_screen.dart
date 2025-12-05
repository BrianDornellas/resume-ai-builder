import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_client.dart';
import '../services/pdf_download_web.dart';
import '../services/local_store.dart';
import '../widgets/drafts_dialog.dart';

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

  // Drafts state
  final LocalStoreService _store = LocalStoreService();
  String? _currentDraftId;

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

  /// Collects current form data into a map for draft storage.
  Map<String, dynamic> _collectFormData() {
    return {
      'name': _nameController.text,
      'company': _companyController.text,
      'role': _roleController.text,
      'jobDescription': _jobDescController.text,
      'experience': _experienceController.text,
      'skills': _skillsController.text,
      'generatedCoverLetter': _coverLetter,
    };
  }

  /// Populates form fields from draft content.
  void _loadFormData(Map<String, dynamic> content) {
    _nameController.text = content['name'] ?? '';
    _companyController.text = content['company'] ?? '';
    _roleController.text = content['role'] ?? '';
    _jobDescController.text = content['jobDescription'] ?? '';
    _experienceController.text = content['experience'] ?? '';
    _skillsController.text = content['skills'] ?? '';
    _coverLetter = content['generatedCoverLetter'];
  }

  Future<void> _saveDraft() async {
    final company = _companyController.text.trim();
    final role = _roleController.text.trim();
    String title;
    if (company.isNotEmpty && role.isNotEmpty) {
      title = '$role at $company';
    } else if (company.isNotEmpty) {
      title = 'Cover Letter - $company';
    } else {
      title = 'Untitled Cover Letter';
    }
    
    final content = _collectFormData();

    if (_currentDraftId != null) {
      _store.updateDraftContent(_currentDraftId!, content);
      _store.renameDraft(_currentDraftId!, title);
    } else {
      final draft = _store.createDraft(
        type: 'cover_letter',
        title: title,
        content: content,
      );
      _currentDraftId = draft.id;
    }

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Draft saved successfully'),
          backgroundColor: Colors.green,
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  void _showDraftsDialog() {
    showDialog(
      context: context,
      builder: (ctx) => DraftsDialog(
        store: _store,
        draftType: 'cover_letter',
        onLoad: (draft) {
          setState(() {
            _currentDraftId = draft.id;
            _loadFormData(draft.content);
            _error = null;
            _copied = false;
          });
          Navigator.of(ctx).pop();
        },
      ),
    );
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
        _error = 'Network error: Unable to connect to server. Please check your connection and try again.';
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
          _error = 'Failed to export PDF. Please try again.';
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
      padding: const EdgeInsets.all(24),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // --- Header with Drafts Button ---
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Create Your Cover Letter',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                Row(
                  children: [
                    OutlinedButton.icon(
                      onPressed: _showDraftsDialog,
                      icon: const Icon(Icons.folder_open, size: 18),
                      label: const Text('My Drafts'),
                    ),
                    const SizedBox(width: 8),
                    ElevatedButton.icon(
                      onPressed: _saveDraft,
                      icon: const Icon(Icons.save, size: 18),
                      label: const Text('Save Draft'),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Text(
              'Fill in your details below to generate a professional cover letter.',
              style: TextStyle(color: Colors.black54),
            ),
            const SizedBox(height: 24),

            // --- Error Banner with Retry ---
            if (_error != null)
              Container(
                margin: const EdgeInsets.only(bottom: 16),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.shade200),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: Colors.red),
                    const SizedBox(width: 12),
                    Expanded(child: Text(_error!, style: const TextStyle(color: Colors.red))),
                    TextButton(
                      onPressed: _submit,
                      child: const Text('RETRY'),
                    ),
                    IconButton(
                      icon: const Icon(Icons.close, size: 18),
                      onPressed: () => setState(() => _error = null),
                    ),
                  ],
                ),
              ),

            // --- Personal Information Section ---
            const Text(
              'Personal Information',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Your Full Name *',
                hintText: 'e.g. Jane Doe',
                border: OutlineInputBorder(),
              ),
              validator: (v) => v == null || v.trim().isEmpty ? 'Name is required' : null,
            ),
            const SizedBox(height: 24),

            // --- Job Details Section ---
            const Text(
              'Job Details',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _companyController,
              decoration: const InputDecoration(
                labelText: 'Company Name *',
                hintText: 'e.g. Acme Corporation',
                border: OutlineInputBorder(),
              ),
              validator: (v) => v == null || v.trim().isEmpty ? 'Company is required' : null,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _roleController,
              decoration: const InputDecoration(
                labelText: 'Position/Role *',
                hintText: 'e.g. Software Engineer',
                border: OutlineInputBorder(),
              ),
              validator: (v) => v == null || v.trim().isEmpty ? 'Role is required' : null,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _jobDescController,
              decoration: const InputDecoration(
                labelText: 'Job Description',
                hintText: 'Paste the job description here for a more tailored letter...',
                border: OutlineInputBorder(),
              ),
              minLines: 4,
              maxLines: 8,
            ),
            const SizedBox(height: 24),

            // --- Your Background Section ---
            const Text(
              'Your Background',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _experienceController,
              decoration: const InputDecoration(
                labelText: 'Relevant Experience',
                hintText: 'e.g. 5 years of experience in software development...',
                border: OutlineInputBorder(),
              ),
              minLines: 3,
              maxLines: 6,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _skillsController,
              decoration: const InputDecoration(
                labelText: 'Key Skills (comma separated)',
                hintText: 'e.g. Python, JavaScript, Project Management',
                border: OutlineInputBorder(),
              ),
              minLines: 2,
              maxLines: 4,
            ),
            const SizedBox(height: 24),

            // --- Generate Button ---
            SizedBox(
              height: 48,
              child: ElevatedButton(
                onPressed: _loading ? null : _submit,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Theme.of(context).colorScheme.primary,
                  foregroundColor: Colors.white,
                ),
                child: _loading
                    ? const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                          ),
                          SizedBox(width: 12),
                          Text('Generating...'),
                        ],
                      )
                    : const Text('Generate Cover Letter', style: TextStyle(fontSize: 16)),
              ),
            ),
            const SizedBox(height: 32),

            // --- Generated Cover Letter Section ---
            if (_coverLetter != null)
              _buildGeneratedLetterSection()
            else
              _buildEmptyState(),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: const Column(
        children: [
          Icon(Icons.mail_outline, size: 48, color: Colors.grey),
          SizedBox(height: 16),
          Text(
            'No Cover Letter Generated Yet',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500, color: Colors.grey),
          ),
          SizedBox(height: 8),
          Text(
            'Fill in your details above and click "Generate Cover Letter" to create your personalized letter.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }

  Widget _buildGeneratedLetterSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Header with actions
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Generated Cover Letter',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
            Row(
              children: [
                // Copy button
                TextButton.icon(
                  onPressed: () async {
                    await Clipboard.setData(ClipboardData(text: _coverLetter!));
                    setState(() => _copied = true);
                    Future.delayed(const Duration(seconds: 2), () {
                      if (mounted) setState(() => _copied = false);
                    });
                  },
                  icon: Icon(_copied ? Icons.check : Icons.copy, size: 18),
                  label: Text(_copied ? 'Copied!' : 'Copy'),
                  style: TextButton.styleFrom(
                    foregroundColor: _copied ? Colors.green : null,
                  ),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Cover letter content
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.grey[50],
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.grey.shade200),
          ),
          child: SelectableText(
            _coverLetter!,
            style: const TextStyle(fontFamily: 'monospace', height: 1.5),
          ),
        ),
        const SizedBox(height: 16),

        // PDF Export Row
        Row(
          children: [
            Expanded(
              child: ElevatedButton.icon(
                onPressed: _exporting ? null : _exportPdf,
                icon: _exporting
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.picture_as_pdf),
                label: Text(_exporting ? 'Exporting...' : 'Download PDF'),
              ),
            ),
            const SizedBox(width: 12),
            Container(
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey.shade300),
                borderRadius: BorderRadius.circular(4),
              ),
              child: DropdownButton<String>(
                value: _pdfTemplate,
                underline: const SizedBox(),
                padding: const EdgeInsets.symmetric(horizontal: 12),
                items: _pdfTemplates
                    .map((t) => DropdownMenuItem<String>(
                          value: t['value'],
                          child: Text(t['name']!),
                        ))
                    .toList(),
                onChanged: (value) {
                  if (value != null) setState(() => _pdfTemplate = value);
                },
              ),
            ),
          ],
        ),
      ],
    );
  }
}
