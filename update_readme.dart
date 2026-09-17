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

_writeAppGridSection(
  buffer: buffer,
  title: '📱 Mobile Apps (${apps.length})',
  items: apps,
);

  _writeTwoColumnSection(
    buffer: buffer,
    title: '🌐 Web Apps (${webs.length})',

    items: webs.map<String>((item) {
      return _link('${item['name']}', item['url']);
    }).toList(),
  );

  _writeTwoColumnSection(
    buffer: buffer,
    title: '🧩 Chrome Extensions (${chrome.length})',
    items: chrome.map<String>((item) {
      return _link('${item['name']}', item['url']);
    }).toList(),
  );

  buffer.writeln(_contact());
  buffer.writeln(_quote());

  File('README.md').writeAsStringSync(buffer.toString());

  print('README.md generated successfully');
}

String _link(String name, String url) => '<a href="$url">$name</a>';
_writeAppGridSection({
  required StringBuffer buffer,
  required String title,
  required List<Map<String, dynamic>> items,
}) {
  buffer.writeln('### $title\n');
  buffer.writeln('<table><tr>');

  for (var i = 0; i < items.length; i++) {
    final item = items[i];

    final icon = item['icon'];
    final name = item['name'];
    final id = item['id'];

    buffer.writeln('''
<td align="center" valign="top" width="20%">
  <a href="https://play.google.com/store/apps/details?id=$id">
    <img src="${icon}=s128" width="96" height="96" />
    <br>
    <b>$name</b>
  </a>
</td>
''');

    // Five apps per row
    if ((i + 1) % 5 == 0 && i != items.length - 1) {
      buffer.writeln('</tr><tr>');
    }
  }

  buffer.writeln('</tr></table>\n');
}
void _writeTwoColumnSection({
  required StringBuffer buffer,
  required String title,
  required List<String> items,
}) {
  final mid = (items.length / 2).ceil();

  final left = items.take(mid).toList();
  final right = items.skip(mid).toList();

  buffer.writeln('### $title\n');
  buffer.writeln('<table>');
  buffer.writeln('<tr>');
  buffer.writeln('<td valign="top" width="50%">');

  buffer.writeln('<ul>');
  for (final item in left) {
    buffer.writeln('<li>$item</li>');
  }
  buffer.writeln('</ul>');

  buffer.writeln('</td>');
  buffer.writeln('<td valign="top" width="50%">');

  buffer.writeln('<ul>');
  for (final item in right) {
    buffer.writeln('<li>$item</li>');
  }
  buffer.writeln('</ul>');

  buffer.writeln('</td>');
  buffer.writeln('</tr>');
  buffer.writeln('</table>\n');
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

I adapt quickly to new technologies, write clean, reusable components and libraries, and enjoy building practical products across mobile, web, desktop, and automation.

---
''';

String _skills() => '''
## 🛠️ Skills

- **Languages:** Kotlin, Java, Dart, Flutter, C#, Python, JavaScript
- **Skills:** REST APIs, Firebase, Play Store Management, OOP, Design Patterns, Clean Architecture
- **DevOps:** Git, Fastlane, CI/CD

---
''';

String _contact() => '''
## 📫 Contact

- LinkedIn: [dat-nguyen-3aa7bb117](https://www.linkedin.com/in/dat-nguyen-3aa7bb117/)
- Email: datnguyen.cr@gmail.com
- Portfolio: [datnguyencr.github.io/portfolio](https://datnguyencr.github.io/portfolio/)

---
''';

String _quote() => '''
> I build practical software with a focus on simplicity, maintainability, and long-term value.
''';
