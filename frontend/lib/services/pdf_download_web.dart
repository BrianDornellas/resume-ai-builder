import 'dart:html' as html;
import 'dart:typed_data';

/// Utility functions for PDF download in Flutter Web.
/// 
/// Note: This module uses dart:html which is web-only.
/// For cross-platform support, use conditional imports.

/// Sanitizes a name string for use in filenames.
/// Removes special characters and replaces them with underscores.
String sanitizeFilename(String name) {
  return name.replaceAll(RegExp(r'[^a-zA-Z0-9]'), '_');
}

/// Generates a filename with the given prefix, name, and current date.
/// Format: {prefix}_{name}_{YYYYMMDD}.pdf
String generatePdfFilename(String prefix, String name) {
  final sanitizedName = sanitizeFilename(name.trim());
  final date = DateTime.now().toIso8601String().substring(0, 10).replaceAll('-', '');
  return '${prefix}_${sanitizedName}_$date.pdf';
}

/// Triggers a browser download for the given PDF bytes.
/// Uses the HTML5 download attribute to prompt the user to save the file.
void downloadPdfInBrowser(Uint8List pdfBytes, String filename) {
  final blob = html.Blob([pdfBytes], 'application/pdf');
  final url = html.Url.createObjectUrlFromBlob(blob);
  html.AnchorElement(href: url)
    ..setAttribute('download', filename)
    ..click();
  html.Url.revokeObjectUrl(url);
}
