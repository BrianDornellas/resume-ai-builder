import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_client.dart';
import '../services/pdf_download_web.dart';

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
  bool _optimizing = false;
  Map<String, dynamic>? _optResult;
  String? _optError;
  bool _optMock = false;

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
    _educationController.dispose();
    _experienceController.dispose();
    _skillsController.dispose();
    _jdController.dispose();
    super.dispose();
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

  Future<void> _analyzeMatch() async {
    setState(() {
      _optimizing = true;
      _optResult = null;
      _optError = null;
      _optMock = false;
    });
    if (_resume == null || _resume!.trim().isEmpty || _jdController.text.trim().isEmpty) {
      setState(() {
        _optimizing = false;
        _optError = 'Please generate a resume and enter a job description.';
      });
      return;
    }
    try {
      final result = await ApiClient().optimizeResume(
        resumeText: _resume!,
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
        _optError = 'Network error: $e';
      });
    } finally {
      setState(() {
        _optimizing = false;
      });
    }
  }

  Future<void> _exportPdf() async {
    if (_resume == null || _resume!.isEmpty) return;
    
    setState(() {
      _exporting = true;
    });
    
    try {
      final pdfBytes = await ApiClient().exportPdf(
        documentType: 'resume',
        content: _resume!,
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
            // --- Resume Template Dropdown ---
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Resume Template', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
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
              ],
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Name',
                hintText: 'e.g. Jane Doe',
              ),
              validator: (v) => v == null || v.trim().isEmpty ? 'Name is required' : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _educationController,
              decoration: const InputDecoration(
                labelText: 'Education',
                hintText: 'e.g. B.S. in Computer Science, University of X',
              ),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _experienceController,
              decoration: const InputDecoration(
                labelText: 'Experience',
                hintText: 'e.g. 3 years at Acme Corp as Software Engineer',
              ),
              minLines: 2,
              maxLines: 4,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _skillsController,
              decoration: const InputDecoration(
                labelText: 'Skills (comma or multiline)',
                hintText: 'e.g. Python, Flutter, Project Management',
              ),
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
                  : const Text('Generate Resume'),
            ),
            const SizedBox(height: 24),
            if (_resume != null)
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    'Generated Resume:',
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
                      _resume!,
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
                          await Clipboard.setData(ClipboardData(text: _resume!));
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
                  const SizedBox(height: 32),
                  // --- Optimize for Job Posting Panel ---
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.blue[50],
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: Colors.blue.shade100),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.tune, color: Colors.blue),
                            const SizedBox(width: 8),
                            const Text('Optimize for Job Posting', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                            if (_optMock)
                              Container(
                                margin: const EdgeInsets.only(left: 10),
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                decoration: BoxDecoration(
                                  color: Colors.orange[100],
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: const Text('Mock Mode', style: TextStyle(color: Colors.orange, fontWeight: FontWeight.bold, fontSize: 12)),
                              ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        TextField(
                          controller: _jdController,
                          minLines: 3,
                          maxLines: 8,
                          decoration: const InputDecoration(
                            labelText: 'Job Description',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        const SizedBox(height: 12),
                        ElevatedButton(
                          onPressed: _optimizing ? null : _analyzeMatch,
                          child: _optimizing
                              ? const SizedBox(
                                  width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : const Text('Analyze Match'),
                        ),
                        const SizedBox(height: 16),
                        if (_optError != null)
                          Text(_optError!, style: const TextStyle(color: Colors.red)),
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
                                        .map<Widget>((s) => Row(children: [const Text('• '), Expanded(child: Text(s.toString()))]))
                                        .toList(),
                                    const SizedBox(height: 10),
                                  ],
                                ),
                              if ((_optResult!['missing_keywords'] as List?)?.isNotEmpty ?? false)
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text('Missing Keywords:', style: TextStyle(fontWeight: FontWeight.bold)),
                                    const SizedBox(height: 4),
                                    Wrap(
                                      spacing: 6,
                                      runSpacing: 6,
                                      children: (_optResult!['missing_keywords'] as List)
                                          .map<Widget>((kw) => Chip(label: Text(kw.toString())))
                                          .toList(),
                                    ),
                                    const SizedBox(height: 10),
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
                                        .map((l) => Row(children: [const Text('• '), Expanded(child: Text(l.trim()))]))
                                        .toList(),
                                  ],
                                ),
                            ],
                          ),
                      ],
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
