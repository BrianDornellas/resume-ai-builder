import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_client.dart';
import '../services/pdf_download_web.dart';
import '../services/local_store.dart';
import '../widgets/drafts_dialog.dart';

/// Helper to remove leading dash and whitespace from suggestion text.
String _cleanSuggestionText(String text) {
  return text.replaceFirst(RegExp(r'^-\s*'), '').trim();
}

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
  late final TextEditingController _resumeEditorController;

  bool _loading = false;
  String? _resume;
  String? _error;
  bool _copied = false;

  // Template selection state
  String _selectedTemplate = 'chronological';
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

  // Optimization panel state
  final _jdController = TextEditingController();
  final _extraDetailsController = TextEditingController();
  bool _optimizing = false;
  Map<String, dynamic>? _optResult;
  String? _optError;
  bool _optMock = false;
  bool _applyingSuggestions = false;

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
  void initState() {
    super.initState();
    _resumeEditorController = TextEditingController();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _educationController.dispose();
    _experienceController.dispose();
    _skillsController.dispose();
    _jdController.dispose();
    _extraDetailsController.dispose();
    _resumeEditorController.dispose();
    super.dispose();
  }

  /// Collects current form data into a map for draft storage.
  Map<String, dynamic> _collectFormData() {
    return {
      'name': _nameController.text,
      'education': _educationController.text,
      'experience': _experienceController.text,
      'skills': _skillsController.text,
      'template': _selectedTemplate,
      'generatedResume': _resumeEditorController.text,
    };
  }

  /// Populates form fields from draft content.
  void _loadFormData(Map<String, dynamic> content) {
    _nameController.text = content['name'] ?? '';
    _educationController.text = content['education'] ?? '';
    _experienceController.text = content['experience'] ?? '';
    _skillsController.text = content['skills'] ?? '';
    _selectedTemplate = content['template'] ?? 'chronological';
    _resume = (content['generatedResume'] ?? '') as String;
    _resumeEditorController.text = _resume ?? '';
  }

  Future<void> _saveDraft() async {
    final name = _nameController.text.trim();
    final title = name.isEmpty ? 'Untitled Resume' : '$name\'s Resume';
    final content = _collectFormData();

    if (_currentDraftId != null) {
      _store.updateDraftContent(_currentDraftId!, content);
      _store.renameDraft(_currentDraftId!, title);
    } else {
      final draft = _store.createDraft(
        type: 'resume',
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
        draftType: 'resume',
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
      _resume = null;
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
      final result = await ApiClient().generateResume(
        name: _nameController.text.trim(),
        education: _educationController.text.trim(),
        experience: _experienceController.text.trim(),
        skills: _skillsController.text.trim(),
        template: _selectedTemplate,
      );
      if (result['success'] == true) {
        setState(() {
          _resume = result['resume'] as String?;
          // Sync the editor controller with the generated resume
          _resumeEditorController.text = _resume ?? '';
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

  Future<void> _analyzeMatch() async {
    setState(() {
      _optimizing = true;
      _optResult = null;
      _optError = null;
      _optMock = false;
    });
    final resumeText = _resumeEditorController.text.trim();
    if (resumeText.isEmpty || _jdController.text.trim().isEmpty) {
      setState(() {
        _optimizing = false;
        _optError = 'Please generate a resume and enter a job description.';
      });
      return;
    }
    try {
      final result = await ApiClient().optimizeResume(
        resumeText: resumeText,
        jobDescription: _jdController.text.trim(),
      );
      setState(() {
        _optResult = result;
        _optError = null;
        _optMock = (result['suggested_edits'] != null && (result['suggested_edits'] as String).contains('Highlight more relevant skills')) ||
            (result['missing_keywords'] is List && (result['missing_keywords'] as List).isNotEmpty && (result['strengths'] as List).isEmpty);
      });
    } catch (e) {
      setState(() {
        _optError = 'Network error: Unable to analyze. Please try again.';
      });
    } finally {
      setState(() {
        _optimizing = false;
      });
    }
  }

  Future<void> _applySuggestions() async {
    // Validate that we have optimization results first
    if (_optResult == null || _optResult?['suggested_edits'] == null) {
      setState(() {
        _optError = 'Please analyze the resume first before applying suggestions.';
      });
      return;
    }
    
    setState(() {
      _applyingSuggestions = true;
      _optError = null;
    });
    
    final resumeText = _resumeEditorController.text.trim();
    final jobDescription = _jdController.text.trim();
    final suggestedEdits = (_optResult!['suggested_edits'] as String?) ?? '';
    final extraDetails = _extraDetailsController.text.trim();
    
    if (resumeText.isEmpty || jobDescription.isEmpty || suggestedEdits.isEmpty) {
      setState(() {
        _applyingSuggestions = false;
        _optError = 'Please generate a resume and analyze it first before applying suggestions.';
      });
      return;
    }
    
    try {
      final result = await ApiClient().improveResume(
        resumeText: resumeText,
        jobDescription: jobDescription,
        suggestedEdits: suggestedEdits,
        extraDetails: extraDetails,
      );
      
      if (result['success'] == true && result['improved_resume'] != null) {
        setState(() {
          // Update the resume editor with the improved version
          _resumeEditorController.text = result['improved_resume'] as String;
          _resume = result['improved_resume'] as String;
        });
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Resume improved successfully! Review the changes in the editor.'),
              backgroundColor: Colors.green,
              duration: Duration(seconds: 3),
            ),
          );
        }
      } else {
        setState(() {
          _optError = result['error']?.toString() ?? 'Failed to improve resume.';
        });
      }
    } catch (e) {
      setState(() {
        _optError = 'Network error: Unable to improve resume. Please try again.';
      });
    } finally {
      setState(() {
        _applyingSuggestions = false;
      });
    }
  }
  }

  Future<void> _exportPdf() async {
    // Use edited text from controller, fallback to _resume if controller is empty
    final editedText = _resumeEditorController.text.trim();
    final content = editedText.isNotEmpty ? editedText : _resume;
    
    if (content == null || content.isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('No resume content to export. Please generate a resume first.'),
            backgroundColor: Colors.orange,
            duration: Duration(seconds: 3),
          ),
        );
      }
      return;
    }
    
    setState(() {
      _exporting = true;
    });
    
    try {
      final pdfBytes = await ApiClient().exportPdf(
        documentType: 'resume',
        content: content,
        template: _pdfTemplate,
      );
      
      // Generate filename and trigger download
      final filename = generatePdfFilename('resume', _nameController.text);
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
                  'Create Your Resume',
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
              'Fill in your details below to generate a professional resume.',
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

            // --- Resume Template Section ---
            const Text(
              'Resume Template',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _selectedTemplate,
              items: _templates
                  .map((t) => DropdownMenuItem<String>(
                        value: t['value'],
                        child: Text(t['name']!),
                      ))
                  .toList(),
              onChanged: (val) {
                if (val != null) setState(() => _selectedTemplate = val);
              },
              decoration: const InputDecoration(border: OutlineInputBorder()),
            ),
            const SizedBox(height: 4),
            Text(
              _templates.firstWhere((t) => t['value'] == _selectedTemplate)['description']!,
              style: const TextStyle(fontSize: 12, color: Colors.black54),
            ),
            const SizedBox(height: 24),

            // --- Personal Information Section ---
            const Text(
              'Personal Information',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Full Name *',
                hintText: 'e.g. Jane Doe',
                border: OutlineInputBorder(),
              ),
              validator: (v) => v == null || v.trim().isEmpty ? 'Name is required' : null,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _educationController,
              decoration: const InputDecoration(
                labelText: 'Education',
                hintText: 'e.g. B.S. in Computer Science, University of X',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 24),

            // --- Experience Section ---
            const Text(
              'Work Experience',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _experienceController,
              decoration: const InputDecoration(
                labelText: 'Experience',
                hintText: 'e.g. 3 years at Acme Corp as Software Engineer',
                border: OutlineInputBorder(),
              ),
              minLines: 3,
              maxLines: 6,
            ),
            const SizedBox(height: 24),

            // --- Skills Section ---
            const Text(
              'Skills',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _skillsController,
              decoration: const InputDecoration(
                labelText: 'Skills (comma separated)',
                hintText: 'e.g. Python, Flutter, Project Management',
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
                    : const Text('Generate Resume', style: TextStyle(fontSize: 16)),
              ),
            ),
            const SizedBox(height: 32),

            // --- Generated Resume Section ---
            if (_resume != null)
              _buildGeneratedResumeSection()
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
          Icon(Icons.description_outlined, size: 48, color: Colors.grey),
          SizedBox(height: 16),
          Text(
            'No Resume Generated Yet',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500, color: Colors.grey),
          ),
          SizedBox(height: 8),
          Text(
            'Fill in your details above and click "Generate Resume" to create your professional resume.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }

  Widget _buildGeneratedResumeSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Header with actions
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Generated Resume',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
            Row(
              children: [
                // Copy button
                TextButton.icon(
                  onPressed: () async {
                    await Clipboard.setData(ClipboardData(text: _resumeEditorController.text));
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

        // Resume editor - Editable multiline text field
        TextField(
          controller: _resumeEditorController,
          minLines: 10,
          maxLines: null,
          keyboardType: TextInputType.multiline,
          decoration: const InputDecoration(
            labelText: 'Edit Resume (Markdown)',
            border: OutlineInputBorder(),
            alignLabelWithHint: true,
          ),
          style: const TextStyle(fontFamily: 'monospace', height: 1.5),
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
        const SizedBox(height: 32),

        // --- Optimize for Job Posting Panel ---
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.blue[50],
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.blue.shade100),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  const Icon(Icons.tune, color: Colors.blue),
                  const SizedBox(width: 8),
                  const Text(
                    'Optimize for Job Posting',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  if (_optMock)
                    Container(
                      margin: const EdgeInsets.only(left: 10),
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.orange[100],
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: const Text(
                        'Mock Mode',
                        style: TextStyle(color: Colors.orange, fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 8),
              const Text(
                'Paste a job description to get suggestions for improving your resume.',
                style: TextStyle(color: Colors.black54, fontSize: 13),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _jdController,
                minLines: 3,
                maxLines: 8,
                decoration: const InputDecoration(
                  labelText: 'Job Description',
                  hintText: 'Paste the job description here...',
                  border: OutlineInputBorder(),
                  filled: true,
                  fillColor: Colors.white,
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                height: 44,
                child: ElevatedButton(
                  onPressed: _optimizing ? null : _analyzeMatch,
                  child: _optimizing
                      ? const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            ),
                            SizedBox(width: 12),
                            Text('Analyzing...'),
                          ],
                        )
                      : const Text('Analyze Match'),
                ),
              ),
              const SizedBox(height: 16),
              if (_optError != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red[50],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error_outline, color: Colors.red, size: 18),
                      const SizedBox(width: 8),
                      Expanded(child: Text(_optError!, style: const TextStyle(color: Colors.red))),
                      TextButton(
                        onPressed: _analyzeMatch,
                        child: const Text('RETRY'),
                      ),
                    ],
                  ),
                ),
              if (_optResult != null)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if ((_optResult!['strengths'] as List?)?.isNotEmpty ?? false)
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Strengths:', style: TextStyle(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 4),
                          ...(_optResult!['strengths'] as List)
                              .map<Widget>((s) => Padding(
                                    padding: const EdgeInsets.only(left: 8, bottom: 4),
                                    child: Row(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        const Text('• '),
                                        Expanded(child: Text(s.toString())),
                                      ],
                                    ),
                                  ))
                              .toList(),
                          const SizedBox(height: 12),
                        ],
                      ),
                    if ((_optResult!['missing_keywords'] as List?)?.isNotEmpty ?? false)
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Missing Keywords:', style: TextStyle(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 8),
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: (_optResult!['missing_keywords'] as List)
                                .map<Widget>((kw) => Chip(
                                      label: Text(kw.toString()),
                                      backgroundColor: Colors.orange[50],
                                    ))
                                .toList(),
                          ),
                          const SizedBox(height: 12),
                        ],
                      ),
                    if ((_optResult!['suggested_edits'] as String?)?.isNotEmpty ?? false)
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Suggested Edits:', style: TextStyle(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 4),
                          ...((_optResult!['suggested_edits'] as String)
                                  .split('\n')
                                  .where((l) => l.trim().isNotEmpty))
                              .map((l) => Padding(
                                    padding: const EdgeInsets.only(left: 8, bottom: 4),
                                    child: Row(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        const Text('• '),
                                        Expanded(child: Text(_cleanSuggestionText(l))),
                                      ],
                                    ),
                                  ))
                              .toList(),
                        ],
                      ),
                    // Extra details and Apply button
                    const SizedBox(height: 16),
                    const Divider(),
                    const SizedBox(height: 16),
                    const Text(
                      'Optional: Provide Additional Context',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Add any extra details (e.g., relevant coursework, projects, certifications) that the AI can use when improving your resume.',
                      style: TextStyle(color: Colors.black54, fontSize: 12),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _extraDetailsController,
                      minLines: 2,
                      maxLines: 5,
                      decoration: const InputDecoration(
                        labelText: 'Extra Details (Optional)',
                        hintText: 'e.g., Completed coursework in Machine Learning, built a portfolio website...',
                        border: OutlineInputBorder(),
                        filled: true,
                        fillColor: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      height: 44,
                      child: ElevatedButton.icon(
                        onPressed: _applyingSuggestions ? null : _applySuggestions,
                        icon: _applyingSuggestions
                            ? const SizedBox(
                                width: 18,
                                height: 18,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.auto_fix_high, size: 20),
                        label: Text(_applyingSuggestions ? 'Applying...' : 'Apply Suggestions with AI'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.green,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                  ],
                ),
            ],
          ),
        ),
      ],
    );
  }
}
