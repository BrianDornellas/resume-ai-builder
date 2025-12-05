import 'dart:convert';
// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;

/// Represents a saved draft (resume or cover letter).
class Draft {
  final String id;
  final String type; // "resume" | "cover_letter"
  String title;
  final DateTime createdAt;
  DateTime updatedAt;
  Map<String, dynamic> content;

  Draft({
    required this.id,
    required this.type,
    required this.title,
    required this.createdAt,
    required this.updatedAt,
    required this.content,
  });

  factory Draft.create({
    required String type,
    required String title,
    required Map<String, dynamic> content,
  }) {
    final now = DateTime.now();
    return Draft(
      id: '${now.millisecondsSinceEpoch}_${type}',
      type: type,
      title: title,
      createdAt: now,
      updatedAt: now,
      content: content,
    );
  }

  factory Draft.fromJson(Map<String, dynamic> json) {
    return Draft(
      id: json['id'] as String,
      type: json['type'] as String,
      title: json['title'] as String,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
      content: Map<String, dynamic>.from(json['content'] as Map),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'title': title,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
      'content': content,
    };
  }

  Draft copyWith({
    String? title,
    Map<String, dynamic>? content,
    DateTime? updatedAt,
  }) {
    return Draft(
      id: id,
      type: type,
      title: title ?? this.title,
      createdAt: createdAt,
      updatedAt: updatedAt ?? DateTime.now(),
      content: content ?? this.content,
    );
  }
}

/// Service for managing drafts in browser localStorage.
/// Uses plain Dart (dart:html) with no external packages.
class LocalStoreService {
  static const String _storageKey = 'resume_ai_builder_drafts';

  /// Gets all saved drafts.
  List<Draft> getAllDrafts() {
    try {
      final stored = html.window.localStorage[_storageKey];
      if (stored == null || stored.isEmpty) {
        return [];
      }
      final List<dynamic> jsonList = jsonDecode(stored) as List<dynamic>;
      return jsonList
          .map((item) => Draft.fromJson(item as Map<String, dynamic>))
          .toList();
    } catch (e) {
      // If data is corrupted, return empty list
      return [];
    }
  }

  /// Gets drafts filtered by type.
  List<Draft> getDraftsByType(String type) {
    return getAllDrafts().where((d) => d.type == type).toList();
  }

  /// Saves a draft (creates new or updates existing).
  void saveDraft(Draft draft) {
    final drafts = getAllDrafts();
    final index = drafts.indexWhere((d) => d.id == draft.id);
    if (index >= 0) {
      drafts[index] = draft.copyWith(updatedAt: DateTime.now());
    } else {
      drafts.add(draft);
    }
    _persist(drafts);
  }

  /// Creates a new draft and saves it.
  Draft createDraft({
    required String type,
    required String title,
    required Map<String, dynamic> content,
  }) {
    final draft = Draft.create(type: type, title: title, content: content);
    saveDraft(draft);
    return draft;
  }

  /// Gets a draft by ID.
  Draft? getDraft(String id) {
    final drafts = getAllDrafts();
    final index = drafts.indexWhere((d) => d.id == id);
    return index >= 0 ? drafts[index] : null;
  }

  /// Deletes a draft by ID.
  bool deleteDraft(String id) {
    final drafts = getAllDrafts();
    final originalLength = drafts.length;
    drafts.removeWhere((d) => d.id == id);
    if (drafts.length < originalLength) {
      _persist(drafts);
      return true;
    }
    return false;
  }

  /// Renames a draft.
  bool renameDraft(String id, String newTitle) {
    final drafts = getAllDrafts();
    final index = drafts.indexWhere((d) => d.id == id);
    if (index >= 0) {
      drafts[index] = drafts[index].copyWith(title: newTitle);
      _persist(drafts);
      return true;
    }
    return false;
  }

  /// Updates a draft's content.
  bool updateDraftContent(String id, Map<String, dynamic> content) {
    final drafts = getAllDrafts();
    final index = drafts.indexWhere((d) => d.id == id);
    if (index >= 0) {
      drafts[index] = drafts[index].copyWith(content: content);
      _persist(drafts);
      return true;
    }
    return false;
  }

  /// Persists drafts to localStorage.
  void _persist(List<Draft> drafts) {
    final jsonList = drafts.map((d) => d.toJson()).toList();
    html.window.localStorage[_storageKey] = jsonEncode(jsonList);
  }

  /// Clears all drafts. Use with caution.
  void clearAll() {
    html.window.localStorage.remove(_storageKey);
  }
}
