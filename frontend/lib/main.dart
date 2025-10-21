import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: const Text('AI Resume Builder')),
        body: const ResumePage(),
      ),
    );
  }
}

class ResumePage extends StatefulWidget {
  const ResumePage({super.key});
  @override
  State<ResumePage> createState() => _ResumePageState();
}

class _ResumePageState extends State<ResumePage> {
  String responseText = "";

  Future<void> callBackend() async {
    final response = await http.post(
      Uri.parse("http://127.0.0.1:8000/generate_resume"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"name": "Brian Dornellas", "skills": ["Java", "C++"]}),
    );

    setState(() {
      responseText = response.body;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ElevatedButton(
          onPressed: callBackend,
          child: const Text("Generate Resume"),
        ),
        Text(responseText),
      ],
    );
  }
}
