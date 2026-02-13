import 'dart:convert';
import 'dart:io';

void main() {
  final apps = _readJsonList('data/apps.json');
  final webs = _readJsonList('data/webs.json');
  final chrome = _readJsonList('data/chrome_extensions.json');

  final buffer = StringBuffer();

  buffer.writeln(_header());
  buffer.writeln(_skills());

  buffer.writeln('## 📂 Featured Projects\n');

  buffer.writeln('### Mobile Apps\n');
  for (final app in apps) {
    final id = app['id'];
    final name = app['name'];
    buffer.writeln(
        '- [$name](https://play.google.com/store/apps/details?id=$id)');
  }

  buffer.writeln('\n### Web Apps\n');
  for (final web in webs) {
    buffer.writeln('- [${web['name']}](${web['url']})');
  }

  buffer.writeln('\n### Chrome Extensions\n');
  for (final ext in chrome) {
    buffer.writeln('- [${ext['name']}](${ext['url']})');
  }

  buffer.writeln(_tools());
  buffer.writeln(_contact());
  buffer.writeln(_quote());

  File('README.md').writeAsStringSync(buffer.toString());
  print('README.md generated successfully');
}

List<Map<String, dynamic>> _readJsonList(String path) {
  final file = File(path);
  if (!file.existsSync()) {
    stderr.writeln('Missing file: $path');
    exit(1);
  }
  final data = jsonDecode(file.readAsStringSync());
  return List<Map<String, dynamic>>.from(data);
}

String _header() => '''
# 👋 Hi, I'm datnguyencr

I am a Mobile Software Developer with a strong background as a full-stack developer.  
I adapt quickly to new technologies, write clean, reusable components and libraries, and excel at delivering efficient, scalable solutions.

---
''';

String _skills() => '''
## 🛠️ Skills

- **Languages:** Kotlin, Java, Dart, Flutter, C#, Python, JavaScript
- **Technologies & Practices:** REST APIs, Firebase, Play Store Management, OOP, Design Patterns
- **Other Areas:** Version Control (Git), CI/CD with Fastlane

---
''';

String _tools() => '''
### Tools and Libs

- [Placeholder](https://datnguyencr.github.io/placeholder/)
- [ASCII Art](https://datnguyencr.github.io/ascii_art/)
- [Image Rotator](https://datnguyencr.github.io/image-rotator/)
- [PDF To Image Converter](https://github.com/datnguyencr/pdf-to-image-converter)
- [Image Converter](https://github.com/datnguyencr/image-converter)

---
''';

String _contact() => '''
## 📫 Contact Me

- Linkedin: [dat-nguyen-3aa7bb117](https://www.linkedin.com/in/dat-nguyen-3aa7bb117/)
- Email: datnguyen.cr@gmail.com
- portfolio: [portfolio](https://datnguyencr.github.io/portfolio/)

---
''';

String _quote() => '''
> “I build projects that are practical, maintainable, and fun — across mobile, desktop, and real-life experiments.”
''';
