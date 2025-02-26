import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;

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
  bool _isSending = false; // flag to throttle sending frames

  // Replace with your actual Python server endpoint
  final String _endpointUrl = 'http://your-python-server-address:port/frame';

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

    // Using YUV420 here as that’s common for streaming.
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
      
      // Start the image stream
      _controller!.startImageStream((CameraImage image) {
        // Save the current frame in a variable named 'frame'
        var frame = image;
        // Throttle sending so we send one frame at a time
        if (!_isSending) {
          _isSending = true;
          sendFrame(frame).then((_) {
            _isSending = false;
          });
        }
      });
    } on CameraException catch (e) {
      debugPrint('Error initializing camera: $e');
    }
  }

  Future<void> sendFrame(CameraImage frame) async {
    try {
      // Convert the CameraImage (typically in YUV420 format) to JPEG bytes.
      // You will need to implement this conversion using a package like 'image' or custom logic.
      List<int> jpegBytes = await convertCameraImageToJpeg(frame);
      
      // Send the JPEG bytes to your Python FastAPI endpoint.
      var response = await http.post(
        Uri.parse(_endpointUrl),
        headers: {"Content-Type": "application/octet-stream"},
        body: jpegBytes,
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

  // Placeholder function for converting CameraImage to JPEG.
  // You can use the 'image' package (https://pub.dev/packages/image) to perform this conversion.
  Future<List<int>> convertCameraImageToJpeg(CameraImage image) async {
    // TODO: Implement conversion logic here.
    // For example, convert YUV420 data to an RGB image and then encode as JPEG.
    return <int>[];
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
    // Optionally, you may remove or replace the preview widget.
    return Scaffold(
      body: SafeArea(
        child: _isCameraInitialized
            ? Center(child: Text("Sending frames to Python server..."))
            : const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}