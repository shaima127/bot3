"""
سكربت إضافة 7 دروس Flutter مرتبة إلى Supabase.
شغّليه مرة واحدة فقط: python add_lessons.py
"""
from database import supabase, get_embedding

LESSONS = [
    {
        "lesson_number": 1,
        "level": 1,
        "title": "ما هو Flutter ولماذا نتعلمه؟",
        "content": """🚀 *الدرس الأول: ما هو Flutter؟*

Flutter هو إطار عمل (Framework) مفتوح المصدر من Google لبناء تطبيقات جميلة تعمل على:
📱 الهاتف (Android و iOS)
💻 الويب
🖥️ سطح المكتب (Windows, Mac, Linux)

*لماذا Flutter مميز؟*
✅ كود واحد يعمل على كل المنصات
✅ أداء سريع جداً (يعمل بسرعة التطبيقات الأصلية)
✅ تصميمات جميلة جاهزة (Material Design)
✅ Hot Reload — شوف التغييرات فوراً بدون إعادة تشغيل

*لغة البرمجة:*
Flutter يستخدم لغة *Dart* وهي لغة سهلة وممتعة من Google.

*مثال أول كود Dart:*
```dart
void main() {
  print('مرحباً بالعالم! 🌍');
  print('أنا أتعلم Flutter!');
}
```

💡 *تمرين:* حاول تتخيل تطبيق تحبه على هاتفك — Flutter يقدر يبنيه!"""
    },
    {
        "lesson_number": 2,
        "level": 1,
        "title": "أساسيات لغة Dart",
        "content": """📘 *الدرس الثاني: أساسيات لغة Dart*

قبل ما نبني تطبيقات، لازم نفهم أساسيات Dart:

*1. المتغيرات (Variables):*
```dart
String name = 'أحمد';      // نص
int age = 25;               // رقم صحيح
double height = 1.75;       // رقم عشري
bool isStudent = true;      // صح أو خطأ
```

*2. الطباعة:*
```dart
print('اسمي $name وعمري $age');
```

*3. الشروط (if/else):*
```dart
if (age >= 18) {
  print('أنت بالغ ✅');
} else {
  print('أنت قاصر');
}
```

*4. الحلقات (Loops):*
```dart
for (int i = 1; i <= 5; i++) {
  print('العدد: $i');
}
```

*5. الدوال (Functions):*
```dart
String greet(String name) {
  return 'أهلاً يا $name! 👋';
}

void main() {
  print(greet('سارة'));
}
```

💡 *نقطة مهمة:* Dart لغة strongly typed يعني لازم تحدد نوع المتغير."""
    },
    {
        "lesson_number": 3,
        "level": 1,
        "title": "أول تطبيق Flutter — Hello World",
        "content": """🎯 *الدرس الثالث: أول تطبيق Flutter!*

الآن نبني أول تطبيق حقيقي:

*الكود الأساسي لأي تطبيق Flutter:*
```dart
import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(
          title: Text('تطبيقي الأول'),
        ),
        body: Center(
          child: Text(
            'مرحباً بالعالم! 🌍',
            style: TextStyle(fontSize: 24),
          ),
        ),
      ),
    );
  }
}
```

*شرح المكونات:*
📌 *MaterialApp* — الغلاف الرئيسي للتطبيق
📌 *Scaffold* — هيكل الصفحة (شريط علوي + محتوى)
📌 *AppBar* — الشريط العلوي
📌 *Center* — يوسط المحتوى
📌 *Text* — يعرض نص

*القاعدة الذهبية:*
في Flutter *كل شيء هو Widget* (عنصر واجهة)!
الأزرار، النصوص، الصور، التخطيطات — كلها Widgets."""
    },
    {
        "lesson_number": 4,
        "level": 2,
        "title": "الـ Widgets الأساسية",
        "content": """🧱 *الدرس الرابع: الـ Widgets الأساسية*

الـ Widgets هي لبنات بناء التطبيق. أهمها:

*1. Container — الصندوق:*
```dart
Container(
  width: 200,
  height: 100,
  color: Colors.blue,
  child: Text('أنا صندوق!'),
)
```

*2. Row — صف أفقي:*
```dart
Row(
  children: [
    Icon(Icons.star),
    Text('نجمة'),
    Icon(Icons.star),
  ],
)
```

*3. Column — عمود رأسي:*
```dart
Column(
  children: [
    Text('السطر الأول'),
    Text('السطر الثاني'),
    Text('السطر الثالث'),
  ],
)
```

*4. ElevatedButton — زر:*
```dart
ElevatedButton(
  onPressed: () {
    print('تم الضغط! 🎉');
  },
  child: Text('اضغط هنا'),
)
```

*5. Image — صورة:*
```dart
Image.network('https://flutter.dev/images/flutter-logo-sharing.png')
```

*6. ListView — قائمة:*
```dart
ListView(
  children: [
    ListTile(title: Text('العنصر 1')),
    ListTile(title: Text('العنصر 2')),
    ListTile(title: Text('العنصر 3')),
  ],
)
```

💡 *تذكر:* كل Widget إما تأخذ child واحد أو children (قائمة)."""
    },
    {
        "lesson_number": 5,
        "level": 2,
        "title": "StatelessWidget vs StatefulWidget",
        "content": """⚡ *الدرس الخامس: StatelessWidget vs StatefulWidget*

في Flutter نوعين رئيسيين من الـ Widgets:

*1. StatelessWidget (بدون حالة):*
لا يتغير بعد ما يتبنى. مثل: نص ثابت، أيقونة.
```dart
class MyText extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Text('أنا ثابت لا أتغير!');
  }
}
```

*2. StatefulWidget (بحالة):*
يتغير ويتحدث! مثل: عداد، نموذج إدخال.
```dart
class Counter extends StatefulWidget {
  @override
  _CounterState createState() => _CounterState();
}

class _CounterState extends State<Counter> {
  int count = 0;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('العدد: $count', style: TextStyle(fontSize: 30)),
        ElevatedButton(
          onPressed: () {
            setState(() {
              count++;
            });
          },
          child: Text('زيادة ➕'),
        ),
      ],
    );
  }
}
```

*متى تستخدم أيهما؟*
📌 الشاشة ثابتة → *StatelessWidget*
📌 الشاشة تتغير (ضغط زر، إدخال نص) → *StatefulWidget*

*القاعدة المهمة:*
`setState()` هي الطريقة لإخبار Flutter بإعادة بناء الشاشة بالبيانات الجديدة."""
    },
    {
        "lesson_number": 6,
        "level": 2,
        "title": "التنقل بين الشاشات (Navigation)",
        "content": """🧭 *الدرس السادس: التنقل بين الشاشات*

أي تطبيق حقيقي فيه أكثر من شاشة. Flutter يستخدم نظام *Navigator*:

*1. الانتقال لشاشة جديدة (Push):*
```dart
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => SecondScreen(),
  ),
);
```

*2. الرجوع للشاشة السابقة (Pop):*
```dart
Navigator.pop(context);
```

*3. مثال كامل:*
```dart
// الشاشة الأولى
class HomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('الرئيسية')),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => DetailScreen(),
              ),
            );
          },
          child: Text('اذهب للتفاصيل'),
        ),
      ),
    );
  }
}

// الشاشة الثانية
class DetailScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('التفاصيل')),
      body: Center(
        child: ElevatedButton(
          onPressed: () => Navigator.pop(context),
          child: Text('رجوع ⬅️'),
        ),
      ),
    );
  }
}
```

*4. إرسال بيانات بين الشاشات:*
```dart
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => DetailScreen(name: 'أحمد'),
  ),
);
```

💡 *نصيحة:* في التطبيقات الكبيرة استخدم Named Routes لتنظيم أفضل."""
    },
    {
        "lesson_number": 7,
        "level": 3,
        "title": "جلب البيانات من الإنترنت (HTTP & API)",
        "content": """🌐 *الدرس السابع: جلب البيانات من الإنترنت*

التطبيقات الحقيقية تحتاج تجلب بيانات من سيرفر (API):

*1. إضافة مكتبة http:*
في ملف pubspec.yaml:
```yaml
dependencies:
  http: ^1.1.0
```

*2. جلب بيانات (GET Request):*
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<void> fetchData() async {
  final response = await http.get(
    Uri.parse('https://jsonplaceholder.typicode.com/posts/1'),
  );

  if (response.statusCode == 200) {
    final data = json.decode(response.body);
    print('العنوان: ${data['title']}');
  } else {
    print('حدث خطأ!');
  }
}
```

*3. استخدامه في Widget:*
```dart
class PostScreen extends StatefulWidget {
  @override
  _PostScreenState createState() => _PostScreenState();
}

class _PostScreenState extends State<PostScreen> {
  String title = 'جاري التحميل...';

  @override
  void initState() {
    super.initState();
    loadPost();
  }

  Future<void> loadPost() async {
    final response = await http.get(
      Uri.parse('https://jsonplaceholder.typicode.com/posts/1'),
    );
    if (response.statusCode == 200) {
      setState(() {
        title = json.decode(response.body)['title'];
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('بيانات من الإنترنت')),
      body: Center(child: Text(title)),
    );
  }
}
```

*مفاهيم مهمة:*
📌 *async/await* — للعمليات غير المتزامنة (ما تجمد التطبيق)
📌 *Future* — وعد بقيمة ستأتي لاحقاً
📌 *json.decode* — تحويل النص لـ Map

💡 *تحدي:* جرب تجلب قائمة مستخدمين من jsonplaceholder.typicode.com/users"""
    },
]


def add_all_lessons():
    """إضافة كل الدروس السبعة دفعة واحدة"""
    print("=" * 50)
    print("📚 إضافة 7 دروس Flutter إلى Supabase")
    print("=" * 50)

    # مسح الدروس القديمة (اختياري)
    try:
        supabase.table("lessons").delete().neq("id", 0).execute()
        print("🗑️ تم مسح الدروس القديمة")
    except Exception as e:
        print(f"⚠️ لم يتم مسح الدروس القديمة: {e}")

    success_count = 0
    for lesson in LESSONS:
        print(f"\n📖 جاري إضافة الدرس {lesson['lesson_number']}: {lesson['title']}...")

        # توليد Embedding للـ RAG
        embedding = get_embedding(lesson["content"][:500])

        lesson_data = {
            "lesson_number": lesson["lesson_number"],
            "level": lesson["level"],
            "title": lesson["title"],
            "content": lesson["content"],
        }

        if embedding:
            lesson_data["embedding"] = embedding
            print("  ✅ تم توليد Vector Embedding")
        else:
            print("  ⚠️ لم يتم توليد Embedding (سيعمل بالبحث العادي)")

        try:
            supabase.table("lessons").insert(lesson_data).execute()
            print(f"  ✅ تم حفظ الدرس {lesson['lesson_number']} بنجاح!")
            success_count += 1
        except Exception as e:
            print(f"  ❌ خطأ في حفظ الدرس {lesson['lesson_number']}: {e}")

    print(f"\n{'=' * 50}")
    print(f"🎉 تم إضافة {success_count}/{len(LESSONS)} دروس بنجاح!")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    add_all_lessons()
