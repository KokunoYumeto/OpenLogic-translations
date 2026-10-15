# بازبینی فارسی: آغاز منطق گزاره‌ای، فرمول‌ها و مقدمات

بازخوانی منبع، اصلاح فارسی و ثبت انتخاب‌ها: OpenAI Codex — GPT-6 Astra، کوشش Ultra. این کار بازبینی انسانی نیست.

تمام بندهای پنج فایل بومی با انگلیسی تثبیت‌شده مقابله شدند، از جمله شاخه‌های نمادی که در خوانندهٔ جاری نمایش داده نمی‌شوند. نگاشت دقیق متن بومی به قطعه‌های خواننده با انتخابگر واقعی برچسب‌ها بازپخش شد. این بازبینی پسینی است؛ برای واژگان فاقد شاهد مستقیم، قطعیت ساختگی یا ادعای مشورت اولیه نداریم. بخش‌های واردشده از فایل‌های دیگر در دامنهٔ این پنج فایل بازداوری نشده‌اند.

## نتیجه

80 بند متن/عنوان ثبت شد. 6 موضع در 6 بند اصلاح شد. نسخه‌های اصلاح‌شده برای ادغام آماده‌اند. این یک بازبینی محدود است، نه گواهی کامل کتاب.

۴: تطبیق مستقیم و شاهد روشن؛ ۳: شاهد مرتبط همراه محدودیت بافتی؛ ۲: شاهد لفظی اختصاصی کافی نیست؛ ۱: تصمیم حل‌نشده. این امتیاز اطمینان تحریری است، نه احتمال کالیبره‌شده. بازبینی انسانی بعدی امکان اصلاح است، نه شرط ادامه.

## انتخاب‌ها و اصلاح‌های مستند

### FA-PL55-INCLUSION

منبع دربارهٔ واردکردن مطالب از فایل‌های بخش دیگر است؛ درون‌برد گرتهٔ ناروشنی بود. عبارت جایگزین همان عمل را بیان می‌کند و ادعای ترجمهٔ دوباره یا نگارش تازه ندارد.

پیش از اصلاح:
```latex
از بخش منطق مرتبهٔ اول درون‌برد شده‌اند
```

پس از اصلاح:
```latex
از بخش منطق مرتبهٔ اول وارد شده‌اند
```

شواهد: MT9-SYNTAX.
گزینه‌های کنارگذاشته‌شده: بازنویسی شده‌اند نادرست است؛ واژهٔ گرفته‌شده رابطهٔ واردکردن فایل را کمتر روشن می‌کند.
اطمینان تحریری: 3 از ۴.

### FA-PL57-MODAL-DISTINCTIONS

تعیین بیشتر و به‌نحو غیرضروری در این بافت گرته و مبهم‌اند. صورت تازه تقابل صدق ضروری با صدق غیرضروری را صریح می‌کند؛ آن را با ندانستن صدق یا صدق در زمان دیگر یکی نمی‌کند. کانن چارچوب صدق را پشتیبانی می‌کند، نه معادل اختصاصی contingency را.

پیش از اصلاح:
```latex
به‌ویژه، در منطق گزاره‌ای هرگونه تعیینِ بیشترِ
صدق و کذب را از بررسی کنار می‌گذاریم؛ برای نمونه، اینکه چیزی ضرورتاً صادق
است نه فقط به‌نحو غیرضروری،
```

پس از اصلاح:
```latex
به‌ویژه، در منطق گزاره‌ای تمایزهای دیگری دربارهٔ
صدق و کذب را بررسی نمی‌کنیم؛ برای نمونه، اینکه چیزی ضرورتاً صادق
است یا صادق است ولی صدقش ضروری نیست،
```

شواهد: MT10-SEMANTICS.
گزینه‌های کنارگذاشته‌شده: صادق احتمالی ممکن است احتمال عددی القا کند؛ اتفاقی بدون توضیح ممکن است تصادف علّی فهمیده شود. بنابراین معنای خود منبع باز شده و اصطلاح فاقد شاهد قطعی تحمیل نشده است.
اطمینان تحریری: 3 از ۴.

### FA-PL57-TRUTH-FUNCTIONS

منبع truth functions می‌گوید؛ افزودن صدق، نوع ارزش را در همان اصطلاحِ پیش‌تر معرفی‌شده روشن می‌کند. هیچ ورودی یا خروجی تابع تغییر نمی‌کند.

پیش از اصلاح:
```latex
توابع ارزشِ رابط‌های منطقی
```

پس از اصلاح:
```latex
توابع ارزش صدقِ رابط‌های منطقی
```

شواهد: MT9-CONNECTIVES, MT10-SEMANTICS.
گزینه‌های کنارگذاشته‌شده: تابع ارزشی بدون اسم ممکن است فقط صفت باشد؛ تابع معنا وابستگی به معنا را برخلاف بند نخست القا می‌کند.
اطمینان تحریری: 3 از ۴.

### FA-PL59-CLASS-SYNTAX

کسرهٔ اضافه پیش از از این دست ساخت نادرستی می‌ساخت. تنها همان کسره حذف شد؛ کمینگی رده و هر دو شمول ثابت‌اند.

پیش از اصلاح:
```latex
کوچک‌ترین ردهٔ
  از این دست
```

پس از اصلاح:
```latex
کوچک‌ترین رده
  از این دست
```

شواهد: I7-CLASS.
گزینه‌های کنارگذاشته‌شده: تبدیل رده به مجموعه ضرورتی ندارد؛ کلاس دانشگاهی نیز معنای ریاضی را مخدوش می‌کند.
اطمینان تحریری: 4 از ۴.

### FA-PL59-EXERCISE-BALANCED

مفعول و فعل در ترتیب طبیعی فارسی قرار گرفتند؛ صورت امری تمرین و همان ارجاع حفظ شدند. تمرین‌های صفحهٔ ۱۱ کانن نیز ساخت امرِ نشان‌دادن نتیجه را به کار می‌برند.

پیش از اصلاح:
```latex
اثبات کنید \olref[pl][syn][pre]{prop:balanced}
```

پس از اصلاح:
```latex
گزارهٔ \olref[pl][syn][pre]{prop:balanced} را ثابت کنید.
```

شواهد: MT11-SAT.
گزینه‌های کنارگذاشته‌شده: حل تمرین یا افزودن راهنمای اثبات جزو درخواست ترجمه نیست.
اطمینان تحریری: 4 از ۴.

### FA-PL59-EXERCISE-NOINIT

مفعول و فعل در ترتیب طبیعی فارسی قرار گرفتند؛ صورت امری تمرین و همان ارجاع حفظ شدند. تمرین‌های صفحهٔ ۱۱ کانن نیز ساخت امرِ نشان‌دادن نتیجه را به کار می‌برند.

پیش از اصلاح:
```latex
اثبات کنید \olref[pl][syn][pre]{prop:noinit}
```

پس از اصلاح:
```latex
گزارهٔ \olref[pl][syn][pre]{prop:noinit} را ثابت کنید.
```

شواهد: MT11-SAT.
گزینه‌های کنارگذاشته‌شده: حل تمرین یا افزودن راهنمای اثبات جزو درخواست ترجمه نیست.
اطمینان تحریری: 4 از ۴.

### PL55-EDITORIAL

یادداشت تحریریه و اصطلاحات صوری از وعدهٔ تولید و از شرح خواننده جدا بمانند.

تغییر فقط رفع گرتهٔ درون‌برد است؛ ارجاع به طرح آینده و تمایز دو نوع تمامیت حفظ شدند.
مواضع بررسی‌شده: OLP-0055-P04, OLP-0055-P05, OLP-0055-P06.
شواهد: MT9-SYNTAX, MT9-CONNECTIVES, MT10-SEMANTICS.
گزینه‌های بررسی‌شده: تبدیل برنامهٔ نویسنده به فصل تازه یا یکی‌گرفتن تمامیت اثباتی و تابعی مجاز نیست.
اطمینان تحریری: 3 از ۴.

### PL56-SYNTAX-SEMANTICS

نحو، معناشناسی و استقرا مفاهیم متفاوت‌اند.

عنوان و درخواست تحریریه با تعاریف خوانده‌شده تطبیق داده شدند.
مواضع بررسی‌شده: OLP-0056-P04, OLP-0056-P05.
شواهد: MT9-SYNTAX, MT10-SEMANTICS, I6-INDUCTIVE.
گزینه‌های بررسی‌شده: نحو به دستور زبان طبیعی تقلیل نمی‌یابد و استقرا به استنتاج از چند مثال تعبیر نمی‌شود.
اطمینان تحریری: 3 از ۴.

### PL57-SEMANTIC-SCOPE

ارزش صدق، ارضا، استلزام و اثبات خلط نشوند.

نمادها، سورهای هر/یک و شرطی مادی در هر بند جداگانه مقابله شدند؛ گواهی واژه‌به‌واژهٔ کاننی ادعا نمی‌شود.
مواضع بررسی‌شده: OLP-0057-P06, OLP-0057-P08, OLP-0057-P09.
شواهد: MT9-CONNECTIVES, MT10-SEMANTICS, MT11-SAT.
گزینه‌های بررسی‌شده: جایگزینی ارضا با اثبات یا شرطی مادی با استلزام معنایی نادرست است.
اطمینان تحریری: 3 از ۴.

### PL57-INDUCTIVE-REGISTER

ساخت استقرایی و تجزیهٔ یکتا با توضیح معنای دقیق حفظ شوند.

همان روش استقرایی در نحو و تعیین معنا به کار می‌رود؛ روش با نام‌گذاری یکسان خلط نشده است.
مواضع بررسی‌شده: OLP-0057-P07, OLP-0057-P08, OLP-0057-P09.
شواهد: I6-INDUCTIVE, MT9-ATOMIC, MT10-SEMANTICS.
گزینه‌های بررسی‌شده: فقط یک معنی داشتن جایگزین درستی برای uniquely readable نیست.
اطمینان تحریری: 3 از ۴.

### PL58-CONSTRUCTORS

اتمی، قاعدهٔ ساخت، انحصار و مرحلهٔ متناهی تفکیک شوند.

تمام حالت‌های پایه و پنج سازنده با صورت دقیق نمادها و ترتیبشان بررسی شدند.
مواضع بررسی‌شده: OLP-0058-P13, OLP-0058-P14, OLP-0058-P15, OLP-0058-P16, OLP-0058-P17, OLP-0058-P18, OLP-0058-P19, OLP-0058-P20, OLP-0058-P21, OLP-0058-P22, OLP-0058-P23.
شواهد: MT9-ATOMIC, I6-INDUCTIVE, I7-FREE.
گزینه‌های بررسی‌شده: تعریف صرفاً توصیفی یا حذف بند انحصار معنای متن را عوض می‌کند.
اطمینان تحریری: 3 از ۴.

### PL58-OPTIONAL-BRANCHES

شاخهٔ غیرفعال نیز جزو منبع قابل ویرایش است؛ نبود آن در نمای جاری حذف ترجمه نیست.

صورت خام کامل و انتخاب پروفایل جاری هر دو سنجیده شدند؛ اختلاف پرانتز قبلی صریح ثبت شد.
مواضع بررسی‌شده: OLP-0058-P06, OLP-0058-P07, OLP-0058-P09, OLP-0058-P10, OLP-0058-P12, OLP-0058-P24, OLP-0058-P25, OLP-0058-P27, OLP-0058-P28, OLP-0058-P29, OLP-0058-P30, OLP-0058-P31, OLP-0058-P32, OLP-0058-P33, OLP-0058-P34, OLP-0058-P35.
شواهد: MT9-SYNTAX, MT9-CONNECTIVES, I7-FREE.
گزینه‌های بررسی‌شده: تطبیق فقط متن انتخاب‌شده نمی‌تواند پوشش همهٔ شاخه‌های خام را ثابت کند.
اطمینان تحریری: 3 از ۴.

### PL59-INDUCTION

استقرا، کمینگی و شرط سره با تمام قیود حفظ شوند.

صورت شرطی هر سازنده، دو شمول برهان، توازن و ادعای پیشوند در بافت خود بررسی شدند.
مواضع بررسی‌شده: OLP-0059-P06, OLP-0059-P07, OLP-0059-P08, OLP-0059-P09, OLP-0059-P10, OLP-0059-P11, OLP-0059-P20, OLP-0059-P23.
شواهد: I6-INDUCTIVE, MT9-SYNTAX, I7-CLASS.
گزینه‌های بررسی‌شده: حذف سره ادعا را کاذب می‌کند؛ توازن به‌تنهایی خوانش یکتا را نتیجه نمی‌دهد.
اطمینان تحریری: 3 از ۴.

### PL59-READING-SUBSTITUTION

خوانش، وقوع و جانشینی بر رشتهٔ صوری اعمال می‌شوند، نه بر ارزش صدق.

هر سازنده و تمام فرمول‌های تمرین بررسی شدند؛ جانشینی هم‌زمان و تغییر همهٔ وقوع‌ها حفظ است.
مواضع بررسی‌شده: OLP-0059-P12, OLP-0059-P13, OLP-0059-P14, OLP-0059-P15, OLP-0059-P16, OLP-0059-P17, OLP-0059-P18, OLP-0059-P19, OLP-0059-P20, OLP-0059-P21, OLP-0059-P22.
شواهد: MT9-ATOMIC, MT9-SYNTAX, I7-FREE.
گزینه‌های بررسی‌شده: تغییر یک رخداد، جانشینی پیاپی یا تفسیر semantic جایگزین تعریف source نیست.
اطمینان تحریری: 3 از ۴.

## بندهای هم‌تراز برای بازبینی انسانی

متن هر دو طرف، بازهٔ دقیق بایت، شمارهٔ خط و هش در PROPOSITIONAL_0055_0059.json موجود است. تکرارهای یک انتخاب در بافت بند خود بررسی شده‌اند؛ این ثبت جای ادعای بی‌پشتوانهٔ تأیید تک‌تک واژه‌ها را نمی‌گیرد.

### محل ادغام اصلاح‌ها: OLP-0055

همهٔ متن بومی، شامل شاخه‌های غیرفعال، بازبینی شده است. انتخابگر واقعی برچسب‌ها نشان می‌دهد که قطعه‌های انتخاب‌شده دقیقاً با خوانندهٔ منتشرشده برابرند. وصلهٔ بومی و اصلاح قطعه‌های خواننده جدا نگه داشته می‌شوند؛ شاهد قدیمی بازنویسی نمی‌شود.

### محل ادغام اصلاح‌ها: OLP-0057

همهٔ متن بومی، شامل شاخه‌های غیرفعال، بازبینی شده است. انتخابگر واقعی برچسب‌ها نشان می‌دهد که قطعه‌های انتخاب‌شده دقیقاً با خوانندهٔ منتشرشده برابرند. وصلهٔ بومی و اصلاح قطعه‌های خواننده جدا نگه داشته می‌شوند؛ شاهد قدیمی بازنویسی نمی‌شود.

### تفاوت مستند با فرمول منبع: OLP-0058

اصلاح موجود در شاهد فارسی؛ اختلاف واقعی با پرانتز منبع، نه اصلاح تازهٔ این نوبت
شاخهٔ defIf با prvOr در انگلیسی پرانتز بستهٔ بی‌جفت دارد. فارسی از قبل پرانتز باز را افزوده است. این شاخه در خوانندهٔ جاری غیرفعال است. سابقهٔ جهانی گزارش هنوز احراز نشده؛ گزارش تازه‌ای ارسال نمی‌شود.
منبع تثبیت‌شده: `$\lnot !A \lor !B)$`؛ صورت بررسی‌شده برای تطبیق: `$(\lnot !A \lor !B)$`. متن منبع دست‌نخورده نگه داشته شده است؛ جدول پیش و پس از اصلاح، تفاوت خوانندهٔ جاری و پیشنهاد را مشخص می‌کند.

### محل ادغام اصلاح‌ها: OLP-0059

همهٔ متن بومی، شامل شاخه‌های غیرفعال، بازبینی شده است. انتخابگر واقعی برچسب‌ها نشان می‌دهد که قطعه‌های انتخاب‌شده دقیقاً با خوانندهٔ منتشرشده برابرند. وصلهٔ بومی و اصلاح قطعه‌های خواننده جدا نگه داشته می‌شوند؛ شاهد قدیمی بازنویسی نمی‌شود.

### OLP-0055-P04

عنوان منطق گزاره‌ای با محتوای بخش و تقابل آن با مرتبهٔ اول سازگار است.
شواهد: MT9-CONNECTIVES.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olpart{pl}{Propositional Logic}
```

ترجمهٔ فارسی:
```latex
\olpart{pl}{منطق گزاره‌ای}
```

</details>

### OLP-0055-P05

واردکردن مطالب، false بودن FOL، حذف محمول و ترم و سور و جایگزینی ساختار با ارزش‌گذاری همگی حفظ شدند. مقدماتی‌بودن فصل و واگذاری برهان‌ها به تمرین، توصیف نویسنده است، نه ادعای کمبود ترجمه.
شواهد: MT9-SYNTAX, MT9-ATOMIC, MT10-SEMANTICS.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: تمامیت و نام دستگاه اثبات در صفحات خوانده‌شده تعریف مستقلی ندارند؛ موقتاً حفظ شده‌اند، با تمایز صریح از تمامیت تابعی بند بعد.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{editorial}
  This part contains material on classical propositional logic. The
  first chapter is relatively rudimentary and just lists definitions
  and results, many proofs are not carried out but are left as
  exercises. The material on proof systems and the completeness
  theorem is included from the part on first-order logic, with the
  ``FOL'' tag set to false. This leaves out everything related to
  predicates, terms, and quantifiers, and replaces talk of
  !!{structure}s~$\Struct{M}$ with talk about
  !!{valuation}s~$\pAssign{v}$.
```

ترجمهٔ فارسی:
```latex
\begin{editorial}
  این بخش مطالبی دربارهٔ منطق گزاره‌ای کلاسیک دربردارد. فصل نخست نسبتاً
  مقدماتی است و تنها تعریف‌ها و نتایج را فهرست می‌کند؛ بسیاری از برهان‌ها
  ارائه نشده‌اند و به‌عنوان تمرین به خواننده واگذار شده‌اند. مطالب مربوط به
  دستگاه‌های اثبات و قضیهٔ تمامیت از بخش منطق مرتبهٔ اول وارد شده‌اند،
  درحالی‌که برچسب ``FOL'' با مقدار نادرست تنظیم شده است. این کار همهٔ مطالب
  مربوط به محمول‌ها، ترم‌ها و سورها را کنار می‌گذارد و سخن از
  !!{structure}s~$\Struct{M}$ را با سخن از
  !!{valuation}s~$\pAssign{v}$ جایگزین می‌کند.
```

</details>

### OLP-0055-P06

عبارت آینده‌نگرِ برنامهٔ توسعه حفظ شد و به وعدهٔ مترجم تبدیل نشد. تمامیت نسبت به توابع ارزش به توان بیان توابع صدق مربوط است، نه تمامیت دستگاه اثبات.
شواهد: MT9-CONNECTIVES.
اطمینان تحریری: 2 از ۴.
نیازمند بررسی: شاهد اختصاصی برای معادل truth-functional completeness در این دو منبع نداریم؛ صورت موجود فقط بر اساس معنای روشن متن و تمایز دو کاربرد به‌طور موقت حفظ شد.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
  It is planned to expand this part to include
  more detail, and to add further topics and results, such as
  truth-functional completeness.
\end{editorial}
```

ترجمهٔ فارسی:
```latex
  برنامه بر این است که این بخش گسترش یابد تا جزئیات بیشتری را دربرگیرد و
  موضوع‌ها و نتایج بیشتری، مانند تمامیت نسبت به توابع ارزش، به آن افزوده
  شوند.
\end{editorial}
```

</details>

### OLP-0055-P07

مسیر واردکردن، شرط برچسب یا قلاب پایانی عیناً حفظ شد. نگاشت قطعه‌های انتخاب‌شده به خواننده بازپخش می‌شود؛ این رکورد ادعای بازبینی فرزندان واردشده ندارد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olimport[syntax-and-semantics]{syntax-and-semantics}
```

ترجمهٔ فارسی:
```latex
\olimport[syntax-and-semantics]{syntax-and-semantics}
```

</details>

### OLP-0055-P08

مسیر واردکردن، شرط برچسب یا قلاب پایانی عیناً حفظ شد. نگاشت قطعه‌های انتخاب‌شده به خواننده بازپخش می‌شود؛ این رکورد ادعای بازبینی فرزندان واردشده ندارد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagfalse{FOL}
```

ترجمهٔ فارسی:
```latex
\tagfalse{FOL}
```

</details>

### OLP-0055-P09

مسیر واردکردن، شرط برچسب یا قلاب پایانی عیناً حفظ شد. نگاشت قطعه‌های انتخاب‌شده به خواننده بازپخش می‌شود؛ این رکورد ادعای بازبینی فرزندان واردشده ندارد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olimport[../first-order-logic/proof-systems]{proof-systems}
```

ترجمهٔ فارسی:
```latex
\olimport[../first-order-logic/proof-systems]{proof-systems}
```

</details>

### OLP-0055-P10

مسیر واردکردن، شرط برچسب یا قلاب پایانی عیناً حفظ شد. نگاشت قطعه‌های انتخاب‌شده به خواننده بازپخش می‌شود؛ این رکورد ادعای بازبینی فرزندان واردشده ندارد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\iftag{prfSC}{%
  \olimport[../first-order-logic/sequent-calculus]{sequent-calculus}
}{}
```

ترجمهٔ فارسی:
```latex
\iftag{prfSC}{%
  \olimport[../first-order-logic/sequent-calculus]{sequent-calculus}
}{}
```

</details>

### OLP-0055-P11

مسیر واردکردن، شرط برچسب یا قلاب پایانی عیناً حفظ شد. نگاشت قطعه‌های انتخاب‌شده به خواننده بازپخش می‌شود؛ این رکورد ادعای بازبینی فرزندان واردشده ندارد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\iftag{prfND}{%
  \olimport[../first-order-logic/natural-deduction]{natural-deduction}
}{}
```

ترجمهٔ فارسی:
```latex
\iftag{prfND}{%
  \olimport[../first-order-logic/natural-deduction]{natural-deduction}
}{}
```

</details>

### OLP-0055-P12

مسیر واردکردن، شرط برچسب یا قلاب پایانی عیناً حفظ شد. نگاشت قطعه‌های انتخاب‌شده به خواننده بازپخش می‌شود؛ این رکورد ادعای بازبینی فرزندان واردشده ندارد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\iftag{prfTab}{%
  \olimport[../first-order-logic/tableaux]{tableaux}
}{}
```

ترجمهٔ فارسی:
```latex
\iftag{prfTab}{%
  \olimport[../first-order-logic/tableaux]{tableaux}
}{}
```

</details>

### OLP-0055-P13

مسیر واردکردن، شرط برچسب یا قلاب پایانی عیناً حفظ شد. نگاشت قطعه‌های انتخاب‌شده به خواننده بازپخش می‌شود؛ این رکورد ادعای بازبینی فرزندان واردشده ندارد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\iftag{prfAX}{%
  \olimport[../first-order-logic/axiomatic-deduction]{axiomatic-deduction}
}{}
```

ترجمهٔ فارسی:
```latex
\iftag{prfAX}{%
  \olimport[../first-order-logic/axiomatic-deduction]{axiomatic-deduction}
}{}
```

</details>

### OLP-0055-P14

مسیر واردکردن، شرط برچسب یا قلاب پایانی عیناً حفظ شد. نگاشت قطعه‌های انتخاب‌شده به خواننده بازپخش می‌شود؛ این رکورد ادعای بازبینی فرزندان واردشده ندارد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olimport[../first-order-logic/completeness]{completeness}
```

ترجمهٔ فارسی:
```latex
\olimport[../first-order-logic/completeness]{completeness}
```

</details>

### OLP-0055-P15

مسیر واردکردن، شرط برچسب یا قلاب پایانی عیناً حفظ شد. نگاشت قطعه‌های انتخاب‌شده به خواننده بازپخش می‌شود؛ این رکورد ادعای بازبینی فرزندان واردشده ندارد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagtrue{FOL}
```

ترجمهٔ فارسی:
```latex
\tagtrue{FOL}
```

</details>

### OLP-0055-P16

مسیر واردکردن، شرط برچسب یا قلاب پایانی عیناً حفظ شد. نگاشت قطعه‌های انتخاب‌شده به خواننده بازپخش می‌شود؛ این رکورد ادعای بازبینی فرزندان واردشده ندارد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\OLEndPartHook
```

ترجمهٔ فارسی:
```latex
\OLEndPartHook
```

</details>

### OLP-0056-P04

عنوان نحو و معناشناسی، شکل نمادین را از تعیین صدق جدا نگه می‌دارد؛ عنوان ناظر به همین دو بخش است.
شواهد: MT9-SYNTAX, MT10-SEMANTICS.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olchapter{pl}{syn}{Syntax and Semantics}
```

ترجمهٔ فارسی:
```latex
\olchapter{pl}{syn}{نحو و معناشناسی}
```

</details>

### OLP-0056-P05

درخواست نویسنده برای شرح استقرا و مثال‌های بیشتر حفظ شد؛ آسان‌فهم وصف درآمد آموزشی است و هیچ اثبات یا مثالی خودسرانه افزوده نشد.
شواهد: I6-INDUCTIVE, MT9-ATOMIC.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{editorial}
  This is a very quick summary of definitions only. It should be
  expanded to provide a gentle intro to proofs by induction on
  formulas, with lots more examples.
\end{editorial}
```

ترجمهٔ فارسی:
```latex
\begin{editorial}
  این فقط خلاصه‌ای بسیار کوتاه از تعریف‌هاست. باید گسترش یابد تا درآمدی
  آسان‌فهم به روشِ اثبات با استقرا بر فرمول‌ها، همراه با مثال‌های بسیار
  بیشتر، فراهم کند.
\end{editorial}
```

</details>

### OLP-0056-P06

ورودی بخش یا قلاب پایان فصل، با همان ترتیب و شناسه حفظ شد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olimport{introduction}
```

ترجمهٔ فارسی:
```latex
\olimport{introduction}
```

</details>

### OLP-0056-P07

ورودی بخش یا قلاب پایان فصل، با همان ترتیب و شناسه حفظ شد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olimport{formulas}
```

ترجمهٔ فارسی:
```latex
\olimport{formulas}
```

</details>

### OLP-0056-P08

ورودی بخش یا قلاب پایان فصل، با همان ترتیب و شناسه حفظ شد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olimport{preliminaries}
```

ترجمهٔ فارسی:
```latex
\olimport{preliminaries}
```

</details>

### OLP-0056-P09

ورودی بخش یا قلاب پایان فصل، با همان ترتیب و شناسه حفظ شد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olimport{formation-sequences}
```

ترجمهٔ فارسی:
```latex
\olimport{formation-sequences}
```

</details>

### OLP-0056-P10

ورودی بخش یا قلاب پایان فصل، با همان ترتیب و شناسه حفظ شد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olimport{valuations-sat}
```

ترجمهٔ فارسی:
```latex
\olimport{valuations-sat}
```

</details>

### OLP-0056-P11

ورودی بخش یا قلاب پایان فصل، با همان ترتیب و شناسه حفظ شد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olimport{semantic-notions}
```

ترجمهٔ فارسی:
```latex
\olimport{semantic-notions}
```

</details>

### OLP-0056-P12

ورودی بخش یا قلاب پایان فصل، با همان ترتیب و شناسه حفظ شد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\OLEndChapterHook
```

ترجمهٔ فارسی:
```latex
\OLEndChapterHook
```

</details>

### OLP-0057-P04

شناسهٔ فایل حفظ شد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olfileid{pl}{syn}{int}
```

ترجمهٔ فارسی:
```latex
\olfileid{pl}{syn}{int}
```

</details>

### OLP-0057-P05

عنوان مقدمه با نقش مرور مفاهیم سازگار است.
شواهد: MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olsection{Introduction}
```

ترجمهٔ فارسی:
```latex
\olsection{مقدمه}
```

</details>

### OLP-0057-P06

دو ارزشی‌بودن، وابستگی کامل ارزش مرکب به اجزا و عدم وابستگی به معنا حفظ‌اند. دوگانه‌های ضروری/غیرضروری، معلوم/نامعلوم و زمانی تفکیک شدند. مناقشه دربارهٔ شرطی انگلیسی، به نفی تابع‌ارزشی‌بودن شرطی مادی تبدیل نشده است.
شواهد: MT9-CONNECTIVES, MT10-SEMANTICS.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: تابع‌ارزشی، شرطی مادی و الفاظ وجهی در صفحات حاضر شاهد مستقیم ندارند؛ تعریف روشن منبع و قید موقت مبنای حفظ آن‌هاست، نه ادعای تثبیت پژوهشی همهٔ الفاظ.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Propositional logic deals with !!{formula}s that are built from
!!{propositional variable}s using the propositional connectives
$\lnot$, $\land$, $\lor$, $\lif$, and $\liff$.  Intuitively,
!!a{propositional variable}~$p$ stands for a sentence or proposition
that is true or false. Whenever the ``truth value'' of the
!!{propositional variable} in !!a{formula} is determined, so is the
truth value of any !!{formula}s formed from them using propositional
connectives.  We say that propositional logic is \emph{truth
  functional}, because its semantics is given by functions of truth
values. In particular, in propositional logic we leave out of
consideration any further determination of truth and falsity, e.g.,
whether something is necessarily true rather than just contingently
true, or whether something is known to be true, or whether something
is true now rather than was true or will be true.  We only consider
two truth values true ($\True$) and false ($\False$), and so exclude
from discussion the possibility that a statement may be neither true
nor false, or only half true. We also concentrate only on connectives where
the truth value of !!a{formula} built from them is completely
determined by the truth values of its parts (and not, say, on its
meaning). In particular, whether the truth value of conditionals in
English is truth functional in this sense is contentious. The material
conditional~$\lif$ is; other logics deal with conditionals that are
not truth functional.
```

ترجمهٔ فارسی:
```latex
منطق گزاره‌ای به دسته‌ای از !!{formula}s می‌پردازد که از
!!{propositional variable}s با استفاده از رابط‌های گزاره‌ایِ
$\lnot$، $\land$، $\lor$، $\lif$ و $\liff$ ساخته می‌شوند. از دید
شهودی، !!a{propositional variable}~$p$ نمایندهٔ جمله یا گزاره‌ای است که
صادق یا کاذب است. هرگاه «ارزش صدق» هر !!{propositional variable} در
!!a{formula} تعیین شود، ارزش صدق هر یک از !!{formula}s که با استفاده از
رابط‌های گزاره‌ای از این متغیرها ساخته می‌شوند نیز تعیین می‌شود. می‌گوییم
منطق گزاره‌ای \emph{تابع‌ارزشی} است، زیرا معناشناسی آن بر پایهٔ تابع‌هایی
از ارزش‌های صدق تعیین می‌شود. به‌ویژه، در منطق گزاره‌ای تمایزهای دیگری دربارهٔ
صدق و کذب را بررسی نمی‌کنیم؛ برای نمونه، اینکه چیزی ضرورتاً صادق
است یا صادق است ولی صدقش ضروری نیست، اینکه صادق‌بودنِ چیزی معلوم است، یا اینکه
چیزی اکنون صادق است نه اینکه در گذشته صادق بوده یا در آینده صادق خواهد
بود. فقط دو ارزش صدق، یعنی صادق ($\True$) و کاذب ($\False$)، را در نظر
می‌گیریم و ازاین‌رو این امکان را از بحث کنار می‌گذاریم که گزاره‌ای نه صادق
باشد نه کاذب، یا فقط نیمه‌صادق باشد. همچنین تنها بر رابط‌هایی تمرکز می‌کنیم
که ارزش صدقِ !!a{formula} ساخته‌شده از آن‌ها کاملاً از ارزش‌های صدقِ
اجزایش تعیین می‌شود، نه مثلاً از معنای آن. به‌ویژه، اینکه ارزش صدقِ
شرطی‌های زبان انگلیسی به این معنا تابع‌ارزشی است یا نه، محل اختلاف است.
شرطی مادی~$\lif$ تابع‌ارزشی است؛ منطق‌های دیگر به شرطی‌هایی می‌پردازند که
تابع‌ارزشی نیستند.
```

</details>

### OLP-0057-P07

تفاوت انتخاب نماد، رابط اولیه و پرانتز از مشترک‌بودن تعریف استقرایی جداست. خوانش یکتا یعنی تجزیهٔ یگانه طبق قواعد، نه صدق یکتا.
شواهد: MT9-SYNTAX, MT9-ATOMIC, I6-INDUCTIVE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: نام نمادگذاری لهستانی، فرانظریه و خوانش یکتا در همین صفحات شاهد مستقیم ندارند؛ به‌عنوان نام و شرح تعریف منبع موقتاً حفظ‌اند.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
In order to develop the theory and metatheory of truth-functional
propositional logic, we must first define the syntax and semantics of
its expressions.  We will describe one way of constructing
!!{formula}s from !!{propositional variable}s using the connectives.
Alternative definitions are possible. Other systems will choose
different symbols, will select different sets of connectives as
primitive, and will use parentheses differently (or even not at all,
as in the case of so-called Polish notation).  What all approaches
have in common, though, is that the formation rules define the set of
!!{formula}s \emph{inductively}. If done properly, every expression
can result essentially in only one way according to the formation
rules.  The inductive definition resulting in expressions that are
\emph{uniquely readable} means we can give meanings to these
expressions using the same method---inductive definition.
```

ترجمهٔ فارسی:
```latex
برای بسط نظریه و فرانظریهٔ منطق گزاره‌ایِ تابع‌ارزشی، نخست باید نحو و
معناشناسی عبارت‌های آن را تعریف کنیم. یک روش ساختن !!{formula}s از
!!{propositional variable}s با استفاده از رابط‌ها را شرح خواهیم داد.
تعریف‌های جایگزین نیز ممکن‌اند. دستگاه‌های دیگر نمادهای متفاوتی برمی‌گزینند،
مجموعه‌های متفاوتی از رابط‌ها را به‌عنوان رابط‌های اولیه انتخاب می‌کنند و
پرانتزها را به شیوه‌ای متفاوت به کار می‌برند؛ یا حتی، مانند آنچه در
نمادگذاری موسوم به لهستانی رخ می‌دهد، اصلاً پرانتز به کار نمی‌برند. بااین‌حال،
وجه مشترک همهٔ رویکردها این است که قواعد ساخت، مجموعهٔ !!{formula}s را
\emph{به‌طور استقرایی} تعریف می‌کنند. اگر این کار درست انجام شود، هر عبارت
اساساً تنها از یک راه مطابق قواعد ساخت به دست می‌آید. اینکه تعریف استقرایی
به عبارت‌هایی \emph{با خوانش یکتا} می‌انجامد، بدین معناست که می‌توانیم با
همان روش، یعنی تعریف استقرایی، به این عبارت‌ها معنا بدهیم.
```

</details>

### OLP-0057-P08

ارزش‌گذاری به متغیرها مقدار می‌دهد؛ ارزش فرمول از آن تعیین می‌شود. iff و معادلهٔ صدق عیناً حفظ‌اند؛ ارضا با اثبات اشتباه نشده است. توابع ارزش صدق روشن شد.
شواهد: MT10-SEMANTICS, MT11-SAT.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: کانن خوانده‌شده معناشناسی مرتبهٔ اول دارد؛ تصدیق مستقیم لفظ ارزش‌گذاری گزاره‌ای از آن استنتاج نمی‌شود.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Giving the meaning of expressions is the domain of semantics.  The
central concept in semantics for propositional logic is that of
satisfaction in !!a{valuation}. !!^a{valuation}~$\pAssign{v}$ assigns
truth values $\True$, $\False$ to the !!{propositional variable}s. Any
!!{valuation} determines a truth value $\pValue{v}(!A)$ for any
!!{formula}~$!A$.  !!^a{formula} is satisfied in
!!a{valuation}~$\pAssign{v}$ iff $\pValue{v}(!A) = \True$---we write
this as $\pSat{v}{!A}$. This relation can also be defined by induction on
the structure of~$!A$, using the truth functions for the logical
connectives to define, say, satisfaction of $!A \land !B$ in terms of
satisfaction (or not) of $!A$ and~$!B$.
```

ترجمهٔ فارسی:
```latex
معنا بخشیدن به عبارت‌ها در قلمرو معناشناسی است. مفهوم محوری در معناشناسیِ
منطق گزاره‌ای، ارضا در !!a{valuation} است. !!^a{valuation}~$\pAssign{v}$
ارزش‌های صدقِ $\True$ و $\False$ را به !!{propositional variable}s نسبت
می‌دهد. هر !!{valuation} یک ارزش صدق به‌صورت $\pValue{v}(!A)$ را برای هر
!!{formula}~$!A$ تعیین می‌کند. !!^a{formula} در
!!a{valuation}~$\pAssign{v}$ ارضا می‌شود اگر و تنها اگر
$\pValue{v}(!A) = \True$؛ این را به‌صورت $\pSat{v}{!A}$ می‌نویسیم. این
رابطه را می‌توان با استقرا بر ساختار~$!A$ نیز تعریف کرد: با استفاده از
توابع ارزش صدقِ رابط‌های منطقی، برای نمونه، ارضای $!A \land !B$ را برحسب ارضا
شدن یا نشدنِ $!A$ و~$!B$ تعریف می‌کنیم.
```

</details>

### OLP-0057-P09

هر ارزش‌گذاری برای همان‌گویی، هر ارزش‌گذاریِ ارضاکنندهٔ همهٔ مقدمات برای استلزام، و یک ارزش‌گذاری مشترک برای ارضاپذیری تفکیک شدند. کاربرد استقرا دو سطح ساخت فرمول و معناشناسی را حفظ می‌کند.
شواهد: MT11-SAT, I6-INDUCTIVE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: همان‌گویی و پیامد معنایی در این صفحات شاهد عین‌عبارت ندارند. معادل‌ها با تعریف‌های صریح منبع سازگارند ولی هنوز موقت‌اند.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
On the basis of the satisfaction relation $\pSat{v}{!A}$ for sentences
we can then define the basic semantic notions of tautology,
entailment, and satisfiability.  !!^a{formula} is a tautology,
$\Entails !A$, if every !!{valuation} satisfies it, i.e.,
$\pValue{v}(!A) = \True$ for any~$\pAssign{v}$. It is entailed by a
set of !!{formula}s, $\Gamma \Entails !A$, if every !!{valuation} that
satisfies all the !!{formula}s in~$\Gamma$ also satisfies~$!A$. And a
set of !!{formula}s is satisfiable if some !!{valuation} satisfies all
!!{formula}s in it at the same time.  Because !!{formula}s are
inductively defined, and satisfaction is in turn defined by induction
on the structure of !!{formula}s, we can use induction to prove
properties of our semantics and to relate the semantic notions
defined.
```

ترجمهٔ فارسی:
```latex
سپس بر پایهٔ رابطهٔ ارضای $\pSat{v}{!A}$ برای جمله‌ها می‌توانیم مفاهیم
معناییِ بنیادیِ همان‌گویی، استلزام معنایی و ارضاپذیری را تعریف کنیم.
!!^a{formula} یک همان‌گویی است، $\Entails !A$، اگر هر !!{valuation} آن را
ارضا کند؛ یعنی $\pValue{v}(!A) = \True$ برای هر~$\pAssign{v}$.
آن فرمول پیامدِ معناییِ مجموعه‌ای از !!{formula}s است،
$\Gamma \Entails !A$، اگر هر !!{valuation} که همهٔ !!{formula}s در~$\Gamma$
را ارضا می‌کند،~$!A$ را نیز ارضا کند. همچنین مجموعه‌ای از !!{formula}s
ارضاپذیر است اگر یک !!{valuation} همهٔ !!{formula}s آن را هم‌زمان ارضا
کند. چون !!{formula}s به‌طور استقرایی تعریف شده‌اند و ارضا نیز به‌نوبهٔ
خود با استقرا بر ساختار !!{formula}s تعریف می‌شود، می‌توانیم با استقرا
ویژگی‌های معناشناسی خود را ثابت کنیم و میان مفاهیم معناییِ تعریف‌شده
ارتباط برقرار کنیم.
```

</details>

### OLP-0058-P04

شناسهٔ بخش حفظ شد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olfileid{pl}{syn}{fml}
```

ترجمهٔ فارسی:
```latex
\olfileid{pl}{syn}{fml}
```

</details>

### OLP-0058-P05

عنوان فرمول‌های گزاره‌ای از توکن جمع ساخته می‌شود؛ شناسهٔ توکن ثابت ماند.
شواهد: MT9-ATOMIC.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olsection{Propositional \usetoken{P}{formula}}
```

ترجمهٔ فارسی:
```latex
\olsection{\usetoken{P}{formula}ی گزاره‌ای}
```

</details>

### OLP-0058-P06

ساخت فرمول از متغیرها، ثابت‌های شرطیِ صدق/کذب و رابط‌ها حفظ شد. دو شاخهٔ و در فارسی برای نبودِ ثابت کذب نیز اتصال نحوی درست می‌سازند و افزودهٔ محتوایی نیستند.
شواهد: MT9-CONNECTIVES, MT9-ATOMIC.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
!!^{formula}s of propositional logic are built up from
\emph{!!{propositional
    variable}s}\iftag{prvFalse}{\iftag{prvTrue}{,}{ and} the
  propositional constant~$\lfalse$}{}\iftag{prvTrue}{\iftag{prvFalse}{
    and}{} the propositional constant~$\ltrue$}{} using \emph{logical
  connectives}.
```

ترجمهٔ فارسی:
```latex
!!^{formula}sی منطق گزاره‌ای از
\emph{!!{propositional
    variable}s}\iftag{prvFalse}{\iftag{prvTrue}{،}{ و} ثابت
  گزاره‌ایِ~$\lfalse$}{}\iftag{prvTrue}{\iftag{prvFalse}{ و}{ و} ثابت
  گزاره‌ایِ~$\ltrue$}{} با استفاده از \emph{رابط‌های منطقی} ساخته می‌شوند.
```

</details>

### OLP-0058-P07

مجموعهٔ شمارای نامتناهی متغیرها، ثابت‌ها، پنج رابط و علائم جداگانه‌اند. ترتیب تمام نمادها و شرط‌های نمایش حفظ است.
شواهد: MT9-SYNTAX, MT9-CONNECTIVES.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: شمارای نامتناهی از توکن موجود می‌آید؛ این دو صفحه شاهد خاص denumerable نیستند. عطف/فصل و نشانهٔ سجاوندی نیز در همین شاهد عیناً نیامده‌اند.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{enumerate}
\item !!^a{denumerable} set~$\PVar$ of !!{propositional variable}s $\Obj p_0$,
  $\Obj p_1$, \dots
\tagitem{prvFalse}{The propositional constant for !!{falsity}~$\lfalse$.}{}
\tagitem{prvTrue}{The propositional constant for !!{truth}~$\ltrue$.}{}
\item The logical connectives:
  \startycommalist
  \iftag{prvNot}{\ycomma $\lnot$ (negation)}{}%
  \iftag{prvAnd}{\ycomma $\land$ (conjunction)}{}%
  \iftag{prvOr}{\ycomma $\lor$ (disjunction)}{}%
  \iftag{prvIf}{\ycomma $\lif$ (!!{conditional})}{}%
  \iftag{prvIff}{\ycomma $\liff$ (!!{biconditional})}{}%
\item Punctuation marks: (, ), and the comma.
\end{enumerate}
```

ترجمهٔ فارسی:
```latex
\begin{enumerate}
\item یک مجموعهٔ !!^a{denumerable} به نام~$\PVar$ از
  !!{propositional variable}s، یعنی $\Obj p_0$،
  $\Obj p_1$، \dots
\tagitem{prvFalse}{ثابت گزاره‌ایِ !!{falsity}~$\lfalse$.}{}
\tagitem{prvTrue}{ثابت گزاره‌ایِ !!{truth}~$\ltrue$.}{}
\item رابط‌های منطقی:
  \startycommalist
  \iftag{prvNot}{\ycomma $\lnot$ (نفی)}{}%
  \iftag{prvAnd}{\ycomma $\land$ (عطف)}{}%
  \iftag{prvOr}{\ycomma $\lor$ (فصل)}{}%
  \iftag{prvIf}{\ycomma $\lif$ (!!{conditional})}{}%
  \iftag{prvIff}{\ycomma $\liff$ (!!{biconditional})}{}%
\item نشانه‌های سجاوندی: ( و )، و نیز ویرگول.
\end{enumerate}
```

</details>

### OLP-0058-P08

نام زبان و زیرنویس صفر عیناً حفظ شده و ادعای انتخاب تنها زبان ممکن نشده است.
شواهد: MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
We denote this language of propositional logic by $\Lang L_0$.
```

ترجمهٔ فارسی:
```latex
این زبان منطق گزاره‌ای را با $\Lang L_0$ نشان می‌دهیم.
```

</details>

### OLP-0058-P09

فهرست نمادهای تعریف‌شده با همهٔ شاخه‌ها بررسی شد. در پروفایل جاری شاخه تهی است اما نقطهٔ پس از آن باقی می‌ماند؛ این اثر قالب منبع جدا ثبت شد.
شواهد: MT9-CONNECTIVES.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: واژهٔ اولیه و تعریف‌شده در این صفحات به همین تقابل اختصاصی تصریح نشده‌اند؛ معنای توضیح بند بعد مبنای تصمیم است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\iftag{defNot,defOr,defAnd,defIf,defIff,defTrue,defFalse,defEx,defAll}{%
In addition to the primitive connectives introduced
above, we also use the following \emph{defined} symbols:
\startycommalist
  \iftag{defNot}{\ycomma $\lnot$ (negation)}{}%
  \iftag{defAnd}{\ycomma $\land$ (conjunction)}{}%
  \iftag{defOr}{\ycomma $\lor$ (disjunction)}{}%
  \iftag{defIf}{\ycomma $\lif$ (!!{conditional})}{}%
  \iftag{defIff}{\ycomma $\liff$ (!!{biconditional})}{}%
  \iftag{defFalse}{\ycomma $\lfalse$ (!!{falsity})}{}%
  \iftag{defTrue}{\ycomma $\ltrue$ (!!{truth})}}{}.
```

ترجمهٔ فارسی:
```latex
\iftag{defNot,defOr,defAnd,defIf,defIff,defTrue,defFalse,defEx,defAll}{%
افزون بر رابط‌های اولیه‌ای که در بالا معرفی شدند، از نمادهای
\emph{تعریف‌شدهٔ} زیر نیز استفاده می‌کنیم:
\startycommalist
  \iftag{defNot}{\ycomma $\lnot$ (نفی)}{}%
  \iftag{defAnd}{\ycomma $\land$ (عطف)}{}%
  \iftag{defOr}{\ycomma $\lor$ (فصل)}{}%
  \iftag{defIf}{\ycomma $\lif$ (!!{conditional})}{}%
  \iftag{defIff}{\ycomma $\liff$ (!!{biconditional})}{}%
  \iftag{defFalse}{\ycomma $\lfalse$ (!!{falsity})}{}%
  \iftag{defTrue}{\ycomma $\ltrue$ (!!{truth})}}{}.
```

</details>

### OLP-0058-P10

اختصار غیرصوری، خارج‌بودن نماد تعریف‌شده از الفبای رسمی و کوتاه‌شدن برهان‌ها حفظ شدند. متن ادعای نویسنده را گزارش می‌کند و برهان تازه‌ای اضافه نمی‌کند.
شواهد: I7-FREE, MT9-ATOMIC.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{tagblock}{defNot,defOr,defAnd,defIf,defIff,defTrue,defFalse,defEx,defAll}
\begin{explain}
A defined symbol is not officially part of the language, but is
introduced as an informal abbreviation: it allows us to abbreviate
formulas which would, if we only used primitive symbols, get quite
long.  This is obviously an advantage.  The bigger advantage, however,
is that proofs become shorter.  If a symbol is primitive, it has to be
treated separately in proofs. The more primitive symbols, therefore,
the longer our proofs.
\end{explain}
\end{tagblock}
```

ترجمهٔ فارسی:
```latex
\begin{tagblock}{defNot,defOr,defAnd,defIf,defIff,defTrue,defFalse,defEx,defAll}
\begin{explain}
نماد تعریف‌شده رسماً جزئی از زبان نیست، بلکه به‌عنوان اختصاری غیرصوری
معرفی می‌شود: چنین نمادی به ما امکان می‌دهد فرمول‌هایی را کوتاه کنیم که
اگر فقط از نمادهای اولیه استفاده می‌کردیم، بسیار طولانی می‌شدند. این مزیت
آشکار است؛ اما مزیت بزرگ‌تر آن است که برهان‌ها کوتاه‌تر می‌شوند. اگر نمادی
اولیه باشد، باید در برهان‌ها جداگانه بررسی شود. بنابراین هرچه شمار نمادهای
اولیه بیشتر باشد، برهان‌های ما طولانی‌تر خواهند بود.
\end{explain}
\end{tagblock}
```

</details>

### OLP-0058-P11

یادداشت انگلیسیِ غیرفعال دربارهٔ نمادهای جایگزین، شاهد فنی است؛ به متن فارسیِ خواننده راه نمی‌یابد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
% Alternate symbols
```

ترجمهٔ فارسی:
```latex
% Alternate symbols
```

</details>

### OLP-0058-P12

نمادهای نفی، عطف، شرطی و دوشرطی دقیقاً حفظ‌اند؛ نام‌های لاتینی و بالا/پایین توضیح نام‌های منبع‌اند، نه اصطلاحات اثباتاً رایج فارسی. علامت !\ در خود منبع است و به‌عنوان خطای تازه تغییر نکرد.
شواهد: MT9-CONNECTIVES.
اطمینان تحریری: 2 از ۴.
نیازمند بررسی: معادل‌های فالسوم، وروم، محال و بالا/پایین در کانن حاضر شاهد مستقیم ندارند؛ برای بررسی تخصصی علامت‌گذاری شده‌اند.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{intro}
You may be familiar with different terminology and symbols than the
ones we use above. Logic texts (and teachers) commonly use either
$\sim$, $\neg$, and~!\ for ``negation'', $\wedge$, $\cdot$, and $\&$
for ``conjunction''.  Commonly used symbols for the ``conditional'' or
``implication'' are $\rightarrow$, $\Rightarrow$, and $\supset$.
\iftag{prvIff,defIff}{Symbols for ``biconditional,'' ``bi-implication,''
  or ``(material) equivalence'' are $\leftrightarrow$,
  $\Leftrightarrow$, and $\equiv$.}{}
\iftag{prvFalse,defFalse}{The $\lfalse$ symbol is variously called
  ``falsity,'' ``falsum,'' ``absurdity,'' or ``bottom.''}{}
\iftag{prvTrue,defTrue}{The $\ltrue$ symbol is variously called
  ``truth,'' ``verum,'' or ``top.''}{}
\end{intro}
```

ترجمهٔ فارسی:
```latex
\begin{intro}
ممکن است با اصطلاح‌ها و نمادهایی متفاوت از آنچه در بالا به کار بردیم آشنا
باشید. متون منطق (و مدرسان) معمولاً یکی از نمادهای $\sim$، $\neg$ و~!\ را
برای «نفی»، و یکی از نمادهای $\wedge$، $\cdot$ و $\&$ را برای «عطف» به
کار می‌برند. نمادهای رایج برای «شرطی» یا «استلزام» عبارت‌اند از
$\rightarrow$، $\Rightarrow$ و $\supset$.
\iftag{prvIff,defIff}{نمادهای «دوشرطی»، «استلزام دوسویه» یا «هم‌ارزی
  (مادی)» عبارت‌اند از $\leftrightarrow$،
  $\Leftrightarrow$ و $\equiv$.}{}
\iftag{prvFalse,defFalse}{نماد $\lfalse$ را به نام‌های «کذب»، «فالسوم»،
  «محال» یا «پایین» نیز می‌خوانند.}{}
\iftag{prvTrue,defTrue}{نماد $\ltrue$ را به نام‌های «صدق»، «وروم» یا
  «بالا» نیز می‌خوانند.}{}
\end{intro}
```

</details>

### OLP-0058-P13

شروع تعریف استقرایی و ثابت کذب به‌عنوان فرمول اتمی حفظ شد؛ اتمی با بسیط معنایی خلط نشد.
شواهد: MT9-ATOMIC, I6-INDUCTIVE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{defn}[Formula]
\ollabel{defn:formulas}
The set~$\Frm[L_0]$ of \emph{!!{formula}s} of propositional logic
is defined inductively as follows:
\begin{enumerate}
\tagitem{prvFalse}{$\lfalse$ is an atomic !!{formula}.}{}
```

ترجمهٔ فارسی:
```latex
\begin{defn}[فرمول]
\ollabel{defn:formulas}
مجموعهٔ~$\Frm[L_0]$ از \emph{!!{formula}sی} منطق گزاره‌ای به‌صورت استقرایی
چنین تعریف می‌شود:
\begin{enumerate}
\tagitem{prvFalse}{$\lfalse$ یک !!{formula} اتمی است.}{}
```

</details>

### OLP-0058-P14

ثابت صدق نیز در شاخهٔ خودش اتمی است؛ شرط برچسب محفوظ است.
شواهد: MT9-ATOMIC.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvTrue}{$\ltrue$ is an atomic !!{formula}.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvTrue}{$\ltrue$ یک !!{formula} اتمی است.}{}
```

</details>

### OLP-0058-P15

هر متغیر گزاره‌ای فرمول اتمی است؛ عکس این ادعا گفته نشده است.
شواهد: MT9-ATOMIC.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\item Every !!{propositional variable}~$\Obj p_i$ is an atomic
  !!{formula}.
```

ترجمهٔ فارسی:
```latex
\item هر !!{propositional variable}~$\Obj p_i$ یک !!{formula} اتمی است.
```

</details>

### OLP-0058-P16

قاعدهٔ ساخت نفی با فرض فرمول‌بودن اجزا و نتیجهٔ فرمول‌بودن مرکب مقابله شد؛ پرانتزها و متغیرهای همان بند دقیقاً حفظ‌اند.
شواهد: MT9-ATOMIC, I6-INDUCTIVE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvNot}{If $!A$ is !!a{formula}, then $\lnot !A$ is
  !!a{formula}.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvNot}{اگر $!A$ یک !!a{formula} باشد، آنگاه $\lnot !A$ یک
  !!a{formula} است.}{}
```

</details>

### OLP-0058-P17

قاعدهٔ ساخت عطف با فرض فرمول‌بودن اجزا و نتیجهٔ فرمول‌بودن مرکب مقابله شد؛ پرانتزها و متغیرهای همان بند دقیقاً حفظ‌اند.
شواهد: MT9-ATOMIC, I6-INDUCTIVE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvAnd}{If $!A$ and $!B$ are !!{formula}s, then $(!A \land
  !B)$ is !!a{formula}.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvAnd}{اگر $!A$ و $!B$ از !!{formula}s باشند، آنگاه $(!A \land
  !B)$ یک !!a{formula} است.}{}
```

</details>

### OLP-0058-P18

قاعدهٔ ساخت فصل با فرض فرمول‌بودن اجزا و نتیجهٔ فرمول‌بودن مرکب مقابله شد؛ پرانتزها و متغیرهای همان بند دقیقاً حفظ‌اند.
شواهد: MT9-ATOMIC, I6-INDUCTIVE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvOr}{If $!A$ and $!B$ are !!{formula}s, then $(!A \lor !B)$
  is !!a{formula}.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvOr}{اگر $!A$ و $!B$ از !!{formula}s باشند، آنگاه $(!A \lor !B)$
  یک !!a{formula} است.}{}
```

</details>

### OLP-0058-P19

قاعدهٔ ساخت شرطی با فرض فرمول‌بودن اجزا و نتیجهٔ فرمول‌بودن مرکب مقابله شد؛ پرانتزها و متغیرهای همان بند دقیقاً حفظ‌اند.
شواهد: MT9-ATOMIC, I6-INDUCTIVE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvIf}{If $!A$ and $!B$ are !!{formula}s, then $(!A \lif !B)$
  is !!a{formula}.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvIf}{اگر $!A$ و $!B$ از !!{formula}s باشند، آنگاه $(!A \lif !B)$
  یک !!a{formula} است.}{}
```

</details>

### OLP-0058-P20

قاعدهٔ ساخت دوشرطی با فرض فرمول‌بودن اجزا و نتیجهٔ فرمول‌بودن مرکب مقابله شد؛ پرانتزها و متغیرهای همان بند دقیقاً حفظ‌اند.
شواهد: MT9-ATOMIC, I6-INDUCTIVE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvIff}{If $!A$ and $!B$ are !!{formula}s, then $(!A \liff !B)$
  is !!a{formula}.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvIff}{اگر $!A$ و $!B$ از !!{formula}s باشند، آنگاه $(!A \liff !B)$
  یک !!a{formula} است.}{}
```

</details>

### OLP-0058-P21

بند انحصار هیچ چیز دیگر، بسته‌بودن تعریف را بیان می‌کند؛ به ادعای معنایی دربارهٔ صدق تبدیل نشده است.
شواهد: MT9-ATOMIC.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{limitClause}{Nothing else is !!a{formula}.}{}
\end{enumerate}
\end{defn}
```

ترجمهٔ فارسی:
```latex
\tagitem{limitClause}{هیچ چیز دیگری !!a{formula} نیست.}{}
\end{enumerate}
\end{defn}
```

</details>

### OLP-0058-P22

مراحل بی‌شمارِ ساخت با فرمول منفرد متناهی خلط نشده‌اند؛ مرحلهٔ پایه همهٔ اتمی‌ها را شامل است و هر دو ثابت شرطی بررسی شدند.
شواهد: I6-INDUCTIVE, MT9-ATOMIC.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{explain}
The definition of !!{formula}s is an
\emph{inductive definition}.  Essentially, we construct the set of
!!{formula}s in infinitely many stages.  In the initial stage, we
pronounce all atomic formulas to be formulas; this corresponds to the
first few cases of the definition, i.e., the cases for
\iftag{prvTrue}{$\ltrue$, }{}%
\iftag{prvFalse}{$\lfalse$, }{}%
$\Obj p_i$.  ``Atomic !!{formula}''
thus means any !!{formula} of this form.
```

ترجمهٔ فارسی:
```latex
\begin{explain}
تعریف !!{formula}s یک \emph{تعریف استقرایی} است. در اصل، مجموعهٔ
!!{formula}s را در بی‌نهایت مرحله می‌سازیم. در مرحلهٔ آغازین، همهٔ
فرمول‌های اتمی را فرمول اعلام می‌کنیم؛ این مرحله با چند حالت نخست تعریف،
یعنی حالت‌های
\iftag{prvTrue}{$\ltrue$، }{}%
\iftag{prvFalse}{$\lfalse$، }{}%
$\Obj p_i$ متناظر است. پس «!!{formula} اتمی» یعنی هر !!{formula}ی که یکی از
این صورت‌ها را داشته باشد.
```

</details>

### OLP-0058-P23

مراحل دوم و سوم از ساخته‌های قبلی استفاده می‌کنند؛ eventually یک مرحلهٔ متناهی برای هر فرمول است، نه فرمولی حاصل از حد بی‌نهایت.
شواهد: I6-INDUCTIVE, I7-FREE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
The other cases of the definition give rules for constructing new
!!{formula}s out of !!{formula}s already constructed.  At the second
stage, we can use them to construct !!{formula}s out of atomic
!!{formula}s.  At the third stage, we construct new formulas from the
atomic formulas and those obtained in the second stage, and so on.  A
!!{formula} is anything that is eventually constructed at such a
stage, and nothing else.
\end{explain}
```

ترجمهٔ فارسی:
```latex
حالت‌های دیگر تعریف، قواعدی برای ساختن !!{formula}sی تازه از
!!{formula}sی پیش‌ترساخته به دست می‌دهند. در مرحلهٔ دوم می‌توانیم
با آن قواعد !!{formula}s را از !!{formula}sی اتمی بسازیم. در
مرحلهٔ سوم، فرمول‌های تازه را از فرمول‌های اتمی و فرمول‌های به‌دست‌آمده در
مرحلهٔ دوم می‌سازیم و همین‌طور ادامه می‌دهیم. اصطلاح «!!{formula}» بر هر
چیزی اطلاق می‌شود که سرانجام در یکی از این مراحل ساخته شود، و نه هیچ چیز
دیگر.
\end{explain}
```

</details>

### OLP-0058-P24

فقط بیرونی‌ترین جفت پرانتز از رابط دوجایگاهی حذف می‌شود؛ رشتهٔ رسمی و کوتاه‌نویسی خلط نشده‌اند.
شواهد: MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: دوجایگاهی با دوموضعیِ کانن هم‌معناست؛ اختلاف سبک ثبت است و برای یکدستیِ بی‌دلیل کل کتاب تغییر داده نشده.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
When writing a formula $(!B \ast !C)$ constructed from $!B$, $!C$
using a two-place connective~$\ast$, we will often leave out the
outermost pair of parentheses and write simply~$!B \ast !C$.
```

ترجمهٔ فارسی:
```latex
هنگام نوشتن فرمول $(!B \ast !C)$ که از $!B$ و $!C$ با استفاده از یک رابط
دوجایگاهی~$\ast$ ساخته شده است، اغلب بیرونی‌ترین جفت پرانتز را حذف می‌کنیم
و فقط~$!B \ast !C$ می‌نویسیم.
```

</details>

### OLP-0058-P25

توضیح عملگرهای تعریف‌شده آغاز می‌شود؛ هیچ شاخهٔ خامی حذف نشده است.
شواهد: I7-FREE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{tagblock}{defNot,defOr,defAnd,defIf,defIff,defTrue,defFalse,defEx,defAll}
\begin{defn}
Formulas constructed using the defined operators are to be understood
as follows:
```

ترجمهٔ فارسی:
```latex
\begin{tagblock}{defNot,defOr,defAnd,defIf,defIff,defTrue,defFalse,defEx,defAll}
\begin{defn}
فرمول‌های ساخته‌شده با عملگرهای تعریف‌شده را باید چنین فهمید:
```

</details>

### OLP-0058-P26

محیط شمارش شرطی عیناً حفظ شد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{tagenumerate}{defTrue,defFalse,defNot,defOr,defAnd,defIf,defIff,defEx,defAll}
```

ترجمهٔ فارسی:
```latex
\begin{tagenumerate}{defTrue,defFalse,defNot,defOr,defAnd,defIf,defIff,defEx,defAll}
```

</details>

### OLP-0058-P27

اختصار صدق با نفی کذب یا طرد شق ثالث و همهٔ گزینه‌های برچسبی آن از انگلیسی به فارسی مقابله شدند. در صورت وجود فرمول اتمی ثابت، قید ثابت حفظ است.
شواهد: MT9-CONNECTIVES, I7-FREE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: این شواهد فارسی همهٔ تعریف‌های خاص OLP را اثبات یا تجویز نمی‌کنند؛ فرمول خود منبع مرجع محتواست.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{defTrue}{$\ltrue$ abbreviates
  \iftag{prvFalse}{$\lnot\lfalse$}{$(!A \lor \lnot !A)$ for some
    fixed atomic !!{formula}~$!A$}.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{defTrue}{$\ltrue$ اختصارِ
  \iftag{prvFalse}{$\lnot\lfalse$}{$(!A \lor \lnot !A)$ برای یک
    !!{formula} اتمی ثابت~$!A$} است.}{}
```

</details>

### OLP-0058-P28

اختصار کذب با نفی صدق یا تناقض و همهٔ گزینه‌های برچسبی آن از انگلیسی به فارسی مقابله شدند. در صورت وجود فرمول اتمی ثابت، قید ثابت حفظ است.
شواهد: MT9-CONNECTIVES, I7-FREE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: این شواهد فارسی همهٔ تعریف‌های خاص OLP را اثبات یا تجویز نمی‌کنند؛ فرمول خود منبع مرجع محتواست.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{defFalse}{$\lfalse$ abbreviates
  \iftag{prvTrue}{$\lnot\ltrue$}{$(!A \land \lnot !A)$ for some
    fixed atomic !!{formula}~$!A$}.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{defFalse}{$\lfalse$ اختصارِ
  \iftag{prvTrue}{$\lnot\ltrue$}{$(!A \land \lnot !A)$ برای یک
    !!{formula} اتمی ثابت~$!A$} است.}{}
```

</details>

### OLP-0058-P29

اختصار نفی با شرطی و کذب و همهٔ گزینه‌های برچسبی آن از انگلیسی به فارسی مقابله شدند. در صورت وجود فرمول اتمی ثابت، قید ثابت حفظ است.
شواهد: MT9-CONNECTIVES, I7-FREE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: این شواهد فارسی همهٔ تعریف‌های خاص OLP را اثبات یا تجویز نمی‌کنند؛ فرمول خود منبع مرجع محتواست.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{defNot}{$\lnot !A$ abbreviates $!A \lif \lfalse$.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{defNot}{$\lnot !A$ اختصارِ $!A \lif \lfalse$ است.}{}
```

</details>

### OLP-0058-P30

اختصار فصل با نفی عطف یا شرطی و همهٔ گزینه‌های برچسبی آن از انگلیسی به فارسی مقابله شدند. در صورت وجود فرمول اتمی ثابت، قید ثابت حفظ است.
شواهد: MT9-CONNECTIVES, I7-FREE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: این شواهد فارسی همهٔ تعریف‌های خاص OLP را اثبات یا تجویز نمی‌کنند؛ فرمول خود منبع مرجع محتواست.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{defOr}{$!A \lor !B$ abbreviates
  \iftag{prvAnd}{$\lnot(\lnot !A \land \lnot !B)$}{$\lnot !A \lif
    !B$}.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{defOr}{$!A \lor !B$ اختصارِ
  \iftag{prvAnd}{$\lnot(\lnot !A \land \lnot !B)$}{$\lnot !A \lif
    !B$} است.}{}
```

</details>

### OLP-0058-P31

اختصار عطف با نفی فصل یا نفی شرطی و همهٔ گزینه‌های برچسبی آن از انگلیسی به فارسی مقابله شدند. در صورت وجود فرمول اتمی ثابت، قید ثابت حفظ است.
شواهد: MT9-CONNECTIVES, I7-FREE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: این شواهد فارسی همهٔ تعریف‌های خاص OLP را اثبات یا تجویز نمی‌کنند؛ فرمول خود منبع مرجع محتواست.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{defAnd}{$!A \land !B$ abbreviates
  \iftag{prvOr}{$\lnot(\lnot !A \lor \lnot !B)$}{$\lnot (!A \lif
    \lnot !B)$}.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{defAnd}{$!A \land !B$ اختصارِ
  \iftag{prvOr}{$\lnot(\lnot !A \lor \lnot !B)$}{$\lnot (!A \lif
    \lnot !B)$} است.}{}
```

</details>

### OLP-0058-P32

اختصار شرطی با فصل یا نفی عطف و همهٔ گزینه‌های برچسبی آن از انگلیسی به فارسی مقابله شدند. در صورت وجود فرمول اتمی ثابت، قید ثابت حفظ است. پرانتز باز افزوده‌شده در فارسی از قبل موجود بود و با پیش‌تصویر صریح ثبت شد.
شواهد: MT9-CONNECTIVES, I7-FREE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: این شواهد فارسی همهٔ تعریف‌های خاص OLP را اثبات یا تجویز نمی‌کنند؛ فرمول خود منبع مرجع محتواست.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{defIf}{$!A \lif !B$ abbreviates
  \iftag{prvOr}{$\lnot !A \lor !B)$}{$\lnot (!A \land \lnot !B)$}.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{defIf}{$!A \lif !B$ اختصارِ
  \iftag{prvOr}{$(\lnot !A \lor !B)$}{$\lnot (!A \land \lnot !B)$} است.}{}
```

</details>

### OLP-0058-P33

اختصار دوشرطی با عطف دو جهت شرطی و همهٔ گزینه‌های برچسبی آن از انگلیسی به فارسی مقابله شدند. در صورت وجود فرمول اتمی ثابت، قید ثابت حفظ است.
شواهد: MT9-CONNECTIVES, I7-FREE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: این شواهد فارسی همهٔ تعریف‌های خاص OLP را اثبات یا تجویز نمی‌کنند؛ فرمول خود منبع مرجع محتواست.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{defIff}{$!A \liff !B$ abbreviates $(!A \lif !B) \land (!B
  \lif !A)$.}{}
\end{tagenumerate}
\end{defn}
\end{tagblock}
```

ترجمهٔ فارسی:
```latex
\tagitem{defIff}{$!A \liff !B$ اختصارِ $(!A \lif !B) \land (!B
  \lif !A)$ است.}{}
\end{tagenumerate}
\end{defn}
\end{tagblock}
```

</details>

### OLP-0058-P34

همانی نحوی به برابری طول و تک‌تک نمادها محدود است؛ هم‌ارزی معنایی جای آن ننشسته است.
شواهد: MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: برای همانی نحوی در صفحات خوانده‌شده شاهد عین‌عبارت نداریم؛ تعریف صریح منبع مبنای حفظ موقت آن است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{defn}[Syntactic identity]
The symbol $\ident$ expresses syntactic identity between strings of
symbols, i.e., $!A \ident !B$ iff $!A$ and $!B$ are strings of symbols
of the same length and which contain the same symbol in each place.
\end{defn}
```

ترجمهٔ فارسی:
```latex
\begin{defn}[همانی نحوی]
نماد $\ident$ همانی نحوی میان رشته‌های نمادها را بیان می‌کند؛ یعنی
$!A \ident !B$ اگر و تنها اگر $!A$ و $!B$ رشته‌هایی از نمادها باشند که
طول یکسان دارند و در هر جایگاه نماد یکسانی دارند.
\end{defn}
```

</details>

### OLP-0058-P35

ترتیب الحاق، پرانتز اول، شروع زیررشته از نماد دوم و نماد پس از آن دقیقاً حفظ‌اند.
شواهد: MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: الحاق و زیررشته در کانن حاضر شاهد مستقیم ندارند؛ تعریف رشته‌ای همان بند تکیه‌گاه معنایی است و نیاز واژگانی ثبت شد.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
The $\ident$ symbol may be flanked by strings obtained by
concatenation, e.g., $!A \ident (!B \lor !C)$ means: the string of
symbols~$!A$ is the same string as the one obtained by concatenating
an opening parenthesis, the string $!B$, the $\lor$ symbol, the
string~$!C$, and a closing parenthesis, in this order. If this is the
case, then we know that the first symbol of $!A$ is an opening
parenthesis, $!A$ contains $!B$ as a substring (starting at the second
symbol), that substring is followed by $\lor$, etc.
```

ترجمهٔ فارسی:
```latex
در دو سوی نماد $\ident$ می‌توان رشته‌هایی را قرار داد که با الحاق به دست
آمده‌اند. برای نمونه، $!A \ident (!B \lor !C)$ یعنی رشتهٔ نمادهای~$!A$
همان رشته‌ای است که با الحاق یک پرانتز باز، رشتهٔ $!B$، نماد $\lor$، رشتهٔ
$!C$ و یک پرانتز بسته، به همین ترتیب، به دست می‌آید. اگر چنین باشد، می‌دانیم
نخستین نماد $!A$ یک پرانتز باز است، $!A$ رشتهٔ $!B$ را به‌عنوان زیررشته‌ای
در بر دارد که از نماد دوم آغاز می‌شود، پس از آن زیررشته نماد $\lor$ می‌آید،
و به همین ترتیب.
```

</details>

### OLP-0059-P04

شناسهٔ فایل حفظ شد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olfileid{pl}{syn}{pre}
```

ترجمهٔ فارسی:
```latex
\olfileid{pl}{syn}{pre}
```

</details>

### OLP-0059-P05

مقدمات عنوان بخش شامل استقرا، خوانش و جانشینی است؛ محتوا محدود به مبانی عددی نشده است.
شواهد: MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olsection{Preliminaries}
```

ترجمهٔ فارسی:
```latex
\olsection{مقدمات}
```

</details>

### OLP-0059-P06

اصل استقرا: همهٔ اتمی‌ها، هر پنج گام سازنده و نتیجهٔ همگانی حفظ‌اند. جهت شرط از اجزا به مرکب در هر مورد جداگانه بررسی شد.
شواهد: I6-INDUCTIVE, MT9-ATOMIC.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{thm}[\emph{Principle of induction on !!{formula}s}]
  \ollabel{thm:induction}  
  If some property~$P$ holds for all the atomic !!{formula}s and is
  such that
  \begin{enumerate}
    \tagitem{prvNot}{it holds for $\lnot !A$ whenever it holds
      for~$!A$;}{}
    \tagitem{prvAnd}{it holds for $(!A \land !B)$
      whenever it holds for $!A$ and~$!B$;}{}
    \tagitem{prvOr}{it holds for $(!A \lor !B)$
      whenever it holds for $!A$ and~$!B$;}{}
    \tagitem{prvIf}{it holds for $(!A \lif !B)$
      whenever it holds for $!A$ and~$!B$;}{}
    \tagitem{prvIff}{it holds for $(!A \liff !B)$
      whenever it holds for $!A$ and~$!B$;}{}
  \end{enumerate}
  then $P$ holds for all !!{formula}s.
\end{thm}
```

ترجمهٔ فارسی:
```latex
\begin{thm}[\emph{اصل استقرا بر !!{formula}s}]
  \ollabel{thm:induction}
  اگر ویژگی‌ای چون~$P$ برای همهٔ !!{formula}sی اتمی برقرار باشد و
  چنان باشد که
  \begin{enumerate}
    \tagitem{prvNot}{برقراری آن برای $\lnot !A$ از برقراری آن برای~$!A$
      نتیجه شود؛}{}
    \tagitem{prvAnd}{برقراری آن برای $(!A \land !B)$ از برقراری آن برای $!A$
      و~$!B$ نتیجه شود؛}{}
    \tagitem{prvOr}{برقراری آن برای $(!A \lor !B)$ از برقراری آن برای $!A$
      و~$!B$ نتیجه شود؛}{}
    \tagitem{prvIf}{برقراری آن برای $(!A \lif !B)$ از برقراری آن برای $!A$
      و~$!B$ نتیجه شود؛}{}
    \tagitem{prvIff}{برقراری آن برای $(!A \liff !B)$ از برقراری آن برای $!A$
      و~$!B$ نتیجه شود؛}{}
  \end{enumerate}
  آنگاه $P$ برای همهٔ !!{formula}s برقرار است.
\end{thm}
```

</details>

### OLP-0059-P07

دو شمول، بسته‌بودن تحت عملگرها و کمینگی دقیقاً محفوظ‌اند. کسرهٔ نادرست پیش از از اصلاح شد؛ جمع‌آوری همهٔ فرمول‌های دارای P به وجود مدل تعبیر نشده است.
شواهد: I7-CLASS, I6-INDUCTIVE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
  Let $S$ be the collection of all !!{formula}s with
  property~$P$. Clearly $S \subseteq \Frm[L_0]$. $S$~satisfies all the
  conditions of \olref[fml]{defn:formulas}: it contains all atomic
  !!{formula}s and is closed under the !!{operator}s.  $\Frm[L_0]$ is
  the smallest such class, so $\Frm[L_0] \subseteq S$. So $\Frm[L_0] = S$, and
  every formula has property~$P$.
\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
  بگذارید $S$ مجموعهٔ همهٔ !!{formula}sی دارای ویژگی~$P$ باشد. آشکارا
  $S \subseteq \Frm[L_0]$. مجموعهٔ~$S$ همهٔ شرط‌های
  \olref[fml]{defn:formulas} را برآورده می‌کند: همهٔ !!{formula}sی اتمی را
  در بر می‌گیرد و تحت !!{operator}s بسته است.  $\Frm[L_0]$ کوچک‌ترین رده
  از این دست است، پس $\Frm[L_0] \subseteq S$. بنابراین $\Frm[L_0] = S$، و
  هر فرمول ویژگی~$P$ را دارد.
\end{proof}
```

</details>

### OLP-0059-P08

متوازن صریحاً با برابر بودن شمار پرانتزهای باز و بسته تعریف می‌شود؛ به درستیِ ترتیب هر پیشوند تعمیم داده نشده است.
شواهد: MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}\ollabel{prop:balanced}
   Any !!{formula} in~$\Frm[L_0]$ is \emph{balanced}, in that it has
   as many left parentheses as right ones.
\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop}\ollabel{prop:balanced}
   هر !!{formula} در~$\Frm[L_0]$ \emph{متوازن} است، به این معنا که شمار
   پرانتزهای باز آن با شمار پرانتزهای بسته برابر است.
\end{prop}
```

</details>

### OLP-0059-P09

جملهٔ تمرین روان شد؛ همان گزارهٔ توازن باید اثبات شود.
شواهد: MT11-SAT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob}
Prove \olref[pl][syn][pre]{prop:balanced}
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob}
گزارهٔ \olref[pl][syn][pre]{prop:balanced} را ثابت کنید.
\end{prob}
```

</details>

### OLP-0059-P10

proper initial segment با قطعهٔ آغازین سره حفظ شده؛ کل رشته از ادعا کنار می‌رود و واژهٔ سره حذف نشده است.
شواهد: MT9-ATOMIC, MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: شاهد خاص قطعهٔ آغازین سره در دو منبع حاضر یافت نشد؛ این معادل تعریف‌محور موقت است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop} \ollabel{prop:noinit}
No proper initial segment of !!a{formula} is !!a{formula}.
\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop} \ollabel{prop:noinit}
هیچ قطعهٔ آغازینِ سره‌ای از !!a{formula}، خود !!a{formula} نیست.
\end{prop}
```

</details>

### OLP-0059-P11

جملهٔ تمرین روان شد؛ همان گزارهٔ پیشوند سره باید اثبات شود.
شواهد: MT11-SAT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob}
  Prove \olref[pl][syn][pre]{prop:noinit}
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob}
  گزارهٔ \olref[pl][syn][pre]{prop:noinit} را ثابت کنید.
\end{prob}
```

</details>

### OLP-0059-P12

خوانش یکتا به تجزیهٔ صوری مربوط است؛ ادعا شامل ثابت کذب و حالت‌های بعدی است.
شواهد: MT9-ATOMIC, MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: شاهد عین‌عبارت خوانش یکتا یا تجزیه در صفحات حاضر وجود ندارد؛ معنای تعریف منبع معیار تصمیم موقت است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}[Unique Readability]
Any !!{formula}~$!A$ in $ \Frm[L_0]$ has exactly one parsing as one of
the following
\begin{enumerate}
\tagitem{prvFalse}{$\lfalse$.}{}
```

ترجمهٔ فارسی:
```latex
\begin{prop}[خوانش یکتا]
هر !!{formula}~$!A$ در $ \Frm[L_0]$ دقیقاً یک تجزیه به یکی از
صورت‌های زیر دارد:
\begin{enumerate}
\tagitem{prvFalse}{$\lfalse$.}{}
```

</details>

### OLP-0059-P13

حالت ثابت صدق فقط فرمول و شرط نمایش دارد و عیناً حفظ است.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvTrue}{$\ltrue$.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvTrue}{$\ltrue$.}{}
```

</details>

### OLP-0059-P14

حالت متغیر گزاره‌ای و تعلق آن به PVar حفظ شد؛ برای یک در اینجا وجودی است نه یکتایی نامربوط شاخص.
شواهد: MT9-ATOMIC.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\item $\Obj p_n$ for some $\Obj p_n \in  \PVar$.
```

ترجمهٔ فارسی:
```latex
\item $\Obj p_n$ برای یک $\Obj p_n \in  \PVar$.
```

</details>

### OLP-0059-P15

حالت تجزیهٔ نفی با وجود فرمول‌های سازنده و نمادهای همان سطر حفظ است.
شواهد: MT9-ATOMIC, MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvNot}{$\lnot !B$ for some !!{formula}~$!B$.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvNot}{$\lnot !B$ برای یک !!{formula}~$!B$.}{}
```

</details>

### OLP-0059-P16

حالت تجزیهٔ عطف با وجود فرمول‌های سازنده و نمادهای همان سطر حفظ است.
شواهد: MT9-ATOMIC, MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvAnd}{$(!B \land !C)$ for some !!{formula}s $!B$ and~$!C$.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvAnd}{$(!B \land !C)$ به‌ازای !!{formula}sی $!B$ و~$!C$.}{}
```

</details>

### OLP-0059-P17

حالت تجزیهٔ فصل با وجود فرمول‌های سازنده و نمادهای همان سطر حفظ است.
شواهد: MT9-ATOMIC, MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvOr}{$(!B \lor !C)$ for some !!{formula}s $!B$ and~$!C$.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvOr}{$(!B \lor !C)$ به‌ازای !!{formula}sی $!B$ و~$!C$.}{}
```

</details>

### OLP-0059-P18

حالت تجزیهٔ شرطی با وجود فرمول‌های سازنده و نمادهای همان سطر حفظ است.
شواهد: MT9-ATOMIC, MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvIf}{$(!B \lif !C)$ for some !!{formula}s $!B$ and~$!C$.}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvIf}{$(!B \lif !C)$ به‌ازای !!{formula}sی $!B$ و~$!C$.}{}
```

</details>

### OLP-0059-P19

حالت تجزیهٔ دوشرطی با وجود فرمول‌های سازنده و نمادهای همان سطر حفظ است. تأکید پایانی بر یکتایی نیز حفظ شده است.
شواهد: MT9-ATOMIC, MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvIff}{$(!B \liff !C)$ for some !!{formula}s $!B$ and~$!C$.}{}
\end{enumerate}
Moreover, this parsing is \emph{unique}.
\end{prop}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvIff}{$(!B \liff !C)$ به‌ازای !!{formula}sی $!B$ و~$!C$.}{}
\end{enumerate}
افزون بر این، این تجزیه \emph{یکتا} است.
\end{prop}
```

</details>

### OLP-0059-P20

برهان استقراییِ نمونهٔ شرطی، برابری دو بخش نخست از منع پیشوند سره و سپس تناقض در دو خوانش بخش دوم را حفظ می‌کند. عبارت برای نمونه مانع ادعای ارائهٔ همهٔ حالت‌هاست.
شواهد: I6-INDUCTIVE, MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: شاهد اصطلاحی خوانش یکتا هنوز محدود است؛ هیچ اثبات تکمیلی خارج از منبع به ترجمه اضافه نشده است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
By induction on $!A$. For instance, suppose that $!A$ has two distinct
readings as $(!B \lif !C)$ and $(!B' \lif !C')$. Then $!B$ and $!B'$
must be the same (or else one would be a proper initial segment of the
other); so if the two readings of $!A$ are distinct it must be because
$!C$ and $!C'$ are distinct readings of the same sequence of symbols,
which is impossible by the inductive hypothesis.
\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
با استقرا بر $!A$. برای نمونه، فرض کنید $!A$ دو خوانش متمایز به‌صورت
$(!B \lif !C)$ و $(!B' \lif !C')$ دارد. در این صورت $!B$ و~$!B'$ باید
یکسان باشند (وگرنه یکی از آن دو قطعهٔ آغازینِ سره‌ای از دیگری خواهد بود)؛ پس اگر دو
خوانشِ $!A$ متمایز باشند، علت باید این باشد که $!C$ و~$!C'$ دو خوانش متمایز
از یک دنبالهٔ واحدِ نمادها هستند، که بنا بر فرض استقرا محال است.
\end{proof}
```

</details>

### OLP-0059-P21

تمام رخدادها باید جایگزین شوند؛ جانشینی هم‌زمان به جانشینی پیاپی تبدیل نشده و ترتیب متغیرها و فرمول‌ها ثابت است.
شواهد: I7-FREE, MT9-ATOMIC.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: جانشینی یکنواخت و رخداد در صفحات حاضر شاهد عین‌عبارت ندارند؛ تعریف صریح جایگزینی همهٔ موارد مبنای حفظ موقت و بررسی آتی است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex

\begin{defn}[Uniform Substitution]
If $!A$ and $!B$ are !!{formula}s, and $\Obj p_i$ is a !!{propositional
variable}, then $\Subst{!A}{!B}{\Obj p_i}$ denotes the result of
replacing each occurrence of $\Obj p_i$ by an occurrence of $!B$ in $!A$;
similarly, the simultaneous substitution of $\Obj p_1$, \dots,~$\Obj p_n$ by
!!{formula}s $!B_1$, \dots,~$!B_n$ is denoted by
$\SSubst{!A}{\subst{!B_1}{\Obj p_1},\dots,\subst{!B_n}{\Obj p_n}}$.
\end{defn}
```

ترجمهٔ فارسی:
```latex

\begin{defn}[جانشینی یکنواخت]
اگر $!A$ و~$!B$ از !!{formula}s باشند و $\Obj p_i$ یک !!{propositional
variable} باشد، آنگاه $\Subst{!A}{!B}{\Obj p_i}$ حاصلِ جایگزین‌کردنِ هر
رخدادِ $\Obj p_i$ با یک رخدادِ~$!B$ در~$!A$ را نشان می‌دهد؛ به همین ترتیب،
جانشینی هم‌زمانِ $\Obj p_1$، \dots،~$\Obj p_n$ با !!{formula}sی
$!B_1$، \dots،~$!B_n$ با
$\SSubst{!A}{\subst{!B_1}{\Obj p_1},\dots,\subst{!B_n}{\Obj p_n}}$ نشان داده می‌شود.
\end{defn}
```

</details>

### OLP-0059-P22

هر پنج فرمول و سه الگوی A جداگانه مقابله شدند. هر ده بازهٔ ریاضی با پرانتزِ بک‌اسلش اکنون واقعاً در کنترل فرمول شرکت دارند؛ تمرین حل یا آسان‌سازی نشده است.
شواهد: MT9-ATOMIC, I6-INDUCTIVE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob} For each of the five !!{formula}s below determine whether the 
 !!{formula} can be expressed as a substitution \( \Subst{!A}{!B}{\Obj p_i} \)
 where \( !A \) is (i) \( \Obj p_0 \); (ii) \( ( \lnot \Obj p_0 \land \Obj
 p_1) \); and (iii) \( ( ( \lnot \Obj p_0 \lif \Obj p_1 ) \land \Obj
 p_2 ) \). In each case specify the relevant substitution.
  \begin{enumerate}
    \item \( \Obj p_1 \) 
    \item \( ( \lnot \Obj p_0 \land \Obj p_0 ) \)
    \item \( ( ( \Obj p_0 \lor \Obj p_1 ) \land \Obj p_2 )  \)
    \item \( \lnot ( ( \Obj p_0 \lif \Obj p_1 ) \land \Obj p_2 ) \)
    \item \( (( \lnot ( \Obj p_0 \lif \Obj p_1 ) \lif ( \Obj p_0 \lor \Obj p_1 )) \land \lnot ( \Obj p_0 \land \Obj p_1 )) \)
  \end{enumerate}
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob} برای هر یک از پنج مورد زیر، که همگی !!{formula}s هستند، تعیین
 کنید که آیا آن !!{formula} را می‌توان به‌صورت جانشینیِ \( \Subst{!A}{!B}{\Obj p_i} \)
 نوشت که در آن \( !A \) عبارت است از (i) \( \Obj p_0 \)؛ (ii) \( ( \lnot \Obj p_0 \land \Obj
 p_1) \)؛ و (iii) \( ( ( \lnot \Obj p_0 \lif \Obj p_1 ) \land \Obj
 p_2 ) \). در هر مورد، جانشینی مربوط را مشخص کنید.
  \begin{enumerate}
    \item \( \Obj p_1 \)
    \item \( ( \lnot \Obj p_0 \land \Obj p_0 ) \)
    \item \( ( ( \Obj p_0 \lor \Obj p_1 ) \land \Obj p_2 )  \)
    \item \( \lnot ( ( \Obj p_0 \lif \Obj p_1 ) \land \Obj p_2 ) \)
    \item \( (( \lnot ( \Obj p_0 \lif \Obj p_1 ) \lif ( \Obj p_0 \lor \Obj p_1 )) \land \lnot ( \Obj p_0 \land \Obj p_1 )) \)
  \end{enumerate}
\end{prob}
```

</details>

### OLP-0059-P23

درخواست تعریف دقیق با استقرا حفظ شد؛ تعریف را خودسرانه به تمرین نیفزودیم.
شواهد: I6-INDUCTIVE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob}
Give a mathematically rigorous definition of $\Subst{!A}{!B}{p}$ by
induction.
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob}
تعریفی از نظر ریاضی دقیق برای $\Subst{!A}{!B}{p}$ با استقرا ارائه کنید.
\end{prob}
```

</details>

## یافته‌های تکمیلی و حدود بازبینی

بازبینی پنج فایل، شامل شاخه‌های خام غیرفعال، انجام شد و شش اصلاح نثر برای ادغام آماده شد. یک پرانتزِ اصلاح‌شدهٔ قبلی و یک نقطهٔ تنها ناشی از قالب شرطی جدا ثبت شدند؛ هیچ خطای تازه‌ای به بالادست ارسال نشد. برای شماری از اصطلاح‌های تخصصی شاهد مستقیمِ کافی نداریم و آن‌ها را صریحاً موقت نگه داشتیم. کنترل فرمول اکنون بازه‌های \(...\) را نیز پوشش می‌دهد؛ ده بازهٔ تمرین پیش‌تر از این کنترل بیرون بودند.
 
## منابع و حدود استناد

### IUTLOG

محسن خانی و افشین زارعی، نظریهٔ مجموعه‌ها، ۱۴۰۰؛ پیش‌نیازهای منطقی

https://khani.iut.ac.ir/sites/khani.iut.ac.ir/files/u145/jozve-kamel.pdf

نسخهٔ دانشگاهی برای مطالعهٔ محلی؛ بازنشر عمومی PDF مجاز فرض نشده و فقط نقل‌های کوتاه و ارجاع منتشر می‌شوند.

### MT

مسعود پورمهدیان و محسن خانی، مباحثی در منطق، دانشگاه صنعتی امیرکبیر، ۱۵ بهمن ۱۳۹۵؛ جلسهٔ مقدماتی

https://mohsen-khani.github.io/modeltheory/jozve1.pdf

نسخهٔ نویسندگان در صفحهٔ دوره؛ سند فارسیِ منطق مرتبهٔ اول است، نه شاهد اختصاصی همهٔ اصطلاح‌های منطق گزاره‌ای. فقط مطالعهٔ محلی، نقل کوتاه و ارجاع؛ PDF در انتشار عمومی قرار نمی‌گیرد.

- MT9-SYNTAX: «نحو»؛ صفحهٔ فایل 9، چاپی 9. عنوان نحو و پانوشت syntax؛ نماد، متغیر، پرانتز باز و بسته و تعریف فرمول در همان صفحه خوانده شد. شاهدی برای نحو است، نه گواهی خودکار تمام معادل‌های متن.
- MT9-CONNECTIVES: «ادوات بولی یا گزاره‌ای»؛ صفحهٔ فایل 9، چاپی 9. پنج رابط گزاره‌ای در بافت صوری معرفی می‌شوند. رابط در ترجمه از ادوات در این شاهد متفاوت است؛ معنای آن با فهرست نمادها و شرح منبع سنجیده شد و انحصار یک معادل ادعا نمی‌شود.
- MT9-ATOMIC: «فرمولهای بسیط (یا اتمیک)»؛ صفحهٔ فایل 9، چاپی 9. تعریف ۱۱ و ادامهٔ آن در صفحهٔ ۱۰ مبنای مقابلهٔ حالت پایه، ساخت استقرایی و شرط انحصارند. این شاهد، فرمول اتمی را از متغیر تنها و جملهٔ بدون متغیر آزاد متمایز می‌کند.
- MT10-SEMANTICS: «به صورت استقرایی»؛ صفحهٔ فایل 10، چاپی 10. تعریف صدق در ساختار و شروط نفی و عطف واقعاً خوانده شد؛ نثر نسبت‌دادن معنا و ساختار استقرایی را پشتیبانی می‌کند. ارزش‌گذاری گزاره‌ای با تعبیر مرتبهٔ اول یکی نیست و از این شاهد چنین همانی‌ای نتیجه نمی‌شود.
- MT11-SAT: «ارضاشدنی»؛ صفحهٔ فایل 11، چاپی 11. تعریف ارضاشدنی با وجود مدل برای تمام جمله‌های نظریه و پانوشت satisfiable؛ در ترجمه ارضاپذیر حفظ شد. تمایز وجود یک ارزش‌گذاری مشترک با ارزش‌گذاری جدا برای هر فرمول بررسی شد.
- I6-INDUCTIVE: «روش استقرایی»؛ صفحهٔ فایل 6، چاپی 5. تعریف ۱، حالت‌های پایه و ساخت عطف؛ نحو جمله‌های شرطی فارسی و اصطلاح فرمول در متن تخصصی شاهد دارند. تعریف مرتبهٔ اول جایگزین تعریف گزاره‌ای OLP نمی‌شود.
- I7-FREE: «متغیر آزاد»؛ صفحهٔ فایل 7، چاپی 6. ادامهٔ ساخت فرمول با نفی و سور، محدودبودن ساخت به مراحل متناهی، و تعریف جمله خوانده شد. در این فصل سورها جزو زبان گزاره‌ای نیستند؛ استفادهٔ ما اصطلاحی و روشی است.
- I7-CLASS: «رده‌ای»؛ صفحهٔ فایل 7، چاپی 6. تعریف مجموعه در پایان صفحه نمونهٔ کاربرد رده در نثر ریاضی است. این شاهد صرفاً انتخاب واژه و ساخت فارسی را پشتیبانی می‌کند؛ استدلال کمینگی از خود OLP بررسی شد.

## وضعیت انتشار

در دامنهٔ ثبت‌شده، تغییر فرمول یا ارجاع فقط با پیش‌تصویر و دلیل صریح مجاز است؛ تفاوت‌های مجاز بالا ثبت شده‌اند و ساختار محیط‌ها و ورودی‌ها حفظ شده است. ساخت خواننده و بازبینی دیداری آن در این نوبت انجام نشد. این گزارش به‌خودی‌خود رسید انتشار نیست. شواهد خصوصیِ فاقد مجوز نباید در بستهٔ عمومی بازنشر شوند.
