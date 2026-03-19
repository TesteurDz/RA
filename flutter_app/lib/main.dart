import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'core/theme.dart';
import 'screens/main_shell.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
    systemNavigationBarColor: Color(0xFF0F0F14),
  ));
  runApp(const RAApp());
}

class RAApp extends StatelessWidget {
  const RAApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RA - Reputation Analyzer',
      debugShowCheckedModeBanner: false,
      theme: appTheme,
      home: const MainShell(),
    );
  }
}
