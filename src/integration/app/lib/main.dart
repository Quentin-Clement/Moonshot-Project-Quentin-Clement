import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;
import 'dart:typed_data';
import 'dart:math';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Camera App',
      themeMode: ThemeMode.dark,
      theme: ThemeData.dark(),
      debugShowCheckedModeBanner: false,
      home: const CameraPage(),
    );
  }
}

class CameraPage extends StatefulWidget {
  const CameraPage({super.key});

  @override
  CameraPageState createState() => CameraPageState();
}

class CameraPageState extends State<CameraPage> with WidgetsBindingObserver {
  CameraController? _controller;
  bool _isCameraInitialized = false;
  late List<CameraDescription> _cameras;
  // Remove the _isSending flag and use an active counter instead.
  int _activeRequests = 0;
  final int _maxConcurrentRequests = 5; // Set your concurrency limit.

  // Replace with your actual Python FastAPI server endpoint
  final String _endpointUrl = 'http://192.168.14.175:8000/frame';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    initCamera(); // Initialize the camera
  }

  Future<void> initCamera() async {
    _cameras = await availableCameras();
    if (_cameras.isNotEmpty) {
      await onNewCameraSelected(_cameras.first);
    } else {
      debugPrint("No cameras found!");
    }
  }

  Future<void> onNewCameraSelected(CameraDescription description) async {
    final previousCameraController = _controller;

    final CameraController cameraController = CameraController(
      description,
      ResolutionPreset.high,
      imageFormatGroup: ImageFormatGroup.yuv420,
    );

    await previousCameraController?.dispose();

    try {
      await cameraController.initialize();
      if (mounted) {
        setState(() {
          _controller = cameraController;
          _isCameraInitialized = true;
        });
      }

      // Start the image stream and send frames concurrently.
      _controller!.startImageStream((CameraImage image) {
        // If we're below the concurrency limit, send the frame.
        if (_activeRequests < _maxConcurrentRequests) {
          _activeRequests++;
          sendFrame(image).whenComplete(() {
            _activeRequests--;
          });
        } else {
          // Optionally, log or handle dropped frames.
          debugPrint("Skipping frame: too many active requests ($_activeRequests).");
        }
      });
    } on CameraException catch (e) {
      debugPrint('Error initializing camera: $e');
    }
  }

  Future<void> sendFrame(CameraImage frame) async {
    try {
      // Convert the YUV420 image to RGB bytes.
      Uint8List rgbBytes = convertYUV420ToRGB(frame);

      // Send the RGB bytes to the Python FastAPI endpoint.
      var response = await http.post(
        Uri.parse(_endpointUrl),
        headers: {"Content-Type": "application/octet-stream"},
        body: rgbBytes,
      );

      if (response.statusCode == 200) {
        debugPrint("Frame sent successfully");
      } else {
        debugPrint("Error sending frame: ${response.statusCode}");
      }
    } catch (e) {
      debugPrint("Exception sending frame: $e");
    }
  }

  /// Converts a YUV420 [CameraImage] to RGB bytes.
  Uint8List convertYUV420ToRGB(CameraImage image) {
    final int width = image.width;
    final int height = image.height;
    var rgbBuffer = Uint8List(width * height * 3);

    // Check if the image has 3 planes (Y, U, and V).
    if (image.planes.length == 3) {
      final int uvRowStride = image.planes[1].bytesPerRow;
      final int uvPixelStride = image.planes[1].bytesPerPixel ?? 1;
      for (int h = 0; h < height; h++) {
        int uvRow = uvRowStride * (h >> 1);
        for (int w = 0; w < width; w++) {
          int uvIndex = uvRow + (w >> 1) * uvPixelStride;
          int index = h * width + w;
          int y = image.planes[0].bytes[index];
          int u = image.planes[1].bytes[uvIndex];
          int v = image.planes[2].bytes[uvIndex];

          double yVal = y.toDouble();
          double uVal = u.toDouble() - 128;
          double vVal = v.toDouble() - 128;

          int r = (yVal + 1.370705 * vVal).round();
          int g = (yVal - 0.337633 * uVal - 0.698001 * vVal).round();
          int b = (yVal + 1.732446 * uVal).round();

          rgbBuffer[index * 3] = r.clamp(0, 255);
          rgbBuffer[index * 3 + 1] = g.clamp(0, 255);
          rgbBuffer[index * 3 + 2] = b.clamp(0, 255);
        }
      }
    }
    // Handle the two-plane (interleaved UV) case.
    else if (image.planes.length == 2) {
      final int uvRowStride = image.planes[1].bytesPerRow;
      final int uvPixelStride = image.planes[1].bytesPerPixel ?? 2;
      for (int h = 0; h < height; h++) {
        int uvRow = uvRowStride * (h >> 1);
        for (int w = 0; w < width; w++) {
          int uvIndex = uvRow + (w >> 1) * uvPixelStride;
          int index = h * width + w;
          int y = image.planes[0].bytes[index];
          int u = image.planes[1].bytes[uvIndex];
          int v = image.planes[1].bytes[uvIndex + 1];

          double yVal = y.toDouble();
          double uVal = u.toDouble() - 128;
          double vVal = v.toDouble() - 128;

          int r = (yVal + 1.370705 * vVal).round();
          int g = (yVal - 0.337633 * uVal - 0.698001 * vVal).round();
          int b = (yVal + 1.732446 * uVal).round();

          rgbBuffer[index * 3] = r.clamp(0, 255);
          rgbBuffer[index * 3 + 1] = g.clamp(0, 255);
          rgbBuffer[index * 3 + 2] = b.clamp(0, 255);
        }
      }
    } else {
      debugPrint("Unsupported number of image planes: ${image.planes.length}");
      return Uint8List(0);
    }
    return rgbBuffer;
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    final CameraController? cameraController = _controller;
    if (cameraController == null || !cameraController.value.isInitialized) {
      return;
    }
    if (state == AppLifecycleState.inactive) {
      cameraController.dispose();
    } else if (state == AppLifecycleState.resumed) {
      onNewCameraSelected(cameraController.description);
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: _isCameraInitialized
            ? Center(child: Text("Sending RGB frames to Python server..."))
            : const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}