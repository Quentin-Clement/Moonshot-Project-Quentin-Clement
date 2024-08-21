import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'dart:convert'; // Import to handle JSON decoding

void main() {
  runApp(VideoUploaderApp());
}

class VideoUploaderApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Video Uploader',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: VideoUploadPage(),
    );
  }
}

class VideoUploadPage extends StatefulWidget {
  @override
  _VideoUploadPageState createState() => _VideoUploadPageState();
}

class _VideoUploadPageState extends State<VideoUploadPage> {
  File? _videoFile;
  String _feedback = ''; // To store feedback from the server

  Future<void> _pickVideo() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickVideo(source: ImageSource.gallery);

    setState(() {
      _videoFile = pickedFile != null ? File(pickedFile.path) : null;
    });
  }

  Future<void> _uploadVideo() async {
    if (_videoFile == null) return;

    final uri = Uri.parse('http://127.0.0.1:5000/analyze'); // Adjust URL for real device/emulator if needed
    final request = http.MultipartRequest('POST', uri)
      ..files.add(await http.MultipartFile.fromPath('video', _videoFile!.path));

    try {
      final response = await request.send();
      final responseBody = await response.stream.bytesToString(); // Get response body

      if (response.statusCode == 200) {
        // Parse the JSON response
        final jsonResponse = jsonDecode(responseBody); // Decode the JSON

        // Get the 'feedback' field from the JSON response
        setState(() {
          _feedback = jsonResponse['feedback']; // Display feedback from the server
        });
      } else {
        setState(() {
          _feedback = 'Failed to upload video: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _feedback = 'Error: $e'; // Handle any errors during the request
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Upload Video'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            ElevatedButton(
              onPressed: _pickVideo,
              child: Text('Pick Video'),
            ),
            if (_videoFile != null)
              ElevatedButton(
                onPressed: _uploadVideo,
                child: Text('Upload Video'),
              ),
            SizedBox(height: 20),
            Text(
              _feedback, // Display the feedback from the server
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
