import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'News Verifier',
      theme: ThemeData(
        primarySwatch: Colors.green,
      ),
      home: HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _controller = TextEditingController();
  String headline = '';

  void fetchFromClipboard() async {
    // Simulate clipboard fetch (replace with real clipboard logic if needed)
    setState(() {
      _controller.text = "Sample headline from clipboard";
    });
  }

  void searchHeadline() async {
    final String query = _controller.text;
    if (query.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Please enter a headline")),
      );
      return;
    }

    // Simulate API call
    final response = await http.post(
      Uri.parse("api endpoint url idhar ayga"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"query": query}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final score = data["score"] ?? 0;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => ResultScreen(score: score),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Error fetching result")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('News Verifier'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              height: 100,
              color: Colors.green[100],
              child: Center(
                child: Text(
                  "Navigation Box",
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
            ),
            SizedBox(height: 16),
            Text(
              "<Enter the Heading>",
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 16),
            TextField(
              controller: _controller,
              decoration: InputDecoration(
                border: OutlineInputBorder(),
                labelText: "Enter Headline",
              ),
            ),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: fetchFromClipboard,
              child: Text("Fetch Headline"),
              style: ElevatedButton.styleFrom(primary: Colors.green[400]),
            ),
            SizedBox(height: 8),
            ElevatedButton(
              onPressed: searchHeadline,
              child: Text("Search"),
              style: ElevatedButton.styleFrom(primary: Colors.green),
            ),
          ],
        ),
      ),
    );
  }
}

class ResultScreen extends StatelessWidget {
  final int score;

  ResultScreen({required this.score});

  @override
  Widget build(BuildContext context) {
    String accuracyLevel;
    if (score > 80) {
      accuracyLevel = "Very Accurate";
    } else if (score >= 60) {
      accuracyLevel = "Slightly Accurate";
    } else if (score >= 40) {
      accuracyLevel = "Mildly Accurate";
    } else if (score >= 20) {
      accuracyLevel = "Low Accuracy";
    } else {
      accuracyLevel = "Not Accurate";
    }

    return Scaffold(
      appBar: AppBar(
        title: Text("Result"),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Score: $score",
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 16),
            Text(
              "Accuracy Level: $accuracyLevel",
              style: TextStyle(fontSize: 20),
            ),
            SizedBox(height: 32),
            Text(
              "Accuracy Table:",
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 16),
            Table(
              border: TableBorder.all(),
              children: [
                TableRow(children: [
                  TableCell(child: Padding(
                    padding: EdgeInsets.all(8),
                    child: Text("Score Range", style: TextStyle(fontWeight: FontWeight.bold)),
                  )),
                  TableCell(child: Padding(
                    padding: EdgeInsets.all(8),
                    child: Text("Accuracy Description", style: TextStyle(fontWeight: FontWeight.bold)),
                  )),
                ]),
                TableRow(children: [
                  TableCell(child: Padding(padding: EdgeInsets.all(8), child: Text("80-100"))),
                  TableCell(child: Padding(padding: EdgeInsets.all(8), child: Text("Very Accurate"))),
                ]),
                TableRow(children: [
                  TableCell(child: Padding(padding: EdgeInsets.all(8), child: Text("60-80"))),
                  TableCell(child: Padding(padding: EdgeInsets.all(8), child: Text("Slightly Accurate"))),
                ]),
                TableRow(children: [
                  TableCell(child: Padding(padding: EdgeInsets.all(8), child: Text("40-60"))),
                  TableCell(child: Padding(padding: EdgeInsets.all(8), child: Text("Mildly Accurate"))),
                ]),
                TableRow(children: [
                  TableCell(child: Padding(padding: EdgeInsets.all(8), child: Text("20-40"))),
                  TableCell(child: Padding(padding: EdgeInsets.all(8), child: Text("Low Accuracy"))),
                ]),
                TableRow(children: [
                  TableCell(child: Padding(padding: EdgeInsets.all(8), child: Text("0-20"))),
                  TableCell(child: Padding(padding: EdgeInsets.all(8), child: Text("Not Accurate"))),
                ]),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
