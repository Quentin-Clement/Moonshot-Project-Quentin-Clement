import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'dart:typed_data';
import 'dart:convert';
import 'package:web_socket_channel/io.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class Squat extends StatelessWidget {
  const Squat({super.key});
  
  @override
  Widget build(BuildContext context) {
    // Return CameraPage directly instead of wrapping in MaterialApp
    return const CameraPage();
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

  // WebSocket channel (adjust the URL to your server's WebSocket endpoint)
  late WebSocketChannel _channel;
  
  // To prevent sending multiple frames before a response arrives
  bool _isSendingFrame = false;

  // Detection state
  bool _depthSufficient = false;
  bool _kneeCaveDetected = false;
  List<String> _missingKeypoints = [];
  bool _poseDetected = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    initCamera();
    // Establish the WebSocket connection.
    _channel = IOWebSocketChannel.connect("ws://192.168.5.9:8000/ws/frame");
    // Listen for responses from the server.
    _channel.stream.listen((message) {
      debugPrint("Received response: $message");
      try {
        final responseData = jsonDecode(message);
        setState(() {
          _poseDetected = responseData['status'] == 'success';
          _depthSufficient = responseData['depth_sufficient'] ?? false;
          _kneeCaveDetected = responseData['knee_cave_detected'] ?? false;
          _missingKeypoints = List<String>.from(responseData['missing_keypoints'] ?? []);
        });
      } catch (e) {
        debugPrint("Error decoding message: $e");
      } finally {
        // Allow sending the next frame.
        _isSendingFrame = false;
      }
    });
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
      // Start the image stream.
      _controller!.startImageStream((CameraImage image) {
        debugPrint("Frame received from camera at ${DateTime.now()}");
        if (!_isSendingFrame) {
          _isSendingFrame = true;
          sendFrame(image);
        }
      });
    } on CameraException catch (e) {
      debugPrint('Error initializing camera: $e');
    }
  }

  Future<void> sendFrame(CameraImage frame) async {
    try {
      debugPrint("Sending frame at ${DateTime.now()}");
      // Convert the YUV420 image to RGB bytes.
      Uint8List rgbBytes = convertYUV420ToRGB(frame);
      // Send the raw bytes over the WebSocket.
      _channel.sink.add(rgbBytes);
    } catch (e) {
      debugPrint("Exception sending frame: $e");
      _isSendingFrame = false;
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
    _channel.sink.close();
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: _isCameraInitialized
            ? Column(
                children: [
                  Expanded(
                    child: Stack(
                      children: [
                        // Camera preview
                        Center(
                          child: CameraPreview(_controller!),
                        ),
                        // Missing keypoints overlay
                        if (_missingKeypoints.isNotEmpty)
                          Positioned(
                            top: 20,
                            right: 20,
                            child: Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: Colors.black54,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: _missingKeypoints
                                    .map((msg) => Padding(
                                          padding: const EdgeInsets.symmetric(vertical: 4),
                                          child: Text(
                                            msg,
                                            style: const TextStyle(color: Colors.red, fontSize: 14),
                                          ),
                                        ))
                                    .toList(),
                              ),
                            ),
                          ),
                      ],
                    ),
                  ),
                  // Detection results panel
                  Container(
                    color: Colors.black87,
                    padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
                    child: Column(
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              'Pose Detected:',
                              style: TextStyle(fontSize: 18),
                            ),
                            Text(
                              _poseDetected ? 'Yes' : 'No',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: _poseDetected ? Colors.green : Colors.red,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              'Depth Sufficient:',
                              style: TextStyle(fontSize: 18),
                            ),
                            Text(
                              _depthSufficient ? 'Yes' : 'No',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: _depthSufficient ? Colors.green : Colors.red,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              'Knee Cave Detected:',
                              style: TextStyle(fontSize: 18),
                            ),
                            Text(
                              _kneeCaveDetected ? 'Yes' : 'No',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: _kneeCaveDetected ? Colors.red : Colors.green,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              )
            : const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}