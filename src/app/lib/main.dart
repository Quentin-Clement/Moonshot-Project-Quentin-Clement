import 'package:flutter/material.dart';
import 'api_service.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: CalculationScreen(),
    );
  }
}

class CalculationScreen extends StatefulWidget {
  @override
  _CalculationScreenState createState() => _CalculationScreenState();
}

class _CalculationScreenState extends State<CalculationScreen> {
  double? result;
  final TextEditingController num1Controller = TextEditingController();
  final TextEditingController num2Controller = TextEditingController();

  void calculate() async {
    final num1 = double.tryParse(num1Controller.text) ?? 0;
    final num2 = double.tryParse(num2Controller.text) ?? 0;

    final res = await ApiService.sendCalculation(num1, num2);

    setState(() {
      result = res;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Flutter - Python API")),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: num1Controller,
              decoration: InputDecoration(labelText: "Enter first number"),
              keyboardType: TextInputType.number,
            ),
            TextField(
              controller: num2Controller,
              decoration: InputDecoration(labelText: "Enter second number"),
              keyboardType: TextInputType.number,
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: calculate,
              child: Text("Calculate"),
            ),
            SizedBox(height: 20),
            Text(
              result == null ? "Result will appear here" : "Result: $result",
              style: TextStyle(fontSize: 20),
            ),
          ],
        ),
      ),
    );
  }
}