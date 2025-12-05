import 'package:flutter/material.dart';
import '../services/local_store.dart';

/// Dialog for managing drafts (list, load, rename, delete).
/// Shared widget used by both Resume and Cover Letter screens.
class DraftsDialog extends StatefulWidget {
  final LocalStoreService store;
  final String draftType;
  final void Function(Draft) onLoad;

  const DraftsDialog({
    super.key,
    required this.store,
    required this.draftType,
    required this.onLoad,
  });

  @override
  State<DraftsDialog> createState() => _DraftsDialogState();
}

class _DraftsDialogState extends State<DraftsDialog> {
  late List<Draft> _drafts;

  @override
  void initState() {
    super.initState();
    _loadDrafts();
  }

  void _loadDrafts() {
    setState(() {
      _drafts = widget.store.getDraftsByType(widget.draftType);
      _drafts.sort((a, b) => b.updatedAt.compareTo(a.updatedAt));
    });
  }

  void _deleteDraft(Draft draft) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Draft'),
        content: Text('Are you sure you want to delete "${draft.title}"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('CANCEL'),
          ),
          TextButton(
            onPressed: () {
              widget.store.deleteDraft(draft.id);
              _loadDrafts();
              Navigator.of(ctx).pop();
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('DELETE'),
          ),
        ],
      ),
    );
  }

  void _renameDraft(Draft draft) {
    final controller = TextEditingController(text: draft.title);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Rename Draft'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            labelText: 'Title',
            border: OutlineInputBorder(),
          ),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('CANCEL'),
          ),
          TextButton(
            onPressed: () {
              final newTitle = controller.text.trim();
              if (newTitle.isNotEmpty) {
                widget.store.renameDraft(draft.id, newTitle);
                _loadDrafts();
              }
              Navigator.of(ctx).pop();
            },
            child: const Text('SAVE'),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);
    if (diff.inDays == 0) {
      return 'Today ${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
    } else if (diff.inDays == 1) {
      return 'Yesterday';
    } else if (diff.inDays < 7) {
      return '${diff.inDays} days ago';
    } else {
      return '${date.month}/${date.day}/${date.year}';
    }
  }

  @override
  Widget build(BuildContext context) {
    final typeLabel = widget.draftType == 'resume' ? 'Resume' : 'Cover Letter';
    
    return AlertDialog(
      title: Row(
        children: [
          const Icon(Icons.folder_open),
          const SizedBox(width: 8),
          Text('My $typeLabel Drafts'),
        ],
      ),
      content: SizedBox(
        width: 400,
        height: 300,
        child: _drafts.isEmpty
            ? const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.inbox_outlined, size: 48, color: Colors.grey),
                    SizedBox(height: 16),
                    Text(
                      'No drafts saved yet',
                      style: TextStyle(color: Colors.grey, fontSize: 16),
                    ),
                    SizedBox(height: 8),
                    Text(
                      'Click "Save Draft" to save your work.',
                      style: TextStyle(color: Colors.grey),
                    ),
                  ],
                ),
              )
            : ListView.builder(
                itemCount: _drafts.length,
                itemBuilder: (ctx, index) {
                  final draft = _drafts[index];
                  return Card(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: ListTile(
                      title: Text(
                        draft.title,
                        overflow: TextOverflow.ellipsis,
                      ),
                      subtitle: Text(
                        'Updated: ${_formatDate(draft.updatedAt)}',
                        style: const TextStyle(fontSize: 12),
                      ),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          IconButton(
                            icon: const Icon(Icons.edit, size: 20),
                            tooltip: 'Rename',
                            onPressed: () => _renameDraft(draft),
                          ),
                          IconButton(
                            icon: const Icon(Icons.delete, size: 20, color: Colors.red),
                            tooltip: 'Delete',
                            onPressed: () => _deleteDraft(draft),
                          ),
                        ],
                      ),
                      onTap: () => widget.onLoad(draft),
                    ),
                  );
                },
              ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('CLOSE'),
        ),
      ],
    );
  }
}
