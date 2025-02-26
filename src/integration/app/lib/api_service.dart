import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = "http://192.168.14.175:8000";

  static Future<double?> sendCalculation(double num1, double num2) async {
    final Uri url = Uri.parse("$baseUrl/calculate");

    try {
      final response = await http.post(
        url,
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"number1": num1, "number2": num2}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data["result"];
      } else {
        throw Exception("Failed to get result");
      }
    } catch (e) {
      print("Error: $e");
      return null;
    }
  }
}