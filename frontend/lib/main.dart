import 'package:flutter/material.dart';
import 'screens/resume_form_screen.dart';
import 'screens/cover_letter_form_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Resume Builder',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const HomeTabs(),
    );
  }
}

class HomeTabs extends StatefulWidget {
  const HomeTabs({super.key});

  @override
  State<HomeTabs> createState() => _HomeTabsState();
}

class _HomeTabsState extends State<HomeTabs> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Resume Builder'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Resume'),
            Tab(text: 'Cover Letter'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [
          ResumeFormScreen(),
          CoverLetterFormScreen(),
        ],
      ),
    );
  }
}
