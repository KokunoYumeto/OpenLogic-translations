> سابقهٔ بازخوانی و دلیل انتخاب‌ها؛ وضعیت انتشار را باید از رسید همان ویرایش خواند. این گزارش به‌تنهایی رسید انتشار نیست.

# بازبینی فارسی: مجموعه‌های نامتناهی، هتل هیلبرت و جبرهای ددکیند

بازخوانی منبع، اصلاح فارسی و ثبت انتخاب‌ها: OpenAI Codex — GPT-6 Astra، کوشش Ultra. این کار بازبینی انسانی نیست.

همهٔ بندهای فعال آغاز فصل و دو بخش ۰۰۵۰ و ۰۰۵۱ با شاهد انگلیسی و متن مؤثر خواننده مقابله شده‌اند. مشورت با کانن مربوط به همین بازبینی است؛ مشورت اولیهٔ مترجم یا گواهی کل کتاب ادعا نمی‌شود. اصلاح خطای منبع، اصلاح ترجمه و پیشنهاد بهبود از هم جدا هستند.

## نتیجه

24 بند متن/عنوان ثبت شد. 9 موضع در 9 بند اصلاح شد. نسخه‌های اصلاح‌شده برای ادغام آماده‌اند. این یک بازبینی محدود است، نه گواهی کامل کتاب.

۴: تطبیق مستقیم و شاهد روشن؛ ۳: شاهد مرتبط همراه محدودیت بافتی؛ ۲: شاهد لفظی اختصاصی کافی نیست؛ ۱: تصمیم حل‌نشده. این امتیاز اطمینان تحریری است، نه احتمال کالیبره‌شده. بازبینی انسانی بعدی امکان اصلاح است، نه شرط ادامه.

## انتخاب‌ها و اصلاح‌های مستند

### FA-INF49-BOOK

عنوان دقیق کتاب منبع حفظ می‌شود؛ نظریهٔ باز نام جاافتادهٔ فارسی این اثر نیست و می‌تواند با مجموعهٔ باز اشتباه شود. جمله و نام نویسنده فارسی می‌مانند.

پیش از اصلاح:
```latex
\emph{نظریهٔ بازِ مجموعه‌ها}
```

پس از اصلاح:
```latex
\emph{Open Set Theory}
```

شواهد: OLP-BOOK-IDENTITY.
گزینه‌های کنارگذاشته‌شده: عنوان فعلی Set Theory: An Open Introduction جای عنوان تاریخی نمی‌نشیند؛ ترجمهٔ حدسی عنوان نیز لازم نیست.
اطمینان تحریری: 4 از ۴.

### FA-INF50-DEFINITION

پسوند نامعین از پایان فرمول و ماکرو برداشته و در ساخت اسمی فارسی بیان می‌شود. ماکرو دقیقاً نگاشت یک‌به‌یک است. سره با شاهد دانشگاهی و اصطلاح بخش زیرمجموعه‌ها یکسان می‌شود؛ حقیقی در این کتاب برای real نیز استفاده شده است. تمام فرمول‌ها و دو سوی هم‌ارزی ثابت‌اند.

پیش از اصلاح:
```latex
مجموعهٔ $A$ \emph{نامتناهیِ ددکیندی} است اگر و تنها اگر !!a{injection}ای
از~$A$ به یک زیرمجموعهٔ حقیقی از~$A$ وجود داشته باشد. یعنی $o \in A$ای
و !!a{injection}ای چون $f \colon A \to A$ وجود دارند چنان‌که
$o \notin \ran{f}$.
```

پس از اصلاح:
```latex
مجموعهٔ $A$ \emph{نامتناهیِ ددکیندی} است اگر و تنها اگر یک !!a{injection}
از~$A$ به یک زیرمجموعهٔ سره از~$A$ وجود داشته باشد. یعنی عضوی چون $o \in A$
و یک !!a{injection} به صورت $f \colon A \to A$ وجود داشته باشند، به‌طوری‌که
$o \notin \ran{f}$.
```

شواهد: I27-PROPER, I46-INJECTION, I53-INFINITE.
گزینه‌های کنارگذاشته‌شده: نگاشت یک‌به‌یک‌ای و o∈Aای پذیرفته نیستند. حقیقی لزوماً در همهٔ کاربردهای فارسی غلط نیست، ولی اینجا سره هم شاهد دارد و هم سازگارتر است.
اطمینان تحریری: 4 از ۴.

### FA-INF50-QUOTE-CREDIT

ما در عبارت اصلی به نویسندهٔ متن مبنا اشاره دارد، نه به بازبین فارسی. انتساب ترجمهٔ نقل‌قول از ادعای ترجمهٔ مستقیم از شاهد آلمانی جدا می‌شود؛ ارجاع و صفحه عوض نمی‌شوند.

پیش از اصلاح:
```latex
؛ ترجمهٔ ما)
```

پس از اصلاح:
```latex
؛ ترجمهٔ نقل‌قول در متن مبنا)
```

شواهد: OLP-BOOK-IDENTITY.
گزینه‌های کنارگذاشته‌شده: حذف عبارت انتساب، یا ادعای مقابلهٔ نقل‌قول با آلمانی بدون دیدن آن، نادرست است.
اطمینان تحریری: 4 از ۴.

### FA-INF51-NATURALS

نامتناهی‌بودن به مجموعهٔ طبیعی‌ها نسبت داده می‌شود، نه بزرگی هر عدد؛ properties و behave well در زمینهٔ اعمال جبری حفظ می‌شوند.

پیش از اصلاح:
```latex
نه‌تنها می‌خواهیم اعداد طبیعی نامتناهی باشند، بلکه می‌خواهیم خواص
(جبریِ) معینی نیز داشته باشند: باید تحت جمع، ضرب و مانند آن به‌خوبی رفتار
کنند.
```

پس از اصلاح:
```latex
نه‌تنها می‌خواهیم مجموعهٔ اعداد طبیعی نامتناهی باشد، بلکه می‌خواهیم اعداد طبیعی
خواص (جبریِ) معینی نیز داشته باشند: جمع، ضرب و مانند آن باید خواص مطلوب را
داشته باشند.
```

شواهد: I45-NATURAL, I53-INFINITE.
گزینه‌های کنارگذاشته‌شده: افزودن نام قوانین خاص که این بند هنوز بیان نکرده است انجام نمی‌شود. عبارت به‌خوبی رفتار کنند لازم نیست تحت‌اللفظی بماند.
اطمینان تحریری: 3 از ۴.

### FA-INF51-ZERO

اصلاح منبع: مجموعهٔ تهی تحت جانشین بسته است؛ بدون شرط دربرداشتن صفر کوچک‌ترین مجموعهٔ بسته تهی می‌شود. تعریف بعدی همان منبع شرط دربرداشتن o را دارد و کانن نیز استقرا را با صفر بیان می‌کند.

پیش از اصلاح:
```latex
\item[3$'$.] اعداد طبیعی کوچک‌ترین مجموعه‌ای هستند که
	\emph{تحت تابع جانشین بسته} است:
```

پس از اصلاح:
```latex
\item[3$'$.] اعداد طبیعی کوچک‌ترین مجموعه‌ای هستند که صفر را در بر دارد و
	\emph{تحت تابع جانشین بسته} است:
```

شواهد: I46-INJECTION, I72-CLOSURE.
گزینه‌های کنارگذاشته‌شده: تنها ناتهی‌بودن برای بازگویی خواستهٔ مشخص متن کافی نیست؛ شرط دقیق دربرداشتن صفر افزوده می‌شود.
اطمینان تحریری: 4 از ۴.

### FA-INF51-CLOSURE-DEFINITION

اصلاح منبع و نحو: دامنه باید تحت تابع بسته باشد و عضو آغازین در آن باشد؛ در غیر این صورت تکرار تابع ممکن است تعریف نشده باشد. شرط X⊆A نیز دامنهٔ تعریف بسته‌بودن را صریح می‌کند. خط تیرهٔ انگلیسی پس از f حذف می‌شود؛ فارسی تحت f بسته است شاهد مستقیم دارد.

پیش از اصلاح:
```latex
برای هر تابع $f$، مجموعهٔ $X$ تحت $f$-
	\emph{بسته} است {اگر و تنها اگر} $(\forall x \in X)f(x) \in X$. اکنون
	برای هر $o$ تعریف کنید:
```

پس از اصلاح:
```latex
برای هر تابع $f \colon A \to A$، مجموعهٔ $X \subseteq A$ تحت $f$
	\emph{بسته} است {اگر و تنها اگر} $(\forall x \in X)f(x) \in X$. اکنون
	برای هر $o \in A$ تعریف می‌کنیم:
```

شواهد: I46-CLOSED, I72-CLOSURE.
گزینه‌های کنارگذاشته‌شده: گسترش تابع به تابعی دلخواه روی جهان همهٔ مجموعه‌ها بدون ثبت فرض مجاز نیست. تبدیل بسته‌بودن به بسته‌بودن تحت رابطه نیز تعریف دیگری می‌سازد.
اطمینان تحریری: 4 از ۴.

### FA-INF51-CLOSURE-LEMMA

اصلاح منبع: A در بیان قبلی لم تعریف نشده بود؛ خودنگاشت بودن هم در ادعای بسته‌بودن برد اجتماع تک‌عضوی لازم است. با این فرض برهان بعدی بدون تغییر برقرار است.

پیش از اصلاح:
```latex
برای هر تابع $f$ و هر $o \in A$:
```

پس از اصلاح:
```latex
برای هر تابع $f \colon A \to A$ و هر $o \in A$:
```

شواهد: I46-INJECTION, I72-CLOSURE.
گزینه‌های کنارگذاشته‌شده: فقط حذف A، یا تغییر فرمول برد بدون تعیین دامنه، مشکل تعریف‌نشدن تکرار را حل نمی‌کند.
اطمینان تحریری: 4 از ۴.

### FA-INF51-INJECTION-PROOF

یک‌به‌یک با ماکرو ثابت همین بخش و زبان کانن یکسان می‌شود؛ تزریقی خطای ریاضی نیست.

پیش از اصلاح:
```latex
تابع تزریقیِ $g
```

پس از اصلاح:
```latex
تابع یک‌به‌یکِ $g
```

شواهد: I46-INJECTION.
گزینه‌های کنارگذاشته‌شده: نگاشت/تابع هر دو در این زمینه مجازند؛ اصطلاح تازه‌ای افزوده نمی‌شود.
اطمینان تحریری: 4 از ۴.

### FA-INF51-INJECTION-RESTRICTION

دو کاربرد باقیمانده در بند تحدید با همان یک‌به‌یک یکسان می‌شوند. دلیل ریاضی، حفظ یکتایی پس از تحدید دامنه است.

پیش از اصلاح:
```latex
دربارهٔ \olref{ded:injection}: تابع $g$ روی $D$ تزریقی است؛ پس
$f \subseteq g$ نیز باید تزریقی باشد.
```

پس از اصلاح:
```latex
دربارهٔ \olref{ded:injection}: تابع $g$ روی $D$ یک‌به‌یک است؛ پس
$f \subseteq g$ نیز باید یک‌به‌یک باشد.
```

شواهد: I46-INJECTION.
گزینه‌های کنارگذاشته‌شده: ترجمهٔ تزریقی غلط نامیده نمی‌شود؛ یکدستی متن و شاهد روشن این انتخاب را توجیه می‌کنند.
اطمینان تحریری: 4 از ۴.

### INF49-NAMES

نامتناهی برای infinite؛ عنوان خاص کتاب به صورت اصلی.

نام حوزه با کانن و نام اثر با اطلاعیهٔ رسمی تطبیق دارد.
مواضع بررسی‌شده: OLP-0049-P04, OLP-0049-P05.
شواهد: I53-INFINITE, OLP-BOOK-IDENTITY.
گزینه‌های بررسی‌شده: بی‌نهایت در نثر توضیحی مجاز است؛ عنوان انگلیسی کتاب عنوان بخش فارسی را جایگزین نمی‌کند.
اطمینان تحریری: 3 از ۴.

### INF50-INFINITY

نامتناهی ددکیندی با صرف نامتناهی یا شمارا یکی نمی‌شود.

صفحهٔ کانن نامتناهی و شمارا را در بافت‌های جدا می‌آورد؛ تعریف اختصاصی از منبع OLP پیروی می‌کند.
مواضع بررسی‌شده: OLP-0050-P03, OLP-0050-P04, OLP-0050-P05, OLP-0050-P06.
شواهد: I45-NATURAL, I53-INFINITE.
گزینه‌های بررسی‌شده: بی‌نهایت اتاق در روایت طبیعی است؛ نامتناهی ددکیندی اصطلاح تعریف است و حذف ددکیندی مجاز نیست.
اطمینان تحریری: 3 از ۴.

### INF50-INJECTION

یک نگاشت یک‌به‌یک و زیرمجموعهٔ سره.

این ترکیب‌ها مستقیماً در نثر دانشگاهی و قالب تعریف متن مبنا پشتیبانی دارند؛ شاهدِ ماکرو به نگاشت یک‌به‌یک بسط می‌یابد.
مواضع بررسی‌شده: OLP-0050-P06.
شواهد: I27-PROPER, I46-INJECTION.
گزینه‌های بررسی‌شده: تزریقی معنا را می‌رساند اما در این تعریف با واژگان ماکرو و کانن یک‌به‌یک یکدست می‌مانیم.
اطمینان تحریری: 4 از ۴.

### INF51-STRUCTURE

ساختار اعداد طبیعی، خواص جبری، صفر و تابع جانشین با معناهای منبع حفظ شوند.

کانن صورت سه‌تایی و شروط پئانو را بیان می‌کند؛ این شاهد برای مفهوم است، نه برای لفظ جبر ددکیند. شکاف لفظی پنهان نمی‌شود.
مواضع بررسی‌شده: OLP-0051-P03, OLP-0051-P04, OLP-0051-P05, OLP-0051-P12, OLP-0051-P13, OLP-0051-P15, OLP-0051-P16.
شواهد: I45-NATURAL, I46-INJECTION.
گزینه‌های بررسی‌شده: حذف جبر یا جایگزینی با حلقه نادرست است؛ اینجا حلقه تعریف نمی‌شود.
اطمینان تحریری: 3 از ۴.

### INF51-CLOSED

تحت f بسته و کوچک‌ترین مجموعهٔ بستهٔ شامل عضو آغازین.

در هر کاربرد، دامنهٔ تابع، عضو آغازین، شمول و جهت استدلال بررسی شده‌اند؛ بسته‌بودن توپولوژیک ادعا نمی‌شود.
مواضع بررسی‌شده: OLP-0051-P05, OLP-0051-P06, OLP-0051-P07, OLP-0051-P08, OLP-0051-P09, OLP-0051-P10, OLP-0051-P11, OLP-0051-P13, OLP-0051-P14, OLP-0051-P16, OLP-0051-P19.
شواهد: I46-CLOSED, I72-CLOSURE.
گزینه‌های بررسی‌شده: f-بسته با خط تیره ساختی انگلیسی است؛ پوشش یا بستار توپولوژیک بدون زمینه انتخاب نمی‌شود.
اطمینان تحریری: 4 از ۴.

### INF51-INJECTIVE

یک‌به‌یک، با ثبات کمیت‌گذارها و مفهوم برد.

قضیهٔ ۳۶ کانن همین شرط و صفر خارج از برد را دارد. تمام مواضع این بخش در بافت خود مقایسه شده‌اند.
مواضع بررسی‌شده: OLP-0051-P05, OLP-0051-P13, OLP-0051-P14, OLP-0051-P16, OLP-0051-P17, OLP-0051-P18.
شواهد: I46-INJECTION.
گزینه‌های بررسی‌شده: تزریقی غلط ریاضی نیست ولی در این قطعه یکدست می‌شود؛ یک‌به‌یک با دوسویی یا پوشا جایگزین نمی‌شود.
اطمینان تحریری: 4 از ۴.

## بندهای هم‌تراز برای بازبینی انسانی

متن هر دو طرف، بازهٔ دقیق بایت، شمارهٔ خط و هش در INFINITE_0049_0051.public.json موجود است. تکرارهای یک انتخاب در بافت بند خود بررسی شده‌اند؛ این ثبت جای ادعای بی‌پشتوانهٔ تأیید تک‌تک واژه‌ها را نمی‌گیرد.

### محل ادغام اصلاح‌ها: OLP-0049

متن پیشنهادی از قطعهٔ مؤثر خواننده ساخته شده است؛ وصله را نباید مستقیماً بر شاهد بومیِ قدیمی اعمال کرد. شناسه و هش قطعه و متن دقیق پیش و پس از هر اصلاح در دفتر آمده‌اند. شاهد تثبیت‌شده و اصلاح‌های پیشین باید حفظ شوند.

### محل ادغام اصلاح‌ها: OLP-0050

متن پیشنهادی از قطعهٔ مؤثر خواننده ساخته شده است؛ وصله را نباید مستقیماً بر شاهد بومیِ قدیمی اعمال کرد. شناسه و هش قطعه و متن دقیق پیش و پس از هر اصلاح در دفتر آمده‌اند. شاهد تثبیت‌شده و اصلاح‌های پیشین باید حفظ شوند.

### محل ادغام اصلاح‌ها: OLP-0051

متن پیشنهادی از قطعهٔ مؤثر خواننده ساخته شده است؛ وصله را نباید مستقیماً بر شاهد بومیِ قدیمی اعمال کرد. شناسه و هش قطعه و متن دقیق پیش و پس از هر اصلاح در دفتر آمده‌اند. شاهد تثبیت‌شده و اصلاح‌های پیشین باید حفظ شوند.

### تفاوت مستند با فرمول منبع: OLP-0051

اصلاح محدود منبع؛ شاهد اصلی دست‌نخورده است
مجموعهٔ تهی بسته است. این تغییر، شرط حذف‌شده را بازیابی می‌کند و تعریف بعدی را عوض نمی‌کند.
منبع تثبیت‌شده: `The natural numbers are the smallest set that is

	\emph{closed under the successor function}`؛ صورت بررسی‌شده برای تطبیق: `The natural numbers are the smallest set containing zero that is

	\emph{closed under the successor function}`. متن منبع دست‌نخورده نگه داشته شده است؛ جدول پیش و پس از اصلاح، تفاوت خوانندهٔ جاری و پیشنهاد را مشخص می‌کند.

### تفاوت مستند با فرمول منبع: OLP-0051

اصلاح محدود منبع؛ شاهد اصلی دست‌نخورده است
تعریف پیشین تابع در همین کتاب، دامنه و هم‌دامنهٔ دلخواه را مجاز می‌داند. برای تکرار و برهان وجود، خودنگاشت بر A با زیرمجموعه‌های A کافی است.
منبع تثبیت‌شده: `For any function $f$, the set $X$ is $f$-\emph{closed}`؛ صورت بررسی‌شده برای تطبیق: `For any function $f \colon A \to A$, the set $X \subseteq A$ is $f$-\emph{closed}`. متن منبع دست‌نخورده نگه داشته شده است؛ جدول پیش و پس از اصلاح، تفاوت خوانندهٔ جاری و پیشنهاد را مشخص می‌کند.

### تفاوت مستند با فرمول منبع: OLP-0051

اصلاح محدود منبع؛ شاهد اصلی دست‌نخورده است
عضو آغازین باید در دامنهٔ بستهٔ تابع باشد؛ وگرنه حتی نخستین تصویر ممکن است تعریف نشود.
منبع تثبیت‌شده: `Now define, for any $o$:`؛ صورت بررسی‌شده برای تطبیق: `Now define, for any $o \in A$:`. متن منبع دست‌نخورده نگه داشته شده است؛ جدول پیش و پس از اصلاح، تفاوت خوانندهٔ جاری و پیشنهاد را مشخص می‌کند.

### تفاوت مستند با فرمول منبع: OLP-0051

اصلاح محدود منبع؛ شاهد اصلی دست‌نخورده است
فرض خودنگاشت، دامنهٔ A و استفاده از o∈A را هم‌زمان موجه می‌کند؛ نمونهٔ f:{0}→{1} با f(0)=1 فرض حذف‌شده را آشکار می‌کند.
منبع تثبیت‌شده: `For any function $f$ and any $o \in A$:`؛ صورت بررسی‌شده برای تطبیق: `For any function $f \colon A \to A$ and any $o \in A$:`. متن منبع دست‌نخورده نگه داشته شده است؛ جدول پیش و پس از اصلاح، تفاوت خوانندهٔ جاری و پیشنهاد را مشخص می‌کند.

### OLP-0049-P04

عنوان مجموعه‌های نامتناهی با نامتناهی در کانن سازگار است؛ نه همهٔ مجموعه‌های نامتناهی را شمارا می‌نامد و نه قید ددکیندی را پیشاپیش به عنوان می‌افزاید.
شواهد: I53-INFINITE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olchapter{sfr}{infinite}{Infinite Sets}
```

ترجمهٔ فارسی:
```latex
\olchapter{sfr}{infinite}{مجموعه‌های نامتناهی}
```

</details>

### OLP-0049-P05

انتساب فصل، نویسنده و موضوع حفظ می‌شوند؛ فقط عنوان قابل بازیابی کتاب اصلاح شد. این شاهد هویت است، نه شاهد دستور زبان فارسی.
شواهد: I53-INFINITE, OLP-BOOK-IDENTITY.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{editorial}

This chapter on infinite sets is taken from Tim Button's \emph{Open

Set Theory}.

\end{editorial}
```

ترجمهٔ فارسی:
```latex
\begin{editorial}
این فصل دربارهٔ مجموعه‌های نامتناهی از متن \emph{Open Set Theory}
نوشتهٔ تیم باتن گرفته شده است.
\end{editorial}
```

</details>

### OLP-0049-P06

پنج ورودی ۰۰۵۰ تا ۰۰۵۴ و ترتیب آن‌ها حفظ و با نشانگرهای واقعی خواننده تطبیق می‌شوند؛ بررسی بدنهٔ سه بخش پایانی در این نوبت ادعا نمی‌شود.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olimport{hilberts-hotel}

\olimport{dedekind-algebra}

\olimport{dedekind-induction}

\olimport{dedekinds-proof}

\olimport{card-sb}
```

ترجمهٔ فارسی:
```latex
\olimport{hilberts-hotel}
\olimport{dedekind-algebra}
\olimport{dedekind-induction}
\olimport{dedekinds-proof}
\olimport{card-sb}
```

</details>

### OLP-0050-P03

عنوان هتل هیلبرت و شناسهٔ بخش حفظ می‌شوند؛ نام خاص است، نه اصطلاحی که از صفحهٔ کانن استنتاج شده باشد.
شواهد: I53-INFINITE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: در صفحات خوانده‌شده شاهد اختصاصی برای املای هتل هیلبرت نیست؛ صورت موجود تغییر حدسی نمی‌کند.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olfileid{sfr}{infinite}{hilbert}

\olsection{Hilbert's Hotel}
```

ترجمهٔ فارسی:
```latex
\olfileid[fa-IR]{sfr}{infinite}{hilbert}
\olsection{هتل هیلبرت}
```

</details>

### OLP-0050-P04

مفروض‌گرفتن طبیعی‌ها ترجمهٔ معنایی help ourselves است. همهٔ قیود نقل‌قول متناهی حفظ‌اند: دقیقاً یک مهمان در ابتدا، حداکثر یک مهمان پس از جابه‌جایی و آزاد نشدن اتاق. لحن رسمی موجود فهم‌پذیر است و کوتاه نمی‌شود.
شواهد: I45-NATURAL, I53-INFINITE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: سال ۱۹۲۴ از منبع حفظ شده است؛ شاهد تاریخی اولیه در این نوبت مقابله نشد.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
The set of the natural numbers is obviously infinite. So, if we do not

want to \emph{help ourselves} to the natural numbers, our first step

must be characterize an infinite set in terms that do not require

mentioning the natural numbers themselves. Here is a nice approach,

presented by Hilbert in a lecture from 1924. He asks us to imagine

\begin{quote}

[\ldots] a hotel with a finite number of rooms. All of these rooms

should be occupied by exactly one guest. If the guests now swap their

rooms somehow, [but] so that each room still contains no more than one

person, then no rooms will become free, and the hotel-owner cannot in

this way create a new place for a newly arriving guest [\ldots

\textparagraph \ldots]
```

ترجمهٔ فارسی:
```latex
مجموعهٔ اعداد طبیعی آشکارا نامتناهی است. بنابراین، اگر نخواهیم اعداد طبیعی
را \emph{مفروض بگیریم}، نخستین گام ما باید توصیف مجموعهٔ نامتناهی با
عبارت‌هایی باشد که نیازی به ذکر خودِ اعداد طبیعی ندارند. اینک رویکردی
دل‌انگیز که هیلبرت در سخنرانی‌ای در سال 1924 عرضه کرد. او از ما می‌خواهد
تصور کنیم
\begin{quote}
[\ldots] هتلی با تعداد متناهی اتاق. هر یک از این اتاق‌ها باید دقیقاً با
یک مهمان اشغال شده باشد. اگر مهمانان اکنون به نحوی اتاق‌هایشان را با هم
عوض کنند، [اما] به‌گونه‌ای که هر اتاق همچنان بیش از یک نفر را در خود جای
ندهد، آنگاه هیچ اتاقی آزاد نخواهد شد و صاحب هتل نمی‌تواند بدین شیوه جایی
تازه برای مهمانی که تازه از راه می‌رسد ایجاد کند [\ldots
\textparagraph \ldots]
```

</details>

### OLP-0050-P05

شمارهٔ اتاق‌ها، حرکت یک واحدی، اتاق خالی ۱، همهٔ پیکان‌های شکل، ارجاع صفحهٔ ۷۳۰ و تقدم زمانی ددکیند حفظ‌اند. زمان‌پریشی به ترتیب روایت اشاره می‌کند. انتساب ترجمهٔ نقل‌قول روشن شد.
شواهد: I46-INJECTION, I53-INFINITE, OLP-BOOK-IDENTITY.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: برای زمان‌پریشی و نامتناهی ددکیندی شاهد لفظی مستقیم در صفحات کانن نداریم؛ معنای آن‌ها با همین منبع تطبیق شد.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Now we stipulate that the hotel shall have infinitely many numbered

rooms $1$, $2$, $3$, $4$, $5$, \dots, each of which is occupied by

exactly one guest. As soon as a new guest comes along, the owner only

needs to move each of the old guests into the room associated with the

number one higher, and room~$1$ will be free for the newly-arriving

guest. 

	\begin{center}

		\begin{tikzpicture}[scale = .75]

		\foreach \x in {1, 2, 3, 4, 5, 6, 7, 8, 9}

		{

			\node (\x a) at (\x, 1) {\small{\x}};

			\node (\x b) at (\x, 2) {\small{\x}};

		}

		\node (dotsa) at (10, 1) {\small{\ldots}};

		\node (dotsb) at (10, 2) {\small{\ldots}};

		\draw[->] (1b)--(2a);

		\draw[->] (2b)--(3a);

		\draw[->] (3b)--(4a);

		\draw[->] (4b)--(5a);

		\draw[->] (5b)--(6a);

		\draw[->] (6b)--(7a);

		\draw[->] (7b)--(8a);

		\draw[->] (8b)--(9a);

		\draw[->] (9b)--(dotsa);

		\draw (1,1) circle (.4);

		\end{tikzpicture}

	\end{center}

	(published in \citealt[730]{EwaldSieg2013}; our translation)

\end{quote}

The crucial point is that Hilbert's Hotel has infinitely many rooms;

and we can take his explanation to define what it means to say this.

Indeed, this was Dedekind's approach (presented here, of course, with

massive anachronism; Dedekind's definition is from

\citeyear{Dedekind1888}):
```

ترجمهٔ فارسی:
```latex
اکنون مقرر می‌کنیم که هتل بی‌نهایت اتاقِ شماره‌دارِ $1$، $2$، $3$، $4$،
$5$، \dots داشته باشد و هر یک دقیقاً با یک مهمان اشغال شده باشد. همین که
مهمانی تازه از راه برسد، صاحب هتل فقط باید هر یک از مهمانان قدیمی را به
اتاقی منتقل کند که شماره‌اش یک واحد بیشتر است؛ آنگاه اتاق~$1$ برای مهمان
تازه‌وارد آزاد خواهد شد.
	\begin{center}
		\begin{tikzpicture}[scale = .75]
		\foreach \x in {1, 2, 3, 4, 5, 6, 7, 8, 9}
		{
			\node (\x a) at (\x, 1) {\small{\x}};
			\node (\x b) at (\x, 2) {\small{\x}};
		}
		\node (dotsa) at (10, 1) {\small{\ldots}};
		\node (dotsb) at (10, 2) {\small{\ldots}};
		\draw[->] (1b)--(2a);
		\draw[->] (2b)--(3a);
		\draw[->] (3b)--(4a);
		\draw[->] (4b)--(5a);
		\draw[->] (5b)--(6a);
		\draw[->] (6b)--(7a);
		\draw[->] (7b)--(8a);
		\draw[->] (8b)--(9a);
		\draw[->] (9b)--(dotsa);
		\draw (1,1) circle (.4);
		\end{tikzpicture}
	\end{center}
	(منتشرشده در \citealt[730]{EwaldSieg2013}؛ ترجمهٔ نقل‌قول در متن مبنا)
\end{quote}
نکتهٔ اساسی این است که هتل هیلبرت بی‌نهایت اتاق دارد؛ و می‌توانیم توضیح
او را تعریفی برای معنای این گفته بدانیم. در واقع، رویکرد ددکیند نیز همین
بود (که البته اینجا با زمان‌پریشیِ شدیدی عرضه می‌شود؛ تعریف ددکیند از
\citeyear{Dedekind1888} است):
```

</details>

### OLP-0050-P06

شرط لازم و کافی، زیرمجموعهٔ سره، عضو خارج از برد و یک‌به‌یکی همگی حفظ شدند؛ عبارت فارسی بدون چسباندن پسوند به فرمول بازسازی شد.
شواهد: I27-PROPER, I46-INJECTION, I53-INFINITE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: صفت ددکیندی در کانن این نوبت شاهد مستقیم ندارد؛ تعریف دقیق جایگزین ادعای رواج اصطلاح نمی‌شود.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{defn}\ollabel{defn:DedekindInfinite}

A set $A$ is \emph{Dedekind infinite} iff there is !!a{injection}

from~$A$ to a proper subset of~$A$. That is, there is some $o \in A$

and !!a{injection} $f \colon A \to A$ such that $o \notin \ran{f}$.

\end{defn}
```

ترجمهٔ فارسی:
```latex
\begin{defn}\ollabel{defn:DedekindInfinite}
مجموعهٔ $A$ \emph{نامتناهیِ ددکیندی} است اگر و تنها اگر یک !!a{injection}
از~$A$ به یک زیرمجموعهٔ سره از~$A$ وجود داشته باشد. یعنی عضوی چون $o \in A$
و یک !!a{injection} به صورت $f \colon A \to A$ وجود داشته باشند، به‌طوری‌که
$o \notin \ran{f}$.
\end{defn}
```

</details>

### OLP-0051-P03

نام جبرهای ددکیند و شناسهٔ بخش حفظ‌اند؛ ساختار سه‌تایی در خود منبع تعریف می‌شود.
شواهد: I45-NATURAL, I46-INJECTION.
اطمینان تحریری: 2 از ۴.
نیازمند بررسی: برای خود اصطلاح جبر ددکیند شاهد لفظی اختصاصی در صفحات حاضر نیست.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olfileid{sfr}{infinite}{dedekind}

\olsection{Dedekind Algebras}
```

ترجمهٔ فارسی:
```latex
\olfileid[fa-IR]{sfr}{infinite}{dedekind}
\olsection{جبرهای ددکیند}
```

</details>

### OLP-0051-P04

مجموعهٔ طبیعی‌ها نامتناهی است، نه تک‌تک اعداد. خواص جبری اعمال همان خواستهٔ منبع‌اند و قانون جدیدی اضافه نشده است.
شواهد: I45-NATURAL, I53-INFINITE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
We not only want natural numbers to be infinite; we want them to have

certain (algebraic) properties: they need to behave well under

addition, multiplication, and so forth. 
```

ترجمهٔ فارسی:
```latex
نه‌تنها می‌خواهیم مجموعهٔ اعداد طبیعی نامتناهی باشد، بلکه می‌خواهیم اعداد طبیعی
خواص (جبریِ) معینی نیز داشته باشند: جمع، ضرب و مانند آن باید خواص مطلوب را
داشته باشند.
```

</details>

### OLP-0051-P05

صفر خارج از برد، یک‌به‌یکی، تکرار جانشین و محدودیت منطق مرتبهٔ اول حفظ‌اند. بند ۳′ اکنون صریحاً صفر را در بر دارد؛ این تصحیحِ منبع است، نه بهبود اختیاری. ارجاع‌های repeatedapplication و همهٔ فرمول‌های اصلی باقی‌اند.
شواهد: I45-NATURAL, I46-INJECTION, I72-CLOSURE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: لفظ تابع جانشین شاهد مستقیم در صفحات حاضر ندارد؛ تعریف و صورت s(x)=x+1 در کانن مقایسه شد.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Dedekind's idea was to take the idea of the \emph{successor function}

as basic, and then characterise the numbers as those with the

following properties:

\begin{enumerate}

	\item There is a number, $0$, which is not the successor of any number

	\\i.e., $0 \notin \ran{s}$

	\\i.e., $\forall x\ s(x) \neq 0$

	\item Distinct numbers have distinct successors 

	\\i.e., $s$ is !!a{injection}

	\\i.e., $\forall x \forall y (s(x) = s(y) \lif x = y)$

	\item\ollabel{repeatedapplication} Every number is obtained from

	$0$ by repeated applications of the successor function.

\end{enumerate}

The first two conditions are easy to deal with using first-order logic

(see above). But we cannot deal with \olref{repeatedapplication} just

using first-order logic. Dedekind's breakthrough was to reformulate

condition \olref{repeatedapplication}, set-theoretically, as follows:

\begin{enumerate}

	\item[3$'$.] The natural numbers are the smallest set that is

	\emph{closed under the successor function}: that is, if we apply

	$s$ to any !!{element} of the set, we obtain another !!{element}

	of the set.

\end{enumerate}

But we shall need to spell this out slowly.
```

ترجمهٔ فارسی:
```latex
اندیشهٔ ددکیند این بود که مفهوم \emph{تابع جانشین} را بنیادی بگیریم و
سپس اعداد را همچون اشیایی با خواص زیر مشخص کنیم:
\begin{enumerate}
	\item عددی چون $0$ وجود دارد که جانشین هیچ عددی نیست
	\\یعنی، $0 \notin \ran{s}$
	\\یعنی، $\forall x\ s(x) \neq 0$
	\item اعداد متمایز جانشین‌های متمایز دارند
	\\یعنی، $s$ یک !!a{injection} است
	\\یعنی، $\forall x \forall y (s(x) = s(y) \lif x = y)$
	\item\ollabel{repeatedapplication} هر عدد با اعمال مکررِ تابع جانشین
	بر $0$ به دست می‌آید.
\end{enumerate}
رسیدگی به دو شرط نخست با منطق مرتبهٔ اول آسان است (بنگرید به بالا). اما
نمی‌توانیم تنها با منطق مرتبهٔ اول به \olref{repeatedapplication} رسیدگی
کنیم. پیشرفت تعیین‌کنندهٔ ددکیند این بود که شرط
\olref{repeatedapplication} را به‌صورت مجموعه‌شناختیِ زیر بازنویسی کرد:
\begin{enumerate}
	\item[3$'$.] اعداد طبیعی کوچک‌ترین مجموعه‌ای هستند که صفر را در بر دارد و
	\emph{تحت تابع جانشین بسته} است: یعنی اگر $s$ را بر هر !!{element}
	از مجموعه اعمال کنیم، !!{element} دیگری از مجموعه به دست می‌آوریم.
\end{enumerate}
اما باید این مطلب را به‌آرامی و با جزئیات بیان کنیم.
```

</details>

### OLP-0051-P06

تعریف بسته‌بودن و اشتراک حفظ‌اند، با فرض‌های صریح خودنگاشت، زیرمجموعهٔ دامنه و عضو آغازین. این افزوده‌ها در جدول اختلاف فرمول ثبت شده‌اند؛ ادعای یکسانی لفظی با منبع نداریم.
شواهد: I46-CLOSED, I72-CLOSURE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{defn}\ollabel{Closure}

	For any function $f$, the set $X$ is $f$-\emph{closed} {iff}

	$(\forall x \in X)f(x) \in X$. Now define, for any $o$:

	$$\closureofunder{f}{o} = \bigcap\Setabs{X}{o \in X\text{ and }X

\text{ is $f$-closed}}$$

\end{defn}
```

ترجمهٔ فارسی:
```latex
\begin{defn}\ollabel{Closure}
	برای هر تابع $f \colon A \to A$، مجموعهٔ $X \subseteq A$ تحت $f$
	\emph{بسته} است {اگر و تنها اگر} $(\forall x \in X)f(x) \in X$. اکنون
	برای هر $o \in A$ تعریف می‌کنیم:
	$$\closureofunder{f}{o} = \bigcap\Setabs{X}{o \in X\text{ و }X
\text{ تحت $f$ بسته است}}$$
\end{defn}
```

</details>

### OLP-0051-P07

کوچک‌ترین یعنی در ترتیب شمول؛ سه خاصیت و ترتیب آن‌ها ثابت‌اند. دامنهٔ A و فرض خودنگاشت در بیان لم صریح می‌شوند.
شواهد: I46-CLOSED, I72-CLOSURE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
So $\closureofunder{f}{o}$ is the intersection of all the $f$-closed

sets with $o$ as !!a{element}. Intuitively, then,

$\closureofunder{f}{o}$ is the \emph{smallest} $f$-closed set with $o$

as !!a{element}. This next result makes that intuitive thought

precise;

\begin{lem}\ollabel{closureproperties}

	For any function $f$ and any $o \in A$:

	\begin{enumerate}

		\item\ollabel{closurehaselem} $o \in \closureofunder{f}{o}$; and

		\item\ollabel{closureclosed} $\closureofunder{f}{o}$ is $f$-closed; and

		\item\ollabel{closuresmallest} if $X$ is $f$-closed and $o \in

		X$, then $\closureofunder{f}{o} \subseteq X$

	\end{enumerate}

\end{lem}
```

ترجمهٔ فارسی:
```latex
پس $\closureofunder{f}{o}$ اشتراک همهٔ مجموعه‌های بسته تحت $f$ است که
$o$ را به‌عنوان !!a{element} دارند. بنابراین، به‌طور شهودی،
$\closureofunder{f}{o}$ \emph{کوچک‌ترین} مجموعهٔ بسته تحت $f$ است که
$o$ را به‌عنوان !!a{element} دارد. نتیجهٔ بعدی این اندیشهٔ شهودی را
دقیق می‌کند؛
\begin{lem}\ollabel{closureproperties}
	برای هر تابع $f \colon A \to A$ و هر $o \in A$:
	\begin{enumerate}
		\item\ollabel{closurehaselem} $o \in \closureofunder{f}{o}$؛ و
		\item\ollabel{closureclosed} $\closureofunder{f}{o}$ تحت $f$ بسته است؛ و
		\item\ollabel{closuresmallest} اگر $X$ تحت $f$ بسته باشد و $o \in
		X$، آنگاه $\closureofunder{f}{o} \subseteq X$
	\end{enumerate}
\end{lem}
```

</details>

### OLP-0051-P08

تحت فرض اصلاح‌شده، برد f اجتماع {o} زیرمجموعهٔ A و بسته است: تصویر هر عضو آن در برد f است. این شاهد ناتهی بودن خانوادهٔ مورد اشتراک است؛ نه اصل جدیدی از منبع فارسی.
شواهد: I72-CLOSURE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}

Note that there is at least one $f$-closed set with $o$ as !!a{element}, namely $\ran{f}\cup

\{o\}$. So $\closureofunder{f}{o}$, the intersection of \emph{all}

such sets, exists. We must now check

\olref{closurehaselem}--\olref{closuresmallest}.
```

ترجمهٔ فارسی:
```latex
\begin{proof}
توجه کنید که دست‌کم یک مجموعهٔ بسته تحت $f$ وجود دارد که $o$ را به‌عنوان
!!a{element} دارد، یعنی $\ran{f}\cup \{o\}$. پس
$\closureofunder{f}{o}$، یعنی اشتراک \emph{همهٔ} چنین مجموعه‌هایی، وجود
دارد. اکنون باید \olref{closurehaselem}--\olref{closuresmallest} را
بررسی کنیم.
```

</details>

### OLP-0051-P09

همگی و اشتراک، کمیت‌گذاری متن را حفظ می‌کنند: چون هر مجموعهٔ خانواده o را دارد، اشتراک نیز دارد.
شواهد: I72-CLOSURE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Concerning \olref{closurehaselem}: $o \in \closureofunder{f}{o}$ as it is an

intersection of sets which all have $o$ as !!a{element}. 
```

ترجمهٔ فارسی:
```latex
دربارهٔ \olref{closurehaselem}: داریم $o \in \closureofunder{f}{o}$،
زیرا این مجموعه اشتراک مجموعه‌هایی است که همگی $o$ را به‌عنوان
!!a{element} دارند.
```

</details>

### OLP-0051-P10

فرض عضویت x در همهٔ مجموعه‌های خانواده و بسته‌بودن هرکدام به عضویت f(x) در همهٔ آن‌ها می‌انجامد؛ هیچ تعویض سور یا نتیجهٔ قوی‌تری نیست.
شواهد: I46-CLOSED, I72-CLOSURE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Concerning \olref{closureclosed}: suppose $x \in \closureofunder{f}{o}$. So if $o \in X$ and $X$ is $f$-closed, then $x \in X$, and now $f(x) \in X$ as $X$ is

$f$-closed. So $f(x) \in \closureofunder{f}{o}$.
```

ترجمهٔ فارسی:
```latex
دربارهٔ \olref{closureclosed}: فرض کنید $x \in
\closureofunder{f}{o}$. پس اگر $o \in X$ و $X$ تحت $f$ بسته باشد، آنگاه
$x \in X$، و اکنون $f(x) \in X$، زیرا $X$ تحت $f$ بسته است. بنابراین
$f(x) \in \closureofunder{f}{o}$.
```

</details>

### OLP-0051-P11

عضویت X در خانوادهٔ C با زیرمجموعه بودن اشتراک در X اشتباه نشده است؛ شمول غیرسره باقی می‌ماند.
شواهد: I27-PROPER, I72-CLOSURE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Concerning \olref{closuresmallest}: quite generally, if $X

\in C$ then $\bigcap C \subseteq X$.

\end{proof}
```

ترجمهٔ فارسی:
```latex
دربارهٔ \olref{closuresmallest}: به‌طور کلی، اگر $X \in C$، آنگاه
$\bigcap C \subseteq X$.
\end{proof}
```

</details>

### OLP-0051-P12

جملهٔ گذار کوتاه و هم‌معنای متن مبنا حفظ می‌شود؛ اصطلاح تخصصی تازه ندارد.
شواهد: I45-NATURAL.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Using this, we can say:
```

ترجمهٔ فارسی:
```latex
با استفاده از این نتیجه می‌توانیم بگوییم:
```

</details>

### OLP-0051-P13

سه جزء A,f,o و سه شرط مستقل حفظ‌اند. یک‌به‌یکی با کانن و بسط ماکرو تطبیق دارد؛ جبر به معنای ساختار است نه درس جبر.
شواهد: I46-INJECTION, I72-CLOSURE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: نام خاص جبر ددکیند در صفحات حاضر شاهد مستقیم ندارد؛ موقتاً بر اساس تعریف منبع حفظ می‌شود.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{defn}

A \emph{Dedekind algebra} is a set $A$ together with a function $f

\colon A \to A$ and some $o \in A$  such that:

	\begin{enumerate}

		\item \ollabel{ded:proper} $o \notin \ran{f}$

		\item \ollabel{ded:injection} $f$ is !!a{injection}

		\item \ollabel{ded:closure} $A = \closureofunder{f}{o}$

	\end{enumerate}

\end{defn}
```

ترجمهٔ فارسی:
```latex
\begin{defn}
یک \emph{جبر ددکیند} مجموعه‌ای چون $A$ همراه با تابعی چون $f
\colon A \to A$ و عضوی چون $o \in A$ است، چنان‌که:
	\begin{enumerate}
		\item \ollabel{ded:proper} $o \notin \ran{f}$
		\item \ollabel{ded:injection} $f$ یک !!a{injection} است
		\item \ollabel{ded:closure} $A = \closureofunder{f}{o}$
	\end{enumerate}
\end{defn}
```

</details>

### OLP-0051-P14

نتیجهٔ کوچک‌ترین‌بودن و استناد به دو شرط اول حفظ‌اند. جملهٔ تبدیل مجموعهٔ نامتناهی به جبر در پرتو قضیه و برهان بعدی خوانده می‌شود.
شواهد: I46-INJECTION, I72-CLOSURE.
اطمینان تحریری: 2 از ۴.
نیازمند بررسی: عبارت تبدیل هر مجموعه به جبر ممکن است حفظ تمام حامل را القا کند؛ برهان فقط ساخت روی زیرمجموعه را ثابت می‌کند. این ابهام جداگانه برای بررسی ثبت شده و بدون داوری قطعی بازنویسی نشده است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Since $A = \closureofunder{f}{o}$, our earlier result tells us that

$A$ is the smallest $f$-closed set with $o$ as !!a{element}. Clearly a

Dedekind algebra is Dedekind infinite; just look at clauses

\olref{ded:proper} and \olref{ded:injection} of the definition. But

the more exciting fact is that any Dedekind infinite set can be turned

into a Dedekind algebra. 
```

ترجمهٔ فارسی:
```latex
چون $A = \closureofunder{f}{o}$، نتیجهٔ پیشین به ما می‌گوید $A$
کوچک‌ترین مجموعهٔ بسته تحت $f$ است که $o$ را به‌عنوان !!a{element}
دارد. یک جبر ددکیند آشکارا نامتناهیِ ددکیندی است؛ کافی است به بندهای
\olref{ded:proper} و \olref{ded:injection} تعریف بنگرید. اما واقعیت
هیجان‌انگیزتر این است که هر مجموعهٔ نامتناهیِ ددکیندی را می‌توان به یک
جبر ددکیند تبدیل کرد.
```

</details>

### OLP-0051-P15

قضیه صرفاً از وجود مجموعهٔ نامتناهی ددکیندی وجود جبر را نتیجه می‌گیرد؛ نمی‌گوید هر حامل دلخواه خود یک جبر با این شروط است.
شواهد: I46-INJECTION, I53-INFINITE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{thm}\ollabel{thm:DedekindInfiniteAlgebra}

If there is a Dedekind infinite set, then there is a Dedekind algebra.

\end{thm}
```

ترجمهٔ فارسی:
```latex
\begin{thm}\ollabel{thm:DedekindInfiniteAlgebra}
اگر مجموعه‌ای نامتناهیِ ددکیندی وجود داشته باشد، آنگاه یک جبر ددکیند وجود
دارد.
\end{thm}
```

</details>

### OLP-0051-P16

وجود g و o، تعریف A به بسته‌سازی و تحدید g به A حفظ‌اند. بسته بودن A در لم، نوع f:A→A را تضمین می‌کند؛ واژهٔ یک‌به‌یک یکسان شده است.
شواهد: I46-INJECTION, I72-CLOSURE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}

Let $D$ be Dedekind infinite. So there is an injection $g \colon D \to

D$ and an element $o  \in D \setminus \ran{g}$. Now let $A =

\closureofunder{g}{o}$; by \olref{closureproperties}, $A$ exists and $o \in A$. Let $f =

\funrestrictionto{g}{A}$. We will show that $A, f, o$ comprise a Dedekind

algebra. 
```

ترجمهٔ فارسی:
```latex
\begin{proof}
فرض کنید $D$ نامتناهیِ ددکیندی باشد. پس تابع یک‌به‌یکِ $g \colon D \to
D$ و عضوی چون $o  \in D \setminus \ran{g}$ وجود دارند. اکنون بگذارید
$A = \closureofunder{g}{o}$؛ بنا بر \olref{closureproperties}، $A$ وجود
دارد و $o \in A$. بگذارید $f = \funrestrictionto{g}{A}$. نشان خواهیم
داد که $A, f, o$ یک جبر ددکیند را تشکیل می‌دهند.
```

</details>

### OLP-0051-P17

خارج‌بودن o از برد g و شمول برد f در برد g دقیقاً همان نتیجهٔ خارج‌بودن از برد f را می‌دهند.
شواهد: I46-INJECTION.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Concerning \olref{ded:proper}: $o \notin \ran{g}$ and $\ran{f}

\subseteq \ran{g}$ so $o\notin \ran{f}$.
```

ترجمهٔ فارسی:
```latex
دربارهٔ \olref{ded:proper}: داریم $o \notin \ran{g}$ و $\ran{f}
\subseteq \ran{g}$، پس $o\notin \ran{f}$.
```

</details>

### OLP-0051-P18

تحدید یک تابع یک‌به‌یک همچنان یک‌به‌یک است. دو مورد تزریقی با یک‌به‌یک یکسان شده‌اند؛ رابطهٔ f⊆g دست‌نخورده است.
شواهد: I46-INJECTION.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Concerning \olref{ded:injection}: $g$ is an injection on $D$; so $f

\subseteq g$ must be an injection.
```

ترجمهٔ فارسی:
```latex
دربارهٔ \olref{ded:injection}: تابع $g$ روی $D$ یک‌به‌یک است؛ پس
$f \subseteq g$ نیز باید یک‌به‌یک باشد.
```

</details>

### OLP-0051-P19

هر دو شمول برای برابری A و بسته‌سازیِ f حفظ‌اند. انتقال از f-بسته به g-بسته به قرار داشتن مجموعه در A و برابری f و g روی A متکی است؛ این زمینه در بندهای قبلی حاضر است.
شواهد: I46-CLOSED, I72-CLOSURE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Concerning \olref{ded:closure}: by \olref{closureproperties}, $A$ is $g$-closed; a fortiori, $A$ is $f$-closed. So $\closureofunder{f}{o} \subseteq A$ by \olref{closureproperties}. Since also $\closureofunder{f}{o}$ is $f$-closed and $f = \funrestrictionto{g}{A}$, it follows that $\closureofunder{f}{o}$ is $g$-closed. So $A \subseteq \closureofunder{f}{o}$ by \olref{closureproperties}.

\end{proof}
```

ترجمهٔ فارسی:
```latex
دربارهٔ \olref{ded:closure}: بنا بر \olref{closureproperties}، $A$ تحت
$g$ بسته است؛ پس به طریق اولی، $A$ تحت $f$ بسته است. بنابراین
$\closureofunder{f}{o} \subseteq A$، بنا بر \olref{closureproperties}. از سوی
دیگر، چون $\closureofunder{f}{o}$ نیز تحت $f$ بسته است و $f =
\funrestrictionto{g}{A}$، نتیجه می‌شود $\closureofunder{f}{o}$ تحت $g$
بسته است. پس $A \subseteq \closureofunder{f}{o}$، بنا بر
\olref{closureproperties}.
\end{proof}
```

</details>

## یافته‌های تکمیلی و حدود بازبینی

سه واحد و همهٔ بندهای فعال آن‌ها بررسی شدند. اصطلاح‌های نامتناهی، یک‌به‌یک، سره و بسته تحت تابع با صفحات واقعاً خوانده‌شده پیوند دارند. لفظ جبر ددکیند و تابع جانشین هنوز شاهد لفظی اختصاصی کافی ندارند؛ تعریف و کاربردشان با منبع تطبیق شد و این خلأ برای بازبینی بعدی آشکار است. دو گروه تصحیح منبع: شرط صفر در کمینگی، و فرض‌های دامنهٔ بسته و عضو آغازین در بسته‌سازی. عبارت تبدیل کل حامل تنها به‌عنوان ابهام ثبت شده، نه اصلاح اجراشده. ۸۴ اصلاح منتشرشدهٔ قبلی باید در پیش‌نویس کامل محفوظ بمانند.
 
## منابع و حدود استناد

### IUT

نظریهٔ مجموعه‌ها؛ محسن خانی و افشین زارعی؛ ۱۸ خرداد ۱۴۰۰

https://khani.iut.ac.ir/sites/khani.iut.ac.ir/files/u145/jozve-kamel.pdf

مشورت محلی؛ اصل PDF بازنشر نمی‌شود.

### OLP-BUTTON

اطلاعیهٔ رسمی OLP دربارهٔ ورود Open Set Theory به پروژه، ۲۹ اوت ۲۰۱۹

https://openlogicproject.org/2019/08/29/tim-buttons-open-set-theory-now-part-of-the-open-logic-project/

برای هویت اثر و انتساب، نه شاهد کاربرد اصطلاح فارسی؛ فقط عنوان کوتاه نقل می‌شود.

- I27-PROPER: «زیرمجموعه‌ی سره‌ای»؛ صفحهٔ فایل 27، چاپی 26. بند برهان پس از لم ۱۴: سره برای زیرمجموعهٔ نابرابر آمده است. برهان آن صفحه دربارهٔ خوش‌ترتیبی است؛ تنها اصطلاح و ساختار نثر شرطی آن مبنای کاربرد زبانی است.
- I45-NATURAL: «اعداد طبیعی»؛ صفحهٔ فایل 45، چاپی 44. عنوان بخش و بند پایانی، ساختار اعداد طبیعی را با صفر و تابع جانشین‌مانند s معرفی می‌کنند. نام دقیق تابع جانشین در این صفحه نیامده است؛ برای خود این لفظ شاهد مستقیم ادعا نمی‌شود.
- I46-INJECTION: «تابعی یک‌به‌یک است»؛ صفحهٔ فایل 46، چاپی 45. قضیهٔ ۳۶: یک‌به‌یکی s، نبودن صفر در برد و اصل استقرا با شرط عضویت صفر. ساختار فارسی بیان ویژگی‌ها و برهان، شاهد مناسبی برای همین موضوع است؛ همهٔ فرمول‌های این جزوه مرجع محتوای OLP نیستند.
- I46-CLOSED: «تحت اعمال اردینال‌ها بسته است»؛ صفحهٔ فایل 46، چاپی 45. قضیهٔ ۳۷ شاهد مستقیم ترکیب تحت ... بسته است در نثر ریاضی است؛ بسته‌بودن تحت اعمال اردینال‌ها را با تعریف بسته‌بودن تحت یک تابع یکی نمی‌گیریم.
- I53-INFINITE: «کاردینال‌های نامتناهی»؛ صفحهٔ فایل 53، چاپی 52. نمادگذاری ۱۴ و تعریف ۱۰ برای تمایز متناهی، نامتناهی و شمارا. نامتناهی ددکیندی را از این صفحه نتیجه نمی‌گیریم و با صرف نامتناهی یکسان نمی‌کنیم.
- I72-CLOSURE: «بسته تحت تابع»؛ صفحهٔ فایل 72، چاپی 71. پانوشت ۷، شرط G(β)∈α برای β∈α و ساخت با تکرار تابع را بیان می‌کند. شاهد مستقیم اصطلاح بسته تحت تابع و نثر ساخت است، نه اثبات لم OLP برای تابع دلخواه بدون دامنهٔ بسته.
- OLP-BOOK-IDENTITY: «Tim Button’s Open Set Theory»؛ عنوان اطلاعیه و دو بند نخست؛ انتساب اثر و نام پیشین در برابر Set Theory: An Open Introduction. منبع رسمی هویت کتاب و نویسنده را تأیید می‌کند. Open وصف دسترسی اثر است؛ این عبارت نام نظریه‌ای دربارهٔ مجموعه‌های باز نیست. حفظ عنوان اصلی در متن فارسی مانع این ابهام و امکان یافتن کتاب را فراهم می‌کند. این منبع شاهد فارسی برای حسابی‌سازی نیست.

## وضعیت انتشار

در دامنهٔ ثبت‌شده، تغییر فرمول یا ارجاع فقط با پیش‌تصویر و دلیل صریح مجاز است؛ تفاوت‌های مجاز بالا ثبت شده‌اند و ساختار محیط‌ها و ورودی‌ها حفظ شده است. ساخت خواننده و بازبینی دیداری آن در این نوبت انجام نشد. این گزارش به‌خودی‌خود رسید انتشار نیست. شواهد خصوصیِ فاقد مجوز نباید در بستهٔ عمومی بازنشر شوند.
