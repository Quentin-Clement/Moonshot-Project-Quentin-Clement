import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'squat.dart';
import 'home.dart';

final routeProvider = Provider<GoRouter>((ref) {
  final router = GoRouter(
    initialLocation: '/home',
    routes: [
      GoRoute(
        path: '/home',
        name: 'home',
        builder: (context, state) => const Home(),
      ),
      GoRoute(
        path: '/squat',
        name: 'squat',
        builder: (context, state) => const Squat(),
      ),
    ],
  );
  return router;
});
