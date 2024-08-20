import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'dart:io';

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
  String _feedback = '';

  Future<void> _pickVideo() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickVideo(source: ImageSource.gallery);

    setState(() {
      _videoFile = pickedFile != null ? File(pickedFile.path) : null;
    });
  }

  Future<void> _uploadVideo() async {
    if (_videoFile == null) return;

    final uri = Uri.parse('http://<FLASK_SERVER_IP>:5000/analyze_video');
    final request = http.MultipartRequest('POST', uri)
      ..files.add(await http.MultipartFile.fromPath('video', _videoFile!.path));

    final response = await request.send();

    if (response.statusCode == 200) {
      final responseData = await response.stream.bytesToString();
      setState(() {
        _feedback = responseData;
      });
    } else {
      setState(() {
        _feedback = 'Failed to upload video';
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
              _feedback,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}