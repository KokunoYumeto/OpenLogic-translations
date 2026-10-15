> سابقهٔ بازخوانی و دلیل انتخاب‌ها؛ وضعیت انتشار را باید از رسید همان ویرایش خواند. این گزارش به‌تنهایی رسید انتشار نیست.

# بازبینی فارسی: استقرا، «برهان» ددکیند و اثبات شرودر–برنشتاین

بازخوانی منبع، اصلاح فارسی و ثبت انتخاب‌ها: OpenAI Codex — GPT-6 Astra، کوشش Ultra. این کار بازبینی انسانی نیست.

همهٔ بندهای فعال سه بخش پایانی فصل با متن انگلیسی و متن مؤثر خواننده مقابله شدند. شواهد فارسی واقعاً در این بازبینی خوانده شدند؛ این ثبت، مشورت اولیهٔ مترجم یا تصدیق تک‌تک واژه‌های کل کتاب نیست. پیگیریِ اصلاح دامنهٔ بسته از بخش پیشین، از اصلاح ترجمه و پیشنهاد بهبود جداست.

## نتیجه

37 بند متن/عنوان ثبت شد. 12 موضع در 11 بند اصلاح شد. نسخه‌های اصلاح‌شده برای ادغام آماده‌اند. این یک بازبینی محدود است، نه گواهی کامل کتاب.

۴: تطبیق مستقیم و شاهد روشن؛ ۳: شاهد مرتبط همراه محدودیت بافتی؛ ۲: شاهد لفظی اختصاصی کافی نیست؛ ۱: تصمیم حل‌نشده. این امتیاز اطمینان تحریری است، نه احتمال کالیبره‌شده. بازبینی انسانی بعدی امکان اصلاح است، نه شرط ادامه.

## انتخاب‌ها و اصلاح‌های مستند

### FA-INF52-CLOSURE-APPLICATION

در تعریف اصلاح‌شدهٔ بخش پیشین، بسته‌بودن برای زیرمجموعهٔ دامنه تعریف شده است. X در این قضیه دلخواه است؛ کمینگی را باید به اشتراک آن با N اعمال کرد. این سطر فقط سازگاری کاربرد با اصلاح قبلی را صریح می‌کند؛ قضیهٔ اصلی یا شرط‌های آن عوض نمی‌شوند و خطای مستقل تازه‌ای ادعا نمی‌شود.

پیش از اصلاح:
```latex
آنگاه $N = \closureofunder{s}{o} \subseteq X$.
```

پس از اصلاح:
```latex
آنگاه $N \cap X$ شامل $o$ است و تحت $s$ بسته است، زیرا $s$ مجموعهٔ $N$
را به درون خودش می‌برد. پس $N = \closureofunder{s}{o} \subseteq N \cap X \subseteq X$.
```

شواهد: I46-INDUCTION, I72-CLOSED.
گزینه‌های کنارگذاشته‌شده: محدودکردن X در صورت قضیه، یا اعلام اینکه هر X زیرمجموعهٔ N است، معنا را بی‌دلیل محدود می‌کند.
اطمینان تحریری: 4 از ۴.

### FA-INF52-PARAMETERS

هر با اشیای جمع ناسازگار بود. دلخواه، عموم انتخاب پارامترها را بدون تغییر فرمول یا دامنهٔ سور نگه می‌دارد.

پیش از اصلاح:
```latex
برای هر اشیای $c_1, \ldots, c_k$
```

پس از اصلاح:
```latex
برای اشیای دلخواه $c_1, \ldots, c_k$
```

شواهد: I7-FORMULA, I72-PARAMETERS.
گزینه‌های کنارگذاشته‌شده: حذف دلخواه می‌تواند عموم گزاره را کم‌رنگ کند؛ تبدیل اشیا به متغیرها نیز عبارت توضیحی و صورت دقیق بعدی را خلط می‌کند.
اطمینان تحریری: 4 از ۴.

### FA-INF52-ARITHMETICAL-LAWS

behave as one would hope در این بافت به خواص اعمال حسابی اشاره دارد. صورت فارسی اکنون همین معنا را روشن می‌کند؛ هیچ قانون تازه یا اثباتی افزوده نشده است.

پیش از اصلاح:
```latex
و نشان دهیم که این‌ها چنان رفتار می‌کنند که امید داریم.
```

پس از اصلاح:
```latex
و نشان دهیم که این اعمال خواص مورد انتظار را دارند.
```

شواهد: I34-RECURSION, I46-INDUCTION.
گزینه‌های کنارگذاشته‌شده: رفتار کنند که امید داریم گرتهٔ نارساست؛ نام‌بردن از قوانین جدیدی که این بند نگفته، انجام نمی‌شود.
اطمینان تحریری: 3 از ۴.

### FA-INF53-ANALYSIS

هر سه مورد، نام رشتهٔ mathematical analysis هستند: حسابی‌سازی آنالیز و دو مورد در عبارت حساب، جبر، آنالیز. کانن فارسی همین نام را در بحث ددکیند به کار می‌برد.

پیش از اصلاح:
```latex
تحلیل
```

پس از اصلاح:
```latex
آنالیز
```

شواهد: S17-ANALYSIS, D19-PREFACE.
گزینه‌های کنارگذاشته‌شده: تحلیل عمومی معنای دیگری القا می‌کند؛ آنالیز حقیقی به‌تنهایی همهٔ دامنهٔ عبارت منبع را نمی‌پوشاند.
اطمینان تحریری: 4 از ۴.

### FA-INF53-TOTALITY

دو مورد totality، کل اشیای قابل اندیشیدن را نام می‌برند، نه خاصیت completeness. کلیت در نثر مرتبط فارسی شاهد دارد و در نقل‌قول و نقد پس از آن یکسان می‌شود.

پیش از اصلاح:
```latex
تمامیت
```

پس از اصلاح:
```latex
کلیت
```

شواهد: S21-TOTALITY, D36-THOUGHT.
گزینه‌های کنارگذاشته‌شده: مجموعه جایگزین نمی‌شود، زیرا خود متن در حال نقد یکی‌گرفتن totality و set است؛ تمامیت در این زمینه ممکن است با خاصیت ریاضی خلط شود.
اطمینان تحریری: 4 از ۴.

### FA-INF54-NAIVE

naive وصف رویکرد نظریهٔ مجموعه‌هاست، نه طبیعی بودن نتیجه یا آسان بودن برهان. عبارت در کنار اما ظریف، همین تقابل را روشن می‌کند.

پیش از اصلاح:
```latex
یک برهان طبیعیِ نهایی
```

پس از اصلاح:
```latex
یک برهان پایانی با رویکرد ساده‌انگارانه
```

شواهد: I7-NAIVE, S19-NAIVE.
گزینه‌های کنارگذاشته‌شده: قضیهٔ طبیعی یا برهان بدیهی معنای دیگری دارد؛ حذف ظریف محتوا را کم می‌کند.
اطمینان تحریری: 3 از ۴.

### FA-INF54-CLOSURE-DEFINITION

همان فرض دامنهٔ بستهٔ OLP-INF51-DOMAIN برای بسته‌سازی از یک مجموعهٔ آغازین لازم است. U مجموعهٔ پایه است؛ با f:U→U و B⊆U خانوادهٔ مجموعه‌های بستهٔ شامل B ناتهی است، زیرا U عضو آن است. این یک ادامهٔ همان اصلاح است، نه شمارش یک خطای مستقل.

پیش از اصلاح:
```latex
برای هر مجموعهٔ $B$ و تابع~$f$.
```

پس از اصلاح:
```latex
برای هر مجموعهٔ $B \subseteq U$ و تابع~$f \colon U \to U$.
```

شواهد: I72-CLOSED.
گزینه‌های کنارگذاشته‌شده: رهاکردن B بیرون از دامنه یا اجازهٔ تابعی که تصویرش از دامنه خارج می‌شود، وجود تکرار را تضمین نمی‌کند.
اطمینان تحریری: 4 از ۴.

### FA-INF54-CLOSURE-LEMMA

همان فرض دامنهٔ بستهٔ OLP-INF51-DOMAIN برای بسته‌سازی از یک مجموعهٔ آغازین لازم است. U مجموعهٔ پایه است؛ با f:U→U و B⊆U خانوادهٔ مجموعه‌های بستهٔ شامل B ناتهی است، زیرا U عضو آن است. این یک ادامهٔ همان اصلاح است، نه شمارش یک خطای مستقل.

پیش از اصلاح:
```latex
برای هر تابع $f$ و هر $B$:
```

پس از اصلاح:
```latex
برای هر تابع $f \colon U \to U$ و هر $B \subseteq U$:
```

شواهد: I72-CLOSED.
گزینه‌های کنارگذاشته‌شده: محدودکردن فقط B، بدون بسته‌بودن دامنه تحت f، کافی نیست.
اطمینان تحریری: 4 از ۴.

### FA-INF54-CLOSURE-APPLICATION

کاربرد تعریف اصلاح‌شده به f با دامنهٔ C درست است، زیرا A زیرمجموعهٔ C است. تصریح مقادیر در C اجازهٔ تکرار را روشن می‌کند، بدون ادعای نادرستِ دوسویی‌بودن f از C روی C.

پیش از اصلاح:
```latex
$f \colon C \to A$، بگذارید
```

پس از اصلاح:
```latex
$f \colon C \to A$ (که با توجه به $A \subseteq C$
مقادیرش در $C$ هستند)، بگذارید
```

شواهد: I51-SB, I72-CLOSED.
گزینه‌های کنارگذاشته‌شده: تبدیل گزارهٔ دوسویی C→A به دوسویی C→C معمولاً غلط است؛ فقط مقادیر در دامنه‌اند.
اطمینان تحریری: 4 از ۴.

### INF52-INDUCTION

استقرا و بدیل ساختاری، با حفظ عموم X و حد دامنه.

شرط آغاز، بسته‌بودن و کمینگی در هر بند بررسی شده‌اند؛ اصلاح اشتراک فقط پیامد محدودسازی تعریف قبلی است.
مواضع بررسی‌شده: OLP-0052-P04, OLP-0052-P05, OLP-0052-P06, OLP-0052-P07, OLP-0052-P08, OLP-0052-P09, OLP-0052-P10, OLP-0052-P11.
شواهد: I46-INDUCTION, I46-ISO, I7-FORMULA, I72-CLOSED.
گزینه‌های بررسی‌شده: استقرا به معنی حدس از نمونه‌ها نیست؛ جبر ددکیند با حلقه یا دستگاه عددی معین یکی نمی‌شود.
اطمینان تحریری: 3 از ۴.

### INF52-PARAMETER-RULE

پارامتر، فرمول و متغیر آزاد از هم تفکیک شوند.

شاهد پارامتر در تعریف‌پذیری و شاهد سورهای محدود خوانده شد؛ تمام کاربردهای این سه بند با فرمول خودشان تطبیق دارند.
مواضع بررسی‌شده: OLP-0052-P10, OLP-0052-P11, OLP-0052-P12.
شواهد: I7-FORMULA, I72-PARAMETERS.
گزینه‌های بررسی‌شده: حذف سورهای بیرونی یا تبدیل پارامتر به متغیر مقید بدون ذکر دامنه مجاز نیست.
اطمینان تحریری: 4 از ۴.

### INF52-RECURSION

تعریف بازگشتی اعمال از اصل استقرا جداست.

کانن این جدایی را صریح بیان می‌کند؛ شش معادله منبع محتوا هستند.
مواضع بررسی‌شده: OLP-0052-P13.
شواهد: I34-RECURSION.
گزینه‌های بررسی‌شده: جایگزینی بازگشت با تکرار صرف یا حذف حالت پایه درست نیست.
اطمینان تحریری: 3 از ۴.

### INF53-PHILOSOPHY

تفکیک نقل تاریخی، نقد نویسنده، فرض وجود و نتیجهٔ مشروط.

کانن مرتبط فلسفهٔ ریاضی و شاهد تاریخی واقعاً خوانده شدند؛ هر ادعای OLP به همین نقش محدود است. قیدها و لحن انتقادی هر بند مقابله شدند.
مواضع بررسی‌شده: OLP-0053-P04, OLP-0053-P05, OLP-0053-P06, OLP-0053-P07, OLP-0053-P08, OLP-0053-P09, OLP-0053-P10, OLP-0053-P11, OLP-0053-P12, OLP-0053-P13, OLP-0053-P14.
شواهد: S17-ANALYSIS, S19-NAIVE, S21-TOTALITY, D19-PREFACE, D36-THOUGHT.
گزینه‌های بررسی‌شده: افزودن دفاع یا رد تازهٔ فلسفی، حذف سه‌نقطه، یا جایگزینی کلیت با مجموعه محتوا را عوض می‌کند.
اطمینان تحریری: 3 از ۴.

### INF53-ANALYSIS-RULE

نام رشته آنالیز است؛ هر سه وقوع اصلاح شد.

کانن فارسی در همین زمینهٔ تاریخی آنالیز حقیقی و مختلط را نام می‌برد.
مواضع بررسی‌شده: OLP-0053-P05, OLP-0053-P08.
شواهد: S17-ANALYSIS, D19-PREFACE.
گزینه‌های بررسی‌شده: تحلیل در معنای عام و فقط آنالیز حقیقی در دامنهٔ محدودتر کنار گذاشته شدند.
اطمینان تحریری: 4 از ۴.

### INF53-TOTALITY-RULE

کلیت، اشیای متعدد و مجموعهٔ واحد سه تعبیر متمایزند.

در نقل و نقد، تبدیل کلیت به مجموعه استدلال انتقادی را از بین می‌برد.
مواضع بررسی‌شده: OLP-0053-P10, OLP-0053-P12, OLP-0053-P13.
شواهد: S21-TOTALITY, D36-THOUGHT.
گزینه‌های بررسی‌شده: تمامیت با completeness مشترک است؛ به‌عنوان تنها معادل نادرست در تمام فارسی حکم داده نمی‌شود.
اطمینان تحریری: 4 از ۴.

### INF54-SB

شرودر–برنشتاین؛ یک‌به‌یک، دوسویی، تصویر و برهان خلف با نقش متفاوت.

هر وقوع در استدلال دوشاخه‌ای و ترکیب نهایی مقابله شد. تعریف زبان مقصد و بسط ماکروها ثابت می‌ماند.
مواضع بررسی‌شده: OLP-0054-P04, OLP-0054-P05, OLP-0054-P06, OLP-0054-P10, OLP-0054-P11, OLP-0054-P12, OLP-0054-P13, OLP-0054-P14, OLP-0054-P15, OLP-0054-P16, OLP-0054-P17.
شواهد: I51-SB.
گزینه‌های بررسی‌شده: پوشا به جای یک‌به‌یک، معکوس روی تمام A یا جابه‌جایی ترتیب ترکیب نادرست است.
اطمینان تحریری: 4 از ۴.

### INF54-CLOSED

بسته تحت تابع و کمینگی با شمول، در یک دامنهٔ بسته.

فرض‌های لازم از اصلاح پیشین به کاربردهای این بخش منتقل شدند؛ شاهد U و اشتراک بسته‌ها کنترل شدند.
مواضع بررسی‌شده: OLP-0054-P06, OLP-0054-P07, OLP-0054-P08, OLP-0054-P09, OLP-0054-P12, OLP-0054-P13, OLP-0054-P15.
شواهد: I72-CLOSED.
گزینه‌های بررسی‌شده: بستار توپولوژیک، کوچک‌ترین اندازه، یا دوسویی اجباری خودنگاشت، هیچ‌یک مراد نیستند.
اطمینان تحریری: 4 از ۴.

### INF54-NAIVE-RULE

رویکرد ساده‌انگارانه، همراه با قید ظریف.

شاهد فارسیِ مرتبط توضیح می‌دهد که naive و طبیعی در عنوان نظریه بافت دارند؛ صفت برهان باید همان روش را برساند.
مواضع بررسی‌شده: OLP-0054-P05.
شواهد: I7-NAIVE, S19-NAIVE.
گزینه‌های بررسی‌شده: بدیهی یا آسان معنا را تغییر می‌دهد.
اطمینان تحریری: 3 از ۴.

## بندهای هم‌تراز برای بازبینی انسانی

متن هر دو طرف، بازهٔ دقیق بایت، شمارهٔ خط و هش در INFINITE_0052_0054.public.json موجود است. تکرارهای یک انتخاب در بافت بند خود بررسی شده‌اند؛ این ثبت جای ادعای بی‌پشتوانهٔ تأیید تک‌تک واژه‌ها را نمی‌گیرد.

### محل ادغام اصلاح‌ها: OLP-0052

متن پیشنهادی از قطعهٔ مؤثر خواننده ساخته شده است؛ وصله را نباید مستقیماً بر شاهد بومیِ قدیمی اعمال کرد. شناسه و هش قطعه و متن دقیق پیش و پس از هر اصلاح در دفتر آمده‌اند. شاهد تثبیت‌شده و اصلاح‌های پیشین باید حفظ شوند.

### تفاوت مستند با فرمول منبع: OLP-0052

پیگیری اصلاح OLP-INF51-DOMAIN؛ نه خطای مستقل تازه
در تعریف اصلاح‌شدهٔ بخش پیشین، بسته‌بودن برای زیرمجموعهٔ دامنه تعریف شده است. X در این قضیه دلخواه است؛ کمینگی را باید به اشتراک آن با N اعمال کرد. این سطر فقط سازگاری کاربرد با اصلاح قبلی را صریح می‌کند؛ قضیهٔ اصلی یا شرط‌های آن عوض نمی‌شوند و خطای مستقل تازه‌ای ادعا نمی‌شود.
منبع تثبیت‌شده: `then $N = \closureofunder{s}{o} \subseteq X$.`؛ صورت بررسی‌شده برای تطبیق: `then $N \cap X$ contains $o$ and is $s$-closed, since $s$ maps $N$

into itself. Thus $N = \closureofunder{s}{o} \subseteq N \cap X \subseteq X$.`. متن منبع دست‌نخورده نگه داشته شده است؛ جدول پیش و پس از اصلاح، تفاوت خوانندهٔ جاری و پیشنهاد را مشخص می‌کند.

### بومی‌سازی هم‌معنای ارجاع؛ نه خطای منبع: OLP-0052

بومی‌سازی برچسب استناد، نه تغییر منبع یا شماره
شمارهٔ صفحه/قضیه و شناسهٔ کتاب ثابت‌اند؛ فقط برچسب خواندنی فارسی شده است.
صورت منبع: `\citealt[pp.~95--8]{Potter2004}`؛ صورت فارسی: `\citealt[صص.~95--8]{Potter2004}`. شناسهٔ اثر و محل استناد ثابت‌اند.

### محل ادغام اصلاح‌ها: OLP-0053

متن پیشنهادی از قطعهٔ مؤثر خواننده ساخته شده است؛ وصله را نباید مستقیماً بر شاهد بومیِ قدیمی اعمال کرد. شناسه و هش قطعه و متن دقیق پیش و پس از هر اصلاح در دفتر آمده‌اند. شاهد تثبیت‌شده و اصلاح‌های پیشین باید حفظ شوند.

### بومی‌سازی هم‌معنای ارجاع؛ نه خطای منبع: OLP-0053

بومی‌سازی برچسب استناد، نه تغییر منبع یا شماره
شمارهٔ صفحه/قضیه و شناسهٔ کتاب ثابت‌اند؛ فقط برچسب خواندنی فارسی شده است.
صورت منبع: `\citeyear[Theorems

132--3]{Dedekind1888}`؛ صورت فارسی: `\citeyear[قضیه‌های 132--3]{Dedekind1888}`. شناسهٔ اثر و محل استناد ثابت‌اند.

### بومی‌سازی هم‌معنای ارجاع؛ نه خطای منبع: OLP-0053

بومی‌سازی برچسب استناد، نه تغییر منبع یا شماره
شمارهٔ صفحه/قضیه و شناسهٔ کتاب ثابت‌اند؛ فقط برچسب خواندنی فارسی شده است.
صورت منبع: `\citep[preface]{Dedekind1888}`؛ صورت فارسی: `\citep[پیشگفتار]{Dedekind1888}`. شناسهٔ اثر و محل استناد ثابت‌اند.

### بومی‌سازی هم‌معنای ارجاع؛ نه خطای منبع: OLP-0053

بومی‌سازی برچسب استناد، نه تغییر منبع یا شماره
شمارهٔ صفحه/قضیه و شناسهٔ کتاب ثابت‌اند؛ فقط برچسب خواندنی فارسی شده است.
صورت منبع: `\citet[p.~23]{Potter2004}`؛ صورت فارسی: `\citet[ص.~23]{Potter2004}`. شناسهٔ اثر و محل استناد ثابت‌اند.

### محل ادغام اصلاح‌ها: OLP-0054

متن پیشنهادی از قطعهٔ مؤثر خواننده ساخته شده است؛ وصله را نباید مستقیماً بر شاهد بومیِ قدیمی اعمال کرد. شناسه و هش قطعه و متن دقیق پیش و پس از هر اصلاح در دفتر آمده‌اند. شاهد تثبیت‌شده و اصلاح‌های پیشین باید حفظ شوند.

### تفاوت مستند با فرمول منبع: OLP-0054

پیگیری اصلاح OLP-INF51-DOMAIN؛ نه خطای مستقل تازه
همان فرض دامنهٔ بستهٔ OLP-INF51-DOMAIN برای بسته‌سازی از یک مجموعهٔ آغازین لازم است. U مجموعهٔ پایه است؛ با f:U→U و B⊆U خانوادهٔ مجموعه‌های بستهٔ شامل B ناتهی است، زیرا U عضو آن است. این یک ادامهٔ همان اصلاح است، نه شمارش یک خطای مستقل.
منبع تثبیت‌شده: `for each set $B$ and function~$f$.`؛ صورت بررسی‌شده برای تطبیق: `for each set $B \subseteq U$ and function~$f \colon U \to U$.`. متن منبع دست‌نخورده نگه داشته شده است؛ جدول پیش و پس از اصلاح، تفاوت خوانندهٔ جاری و پیشنهاد را مشخص می‌کند.

### تفاوت مستند با فرمول منبع: OLP-0054

پیگیری اصلاح OLP-INF51-DOMAIN؛ نه خطای مستقل تازه
همان فرض دامنهٔ بستهٔ OLP-INF51-DOMAIN برای بسته‌سازی از یک مجموعهٔ آغازین لازم است. U مجموعهٔ پایه است؛ با f:U→U و B⊆U خانوادهٔ مجموعه‌های بستهٔ شامل B ناتهی است، زیرا U عضو آن است. این یک ادامهٔ همان اصلاح است، نه شمارش یک خطای مستقل.
منبع تثبیت‌شده: `For any function $f$, and any $B$:`؛ صورت بررسی‌شده برای تطبیق: `For any function $f \colon U \to U$, and any $B \subseteq U$:`. متن منبع دست‌نخورده نگه داشته شده است؛ جدول پیش و پس از اصلاح، تفاوت خوانندهٔ جاری و پیشنهاد را مشخص می‌کند.

### تفاوت مستند با فرمول منبع: OLP-0054

پیگیری اصلاح OLP-INF51-DOMAIN؛ نه خطای مستقل تازه
کاربرد تعریف اصلاح‌شده به f با دامنهٔ C درست است، زیرا A زیرمجموعهٔ C است. تصریح مقادیر در C اجازهٔ تکرار را روشن می‌کند، بدون ادعای نادرستِ دوسویی‌بودن f از C روی C.
منبع تثبیت‌شده: `Given !!a{bijection}  $f \colon C \to A$, let`؛ صورت بررسی‌شده برای تطبیق: `Given !!a{bijection}  $f \colon C \to A$ (whose values lie, since $A \subseteq C$,

in $C$), let`. متن منبع دست‌نخورده نگه داشته شده است؛ جدول پیش و پس از اصلاح، تفاوت خوانندهٔ جاری و پیشنهاد را مشخص می‌کند.

### بومی‌سازی هم‌معنای ارجاع؛ نه خطای منبع: OLP-0054

بومی‌سازی برچسب استناد، نه تغییر منبع یا شماره
شمارهٔ صفحه/قضیه و شناسهٔ کتاب ثابت‌اند؛ فقط برچسب خواندنی فارسی شده است.
صورت منبع: `\citet[pp.~157--8]{Potter2004}`؛ صورت فارسی: `\citet[صص.~157--8]{Potter2004}`. شناسهٔ اثر و محل استناد ثابت‌اند.

### OLP-0052-P04

عنوان استقرای حسابی و نام جبرهای ددکیند حفظ شد؛ استقرا از بازگشت در بند پایانی جداست.
شواهد: I46-INDUCTION.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: لفظ خاص جبر ددکیند در این صفحات شاهد مستقیم ندارد؛ تعریف منبع و ثبات نام در بخش‌های پیشین مبنای حفظ آن است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olfileid{sfr}{infinite}{induction}

\olsection[Arithmetical Induction]{Dedekind Algebras and Arithmetical Induction}
```

ترجمهٔ فارسی:
```latex
\olfileid[fa-IR]{sfr}{infinite}{induction}
\olsection[استقرای حسابی]{جبرهای ددکیند و استقرای حسابی}
```

</details>

### OLP-0052-P05

تأکید روی هر جبر و نقش آن به‌عنوان بدیل اعداد طبیعی حفظ است؛ ادعای یکی‌بودن اشیای حامل نمی‌شود.
شواهد: I46-INDUCTION, I46-ISO.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Crucially, now, a Dedekind algebra---indeed, \emph{any} Dedekind

algebra---will serve as a surrogate for the natural numbers. This is

thanks to the following trivial consequence:
```

ترجمهٔ فارسی:
```latex
اکنون نکتهٔ اساسی این است که یک جبر ددکیند---در واقع، \emph{هر} جبر
ددکیند---می‌تواند بدیلی برای اعداد طبیعی باشد. این امر از نتیجهٔ سادهٔ زیر
ناشی می‌شود:
```

</details>

### OLP-0052-P06

شرط صفر، سور روی اشتراک N و X و نتیجهٔ شمول عیناً حفظ‌اند. برخلاف کانن، X اینجا دلخواه است؛ قضیه به X زیرمجموعهٔ N محدود نمی‌شود.
شواهد: I46-INDUCTION, I7-FORMULA.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{thm}[Arithmetical induction]\ollabel{thm:dedinfiniteinduction}

Let $N, s, o$ comprise a Dedekind algebra. Then for any set $X$:  

	\begin{center}

		if $o \in X$ and $(\forall {n} \in N \cap X){s}({n}) \in X$, {then} $N \subseteq X$.

	\end{center}

\end{thm}
```

ترجمهٔ فارسی:
```latex
\begin{thm}[استقرای حسابی]\ollabel{thm:dedinfiniteinduction}
فرض کنید $N, s, o$ یک جبر ددکیند را تشکیل دهند. آنگاه برای هر مجموعهٔ
$X$:
	\begin{center}
		اگر $o \in X$ و $(\forall {n} \in N \cap X){s}({n}) \in X$، {آنگاه} $N \subseteq X$.
	\end{center}
\end{thm}
```

</details>

### OLP-0052-P07

استدلالِ کمینگی پس از اصلاح دامنه به N∩X اعمال شد. چون s از N به N می‌رود و فرض قضیه تصویر عضو اشتراک را در X قرار می‌دهد، اشتراک بسته است و o را دارد. شاهد انگلیسی اصلی تغییر نمی‌کند.
شواهد: I46-INDUCTION, I72-CLOSED.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}

By the definition of a Dedekind algebra, $N = \closureofunder{s}{o}$.

Now if both ${o} \in X$ and $(\forall {n} \in N)(n \in X \lif

{s}({n}) \in X)$, then $N = \closureofunder{s}{o} \subseteq X$.

\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
بنا بر تعریف جبر ددکیند، $N = \closureofunder{s}{o}$. اکنون اگر هم
${o} \in X$ و هم $(\forall {n} \in N)(n \in X \lif
{s}({n}) \in X)$، آنگاه $N \cap X$ شامل $o$ است و تحت $s$ بسته است، زیرا $s$ مجموعهٔ $N$
را به درون خودش می‌برد. پس $N = \closureofunder{s}{o} \subseteq N \cap X \subseteq X$.
\end{proof}
```

</details>

### OLP-0052-P08

از هر مجموعهٔ نامتناهی ددکیندی می‌توان یک جبر ساخت؛ جمله نمی‌گوید حامل جبر لزوماً تمام آن مجموعه است. واژهٔ بدیل با استدلال وجودی سازگار است.
شواهد: I46-INDUCTION, I46-ISO.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Since induction is characteristic of the natural numbers, the point is

this. Given any Dedekind infinite set, we can form a Dedekind algebra,

and use that algebra as our surrogate for the natural numbers. 
```

ترجمهٔ فارسی:
```latex
چون استقرا مشخصهٔ اعداد طبیعی است، نکته چنین است. هر مجموعهٔ نامتناهیِ
ددکیندی که داده شود، می‌توانیم یک جبر ددکیند تشکیل دهیم و آن جبر را بدیل
خود برای اعداد طبیعی قرار دهیم.
```

</details>

### OLP-0052-P09

صورت مجموعه‌شناختی و گذار به صورت فرمولی، با قید شاید آشناتر، حفظ می‌شود؛ آشنایی مخاطب قطعی فرض نمی‌شود.
شواهد: I7-FORMULA, I46-INDUCTION.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Admittedly, \olref{thm:dedinfiniteinduction} formulates induction in

\emph{set-theoretic} terms. But we can easily put the principle in

terms which might be more familiar:
```

ترجمهٔ فارسی:
```latex
البته \olref{thm:dedinfiniteinduction} استقرا را با عبارت‌های
\emph{مجموعه‌شناختی} صورت‌بندی می‌کند. اما به‌آسانی می‌توانیم این اصل را
با عبارت‌هایی بیان کنیم که شاید آشناتر باشند:
```

</details>

### OLP-0052-P10

اجازهٔ پارامتر، پایه و گام استقرا، سورهای محدود و نتیجهٔ همگانی حفظ شدند. پارامتر با متغیرِ مقید اشتباه نمی‌شود.
شواهد: I7-FORMULA, I72-PARAMETERS, I46-INDUCTION.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{cor}\ollabel{natinductionschema}

Let $N, s, o$ comprise a Dedekind algebra. Then for any formula

$\phi(x)$, which may have parameters:

\begin{center}

	if $\phi(o)$ and $(\forall {n} \in N)(\phi(n)\lif

	\phi({s}({n})))$, {then} $(\forall n \in N)\phi(n)$

\end{center}

\end{cor}
```

ترجمهٔ فارسی:
```latex
\begin{cor}\ollabel{natinductionschema}
فرض کنید $N, s, o$ یک جبر ددکیند را تشکیل دهند. آنگاه برای هر فرمول
$\phi(x)$ که ممکن است پارامتر داشته باشد:
\begin{center}
	اگر $\phi(o)$ و $(\forall {n} \in N)(\phi(n)\lif
	\phi({s}({n})))$، {آنگاه} $(\forall n \in N)\phi(n)$
\end{center}
\end{cor}
```

</details>

### OLP-0052-P11

X از اعضای N تعریف می‌شود که فرمول را ارضا می‌کنند؛ استناد به قضیهٔ قبلی محفوظ است و با صورت مجموعه‌ای انطباق دارد.
شواهد: I7-FORMULA, I72-PARAMETERS.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}

Let $X = \Setabs{n \in N}{\phi(n)}$, and now use

\olref{thm:dedinfiniteinduction}

\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
بگذارید $X = \Setabs{n \in N}{\phi(n)}$، و اکنون از
\olref{thm:dedinfiniteinduction} استفاده کنید.
\end{proof}
```

</details>

### OLP-0052-P12

اشیای دلخواه جای ساخت نادرست هر اشیای نشست. همهٔ متغیرهای آزاد نمایش داده شده‌اند و سورهای بیرونی vها حفظ‌اند؛ پارامتر در توضیح، ثابتِ انتخاب‌شده است نه نماد تازهٔ الزامیِ زبان.
شواهد: I7-FORMULA, I72-PARAMETERS.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
In this result, we spoke of a formula ``having parameters''. What this

means, roughly, is that for any objects $c_1, \ldots, c_k$, we can

work with $\phi(x, c_1, \ldots, c_k)$. More precisely, we can state

the result without mentioning ``parameters'' as follows. For any

formula $\phi(x, v_1, \ldots, v_k)$, whose free variables are all

displayed, we have:

	\begin{align*}

			\forall v_1 \ldots \forall v_k((&\phi(o, v_1,\ldots, v_k) \land {}\\

			&	(\forall x \in N)(\phi(x,v_1, \ldots, v_k) \lif \phi(s(x), v_1,\ldots, v_k))) \lif {}\\

			&\hspace{3em} (\forall x \in N)\phi(x, v_1,\ldots, v_k))

	\end{align*}

Evidently, speaking of ``having parameters'' can make things much

easier to read. (In \olref[sth][][]{part}, we will use this device

rather frequently.)
```

ترجمهٔ فارسی:
```latex
در این نتیجه از فرمولی سخن گفتیم که «پارامتر دارد». معنای تقریبی این سخن
آن است که برای اشیای دلخواه $c_1, \ldots, c_k$ می‌توانیم با
$\phi(x, c_1, \ldots, c_k)$ کار کنیم. به‌بیان دقیق‌تر، می‌توانیم نتیجه را
بی‌ذکر «پارامترها» چنین بیان کنیم. برای هر فرمول
$\phi(x, v_1, \ldots, v_k)$ که همهٔ متغیرهای آزادش نمایش داده شده‌اند،
داریم:
	\begin{align*}
			\forall v_1 \ldots \forall v_k((&\phi(o, v_1,\ldots, v_k) \land {}\\
			&	(\forall x \in N)(\phi(x,v_1, \ldots, v_k) \lif \phi(s(x), v_1,\ldots, v_k))) \lif {}\\
			&\hspace{3em} (\forall x \in N)\phi(x, v_1,\ldots, v_k))
	\end{align*}
آشکار است که سخن‌گفتن از «داشتن پارامتر» می‌تواند خواندن مطالب را بسیار
آسان‌تر کند. (در \olref[sth][][]{part} این شیوه را بسیار به کار خواهیم
برد.)
```

</details>

### OLP-0052-P13

شش معادلهٔ بازگشتی، از جمله a به توان o برابر s(o)، دقیقاً حفظ شدند. معرفی و توجیه روش به بعد موکول است؛ اینجا اثباتی اختراع نشده. تعبیر نهایی خواص مورد انتظار را می‌رساند و صفحات استناد ثابت‌اند.
شواهد: I34-RECURSION, I46-INDUCTION.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: کانن خودِ بازگشت و توان را دارد؛ برای ترکیب لفظی تعریف بازگشتی و توان‌رسانی در همین صفحات شاهد عین‌عبارت نداریم، اما تمایز مفهوم و صورت‌های موجود روشن است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Returning to Dedekind algebras: given any Dedekind algebra, we can

also define the usual arithmetical functions of addition,

multiplication and exponentiation. This is non-trivial, however, and

it involves the technique of \emph{recursive definition}. That is a

technique which we shall introduce and justify much later, and in a

much more general context. (Enthusiasts might want to revisit this

after \olref[sth][ord-arithmetic][]{chap}, or perhaps read an alternative

treatment, such as \citealt[pp.~95--8]{Potter2004}.) But, where $N, s, o$

comprise a Dedekind algebra, we will ultimately be able to stipulate the

following:

\begin{align*}

	{a} + {o} &= {a} & & & {a} \times {o} &= {o} & & & {a}^{o} &= s(o)\\

{a} + {s}({b}) &= {s}({a}+{b}) &&& {a} \times {s}({b}) &= ({a}\times {b}) + {a}  & & & {a}^{{s}({b})} &= {a}^{b} \times {a}

\end{align*}

and show that these behave as one would hope.
```

ترجمهٔ فارسی:
```latex
به جبرهای ددکیند بازگردیم: هر جبر ددکیندی که داده شود، می‌توانیم توابع
معمول حسابیِ جمع، ضرب و توان‌رسانی را نیز تعریف کنیم. اما این کار
ساده نیست و فن \emph{تعریف بازگشتی} را به کار می‌گیرد. این فنی است که
بسیار دیرتر و در بافتی بسیار کلی‌تر معرفی و توجیه خواهیم کرد. (علاقه‌مندان
شاید بخواهند پس از \olref[sth][ord-arithmetic][]{chap} به این مطلب
بازگردند، یا شاید شرحی جایگزین، مانند \citealt[صص.~95--8]{Potter2004}، را
بخوانند.) اما هرگاه $N, s, o$ یک جبر ددکیند را تشکیل دهند، در نهایت
خواهیم توانست مطالب زیر را مقرر کنیم:
\begin{align*}
	{a} + {o} &= {a} & & & {a} \times {o} &= {o} & & & {a}^{o} &= s(o)\\
{a} + {s}({b}) &= {s}({a}+{b}) &&& {a} \times {s}({b}) &= ({a}\times {b}) + {a}  & & & {a}^{{s}({b})} &= {a}^{b} \times {a}
\end{align*}
و نشان دهیم که این اعمال خواص مورد انتظار را دارند.
```

</details>

### OLP-0053-P03

شناسهٔ بخش و علامت زبان محفوظ‌اند؛ این بند فقط ساختاری است.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olfileid{sfr}{infinite}{dedekindsproof}
```

ترجمهٔ فارسی:
```latex
\olfileid[fa-IR]{sfr}{infinite}{dedekindsproof}
```

</details>

### OLP-0053-P04

گیومه‌های «برهان» عمدی‌اند و موضع انتقادی متن را حفظ می‌کنند؛ وجود یک مجموعه نامتناهی، نه نامتناهی بودن هر مجموعه، عنوان است.
شواهد: D36-THOUGHT.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olsection[Dedekind's ``Proof'']{Dedekind's ``Proof'' of the 

Existence of an Infinite Set}
```

ترجمهٔ فارسی:
```latex
\olsection[«برهان» ددکیند]{«برهان» ددکیند بر وجود یک
مجموعهٔ نامتناهی}
```

</details>

### OLP-0053-P05

حسابی‌سازی آنالیز جای تعبیر عمومی تحلیل را گرفت. ارجاع دوگزینه‌ای صحیح است: در بخش sfr، [arith][ref] به sfr:arith:ref می‌رسد؛ جایگزینی یا ثبت خطای ارجاع لازم نیست.
شواهد: S17-ANALYSIS.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
In this chapter, we have offered a set-theoretic treatment of the

natural numbers, in terms of Dedekind algebras. In

\olref[arith][ref]{sec}, we reflected on the philosophical

significance of the arithmetisation of analysis (among other things).

Now we should reflect on the significance of what we have achieved

here.
```

ترجمهٔ فارسی:
```latex
در این فصل، اعداد طبیعی را برحسب جبرهای ددکیند به شیوه‌ای مجموعه‌شناختی
بررسی کردیم. در \olref[arith][ref]{sec} دربارهٔ اهمیت فلسفیِ حسابی‌سازیِ
آنالیز (در کنار موضوعات دیگر) تأمل کردیم. اکنون باید دربارهٔ اهمیت آنچه
اینجا به دست آورده‌ایم تأمل کنیم.
```

</details>

### OLP-0053-P06

تمایز ساخت صریح صحیح‌ها، گویاها و حقیقی‌ها با ساخت مشروط طبیعی‌ها حفظ شد؛ وجود مجموعهٔ ددکیندی مفروض است، نه نتیجهٔ اثبات‌شده.
شواهد: I46-INDUCTION, S17-ANALYSIS.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Throughout \olref[sfr][arith][]{chap}, we took the natural numbers as

given, and used them to construct the integers, rationals, and reals,

explicitly. In this chapter, we have not given an explicit

construction of the natural numbers. We have just shown that,

\emph{given any Dedekind infinite set}, we can define a set which will

behave just like we want~$\Nat$ to behave. 
```

ترجمهٔ فارسی:
```latex
در سراسر \olref[sfr][arith][]{chap} اعداد طبیعی را مفروض گرفتیم و با
استفاده از آن‌ها اعداد صحیح، گویا و حقیقی را به‌صراحت ساختیم. در این فصل
ساختی صریح از اعداد طبیعی عرضه نکرده‌ایم. فقط نشان داده‌ایم که
\emph{هر مجموعهٔ نامتناهیِ ددکیندی که داده شود}، می‌توانیم مجموعه‌ای تعریف
کنیم که دقیقاً چنان رفتار کند که از~$\Nat$ می‌خواهیم.
```

</details>

### OLP-0053-P07

کشف در برابر قرارداد، پرسش دربارهٔ هویت اشیا و هم‌ریختی همهٔ جبرها با معنای منبع حفظ‌اند. هم‌ریخت به معنای ایزومرفیسمِ قبلاً تعریف‌شده است.
شواهد: I46-ISO, S21-TOTALITY.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: لفظ مابعدالطبیعی و ساختارگرایان در صفحات خوانده‌شده شاهد مستقیم ندارند؛ معادل‌های موجود بر اساس معنای روشن منبع موقتاً حفظ شده‌اند. قضیه‌های ۱۳۲–۱۳۳ از شاهد اصلی در این نوبت بازاثبات نشدند.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Obviously, then, we cannot claim to have answered a metaphysical

question, such as \emph{which objects are the natural numbers}. But

that's a good thing. After all, in  \olref[sfr][arith][ref]{sec}, we

emphasized that we would be wrong to think of the definition of

$\Real$ as the set of Dedekind cuts as a \emph{discovery}, rather than

a convenient stipulation. The crucial observation is that the Dedekind

cuts exemplify the key mathematical properties of the real

numbers. So too here: the crucial observation is that \emph{any}

Dedekind algebra exemplifies the key mathematical properties of the

natural numbers. (Indeed, Dedekind pushed this point home by proving

that all Dedekind algebras are \emph{isomorphic} (\citeyear[Theorems

132--3]{Dedekind1888}). It is no surprise, then, that many

contemporary ``structuralists'' cite Dedekind as a forerunner.)
```

ترجمهٔ فارسی:
```latex
پس آشکار است که نمی‌توانیم مدعی شویم به پرسشی مابعدالطبیعی، مانند اینکه
\emph{کدام اشیا همان اعداد طبیعی‌اند}، پاسخ داده‌ایم. اما این نکتهٔ خوبی
است. گذشته از این، در \olref[sfr][arith][ref]{sec} تأکید کردیم که اشتباه
است تعریف $\Real$ به‌صورت مجموعهٔ برش‌های ددکیند را به‌جای یک قرارداد
سودمند، \emph{کشف} بدانیم. مشاهدهٔ اساسی این است که برش‌های ددکیند خواص
ریاضیِ اصلیِ اعداد حقیقی را متجلی می‌کنند. در اینجا نیز چنین است: مشاهدهٔ
اساسی این است که \emph{هر} جبر ددکیند خواص ریاضیِ اصلیِ اعداد طبیعی را
متجلی می‌کند. (در واقع، ددکیند با اثبات اینکه همهٔ جبرهای ددکیند
\emph{هم‌ریخت} هستند این نکته را قاطعانه نشان داد
(\citeyear[قضیه‌های 132--3]{Dedekind1888}). پس جای شگفتی نیست که بسیاری
از «ساختارگرایان» معاصر ددکیند را پیشگام خود می‌دانند.)
```

</details>

### OLP-0053-P08

نقل‌قول پیشگفتار با شاهد بمان مقایسه شد؛ تفاوت تعبیرهای انگلیسی آشکار است و OLP مبنای ترجمه می‌ماند. ممکن، ظاهراً و معنای گستردهٔ منطق حفظ‌اند؛ طرح فلسفی ددکیند به‌عنوان حقیقت قطعی عرضه نمی‌شود. آنالیز در هر دو جای این بند اصلاح شد.
شواهد: S17-ANALYSIS, S19-NAIVE, D19-PREFACE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
 Moreover, we have shown how to embed the theory of the natural

 numbers into a na\"ive simple set theory, which itself still remains

 rather informal, but which doesn't (apparently) assume the natural

 numbers as given. So, we may be on the way to realising Dedekind's

 own ambitious project, which he explained thus:

\begin{quote}

	In science nothing capable of proof ought to be believed without

	proof. Though this demand seems reasonable, I cannot regard it as

	having been met even in the most recent methods of laying the

	foundations of the simplest science; viz., that part of logic

	which deals with the theory of numbers. In speaking of arithmetic

	(algebra, analysis) as merely a part of logic I mean to imply that

	I consider the number-concept entirely independent of the notions

	or intuitions of space and time---that I rather consider it an

	immediate product of the pure laws of thought.

	\citep[preface]{Dedekind1888}

\end{quote}

Dedekind's bold idea is this. We have just shown how to build the

natural numbers using (na\"ive) set theory alone. In

\olref[sfr][arith][]{chap}, we saw how to construct the reals given

the natural numbers and some set theory. So, perhaps, ``arithmetic

(algebra, analysis)'' turn out to be ``merely a part of logic'' (in

Dedekind's extended sense of the word ``logic'').
```

ترجمهٔ فارسی:
```latex
افزون بر این، نشان داده‌ایم چگونه نظریهٔ اعداد طبیعی را در یک نظریهٔ
طبیعی و سادهٔ مجموعه‌ها بنشانیم؛ نظریه‌ای که خود هنوز نسبتاً غیرصوری
است، اما (ظاهراً) اعداد طبیعی را مفروض نمی‌گیرد. بنابراین شاید در مسیر
تحقق طرح بلندپروازانهٔ خودِ ددکیند باشیم؛ طرحی که او چنین توضیح داد:
\begin{quote}
	در علم، هیچ امرِ اثبات‌پذیری را نباید بی‌برهان پذیرفت. هرچند این مطالبه
	معقول می‌نماید، نمی‌توانم آن را حتی در جدیدترین شیوه‌های بنیان‌گذاریِ
	ساده‌ترین علم برآورده‌شده بدانم؛ یعنی آن بخش از منطق که به نظریهٔ اعداد
	می‌پردازد. وقتی از حساب (جبر، آنالیز) صرفاً همچون بخشی از منطق سخن
	می‌گویم، مقصودم این است که مفهوم عدد را یکسره مستقل از مفاهیم یا شهودهای
	مکان و زمان می‌دانم---بلکه آن را محصول بی‌واسطهٔ قوانین ناب اندیشه
	می‌دانم.
	\citep[پیشگفتار]{Dedekind1888}
\end{quote}
اندیشهٔ جسورانهٔ ددکیند چنین است. همین اکنون نشان داده‌ایم چگونه اعداد
طبیعی را تنها با استفاده از نظریهٔ طبیعی مجموعه‌ها بسازیم. در
\olref[sfr][arith][]{chap} دیدیم که با داشتن اعداد طبیعی و مقداری نظریهٔ
مجموعه‌ها چگونه اعداد حقیقی را بسازیم. پس شاید «حساب (جبر، آنالیز)» «صرفاً
بخشی از منطق» از آب درآید (با معنای گسترده‌ای که ددکیند برای واژهٔ «منطق»
در نظر داشت).
```

</details>

### OLP-0053-P09

شرط وجود مجموعهٔ نامتناهی ددکیندی و نتیجهٔ متوقف‌شدن طرح بدون اثبات آن، کامل حفظ‌اند. قید ددکیندی حذف نمی‌شود.
شواهد: I46-INDUCTION, D36-THOUGHT.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
That's the idea. But hold on for a moment. Our construction of a

Dedekind algebra (our surrogate for the natural numbers) is

conditional on the existence of a Dedekind infinite set. (Just look

back to \olref[sfr][infinite][dedekind]{thm:DedekindInfiniteAlgebra}.)

Unless the existence of a Dedekind infinite set can be established via

``logic'' or ``the pure laws of thought'', the project stalls. 
```

ترجمهٔ فارسی:
```latex
اندیشه همین است. اما لحظه‌ای درنگ کنید. ساخت ما از یک جبر ددکیند (بدیل ما
برای اعداد طبیعی) مشروط به وجود یک مجموعهٔ نامتناهیِ ددکیندی است. (کافی
است به \olref[sfr][infinite][dedekind]{thm:DedekindInfiniteAlgebra}
بازگردید.) مگر آنکه بتوان وجود یک مجموعهٔ نامتناهیِ ددکیندی را از راه
«منطق» یا «قوانین ناب اندیشه» اثبات کرد، طرح متوقف می‌شود.
```

</details>

### OLP-0053-P10

کلیتِ S با مجموعه نامیده نمی‌شود؛ s، s′ و تصویر آن‌ها متفاوت‌اند. سه‌نقطهٔ OLP حذف عمدی است و با افزودن بخش حذف‌شدهٔ شاهد بمان پُر نمی‌شود. توضیح داخل کروشه و ارجاع ۶۶ محفوظ‌اند.
شواهد: S21-TOTALITY, D36-THOUGHT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
So, \emph{can} the existence of a Dedekind infinite set be established

by ``the pure laws of thought''? Here was Dedekind's effort:

\begin{quote}

  My own realm of thoughts, i.e., the totality $S$ of all things which

  can be objects of my thought, is infinite. For if $s$ signifies an

  element of~$S$, then the thought $s'$ that~$s$ can be an object of

  my thought, is itself an element of~$S$. If we regard this as an

  image $\phi(s)$ of the element~$s$, then \dots~$S$ is [Dedekind]

  infinite, which was to be proved.

	\citep[\S66]{Dedekind1888}

\end{quote}

This is quite an astonishing thing to find in the middle of a book

which largely consists of highly rigorous mathematical proofs. Two

remarks are worth making. 
```

ترجمهٔ فارسی:
```latex
پس آیا \emph{می‌توان} وجود یک مجموعهٔ نامتناهیِ ددکیندی را با «قوانین ناب
اندیشه» اثبات کرد؟ تلاش ددکیند چنین بود:
\begin{quote}
  قلمرو افکار خود من، یعنی کلیتِ $S$، متشکل از همهٔ چیزهایی که می‌توانند موضوع
  اندیشهٔ من باشند، نامتناهی است. زیرا اگر $s$ نشانهٔ عضوی از~$S$ باشد،
  آنگاه اندیشهٔ $s'$ مبنی بر اینکه~$s$ می‌تواند موضوع اندیشهٔ من باشد،
  خود عضوی از~$S$ است. اگر این را تصویری به‌صورت $\phi(s)$ از عضو~$s$ بدانیم،
  آنگاه \dots~$S$ [به معنای ددکیندی] نامتناهی است، و این همان چیزی بود
  که باید ثابت می‌شد.
	\citep[\S66]{Dedekind1888}
\end{quote}
یافتن چنین مطلبی در میانهٔ کتابی که بخش عمده‌اش از برهان‌های ریاضیِ بسیار
دقیق تشکیل شده، کاملاً شگفت‌آور است. دو نکته شایستهٔ ذکرند.
```

</details>

### OLP-0053-P11

صرفاً ممکن‌بودن افکار و نقد ماهیت روان‌شناختیِ استدلال حفظ‌اند؛ جمله دربارهٔ بالفعل بودن بی‌نهایت فکر ادعای تازه ندارد.
شواهد: D36-THOUGHT, S21-TOTALITY.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
First: this ``proof'' scarcely has what we would now recognize as a

``mathematical'' character. It speaks of psychological objects

(thoughts), and merely \emph{possible} ones at that.
```

ترجمهٔ فارسی:
```latex
نخست: این «برهان» به‌سختی خصلتی دارد که امروزه آن را «ریاضی» بشناسیم. این
برهان از اشیای روان‌شناختی (اندیشه‌ها) سخن می‌گوید، آن هم اشیایی که صرفاً
\emph{ممکن} هستند.
```

</details>

### OLP-0053-P12

تفاوت بی‌نهایت چیز به صیغهٔ جمع با یک مجموعهٔ واحد، محور نقد است و عیناً حفظ شد. ماکروی اعضا به صورت جمع فارسی بسط می‌یابد؛ عنصر واحد جایگزین نمی‌شود.
شواهد: D36-THOUGHT, S21-TOTALITY.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Second: at least as we have presented Dedekind algebras, this

``proof'' has a straightforward technical shortcoming. If Dedekind's

argument is successful, it establishes only that there are infinitely

many things (specifically, infinitely many thoughts). But Dedekind

also needs to give us a reason to regard~$S$ as a single \emph{set},

with infinitely many !!{element}s, rather than thinking of~$S$ as

\emph{some things} (in the plural). 
```

ترجمهٔ فارسی:
```latex
دوم: دست‌کم با نحوه‌ای که ما جبرهای ددکیند را عرضه کرده‌ایم، این «برهان»
کاستیِ فنیِ سرراستی دارد. اگر استدلال ددکیند موفق باشد، تنها ثابت می‌کند
که بی‌نهایت چیز وجود دارد (به‌طور مشخص، بی‌نهایت اندیشه). اما ددکیند همچنین
باید دلیلی به ما بدهد تا~$S$ را یک \emph{مجموعهٔ} واحد، که بی‌نهایت
!!{element}s دارد، بدانیم، به‌جای آنکه~$S$ را \emph{چیزهایی} (به صیغهٔ
جمع) تلقی کنیم.
```

</details>

### OLP-0053-P13

دومین کلیت با نقل‌قول یکسان شد؛ شاید، دقیقاً، ما و برخی اصول کلی همگی محفوظ‌اند. پارادوکس راسل نتیجهٔ نداشتن محدودیت‌های مناسب بر تشکیل مجموعه‌هاست، نه نتیجهٔ صرف استفاده از هر تعریف شهودی. ارجاع پاتر ثابت است.
شواهد: S19-NAIVE, S21-TOTALITY.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: پاتر صفحهٔ ۲۳ در این نوبت مستقیماً خوانده نشد؛ ادعای تاریخی فقط مطابق متن OLP حفظ شده و مستقل تصدیق نمی‌شود.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
The fact that Dedekind did not see a gap here might suggest that his

use of the word ``totality'' does not precisely track \emph{our} use

of the word ``set''.\footnote{Indeed, we have other reasons to think

it did not; see \citet[p.~23]{Potter2004}.} But this would not be

too surprising. The project we have pursued in the last two

chapters---a ``construction'' of the naturals, and from them a

``construction'' of the integers, reals and rationals---has all been

carried out na\"ively. We have helped ourselves to this set, or that

set, as and when we have needed them, without laying down many general

principles concerning exactly which sets exist, and when. But we know

that we need \emph{some} general principles, for otherwise we will

fall into Russell's Paradox.
```

ترجمهٔ فارسی:
```latex
این واقعیت که ددکیند در اینجا شکافی ندید شاید نشان دهد کاربرد واژهٔ
«کلیت» نزد او دقیقاً با کاربرد \emph{ما} از واژهٔ «مجموعه» متناظر نیست.
\footnote{در واقع، دلایل دیگری نیز داریم که چنین نبوده است؛ بنگرید به
\citet[ص.~23]{Potter2004}.} اما این امر چندان شگفت‌آور نیست. طرحی که در دو
فصل گذشته دنبال کردیم---«ساختن» اعداد طبیعی و از آن‌ها «ساختن» اعداد صحیح،
حقیقی و گویا---یکسره به شیوه‌ای ساده‌انگارانه انجام شده است. هر زمان که به
این مجموعه یا آن مجموعه نیاز داشته‌ایم، آن را مفروض گرفته‌ایم، بی‌آنکه
اصول کلیِ بسیاری دربارهٔ اینکه دقیقاً کدام مجموعه‌ها و چه هنگام وجود دارند
وضع کنیم. اما می‌دانیم به \emph{برخی} اصول کلی نیاز داریم؛ وگرنه به
پارادوکس راسل گرفتار خواهیم شد.
```

</details>

### OLP-0053-P14

جملهٔ گذار نهایی بازی معنایی naive را حفظ می‌کند؛ مخاطب کم‌هوش یا کودک خطاب نمی‌شود.
شواهد: I7-NAIVE, S19-NAIVE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
 The time has come for us to outgrow our na\"ivety. 
```

ترجمهٔ فارسی:
```latex
زمان آن رسیده است که از ساده‌انگاریِ خود فراتر برویم.
```

</details>

### OLP-0054-P03

شناسهٔ بخش و علامت زبان دقیقاً حفظ‌اند.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olfileid{sfr}{infinite}{card-sb}
```

ترجمهٔ فارسی:
```latex
\olfileid[fa-IR]{sfr}{infinite}{card-sb}
```

</details>

### OLP-0054-P04

نام قضیه و نقش ضمیمه در عنوان محفوظ‌اند؛ کانن، هویت شرودر–برنشتاین را با پانوشت انگلیسی مشخص می‌کند.
شواهد: I51-SB.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olsection{Appendix: Proving Schr\"oder-Bernstein}
```

ترجمهٔ فارسی:
```latex
\olsection{ضمیمه: اثبات شرودر–برنشتاین}
```

</details>

### OLP-0054-P05

دو تزریق در دو جهت و وجود دوسویی حفظ شد. صفت naive به رویکرد ساده‌انگارانه بازگردانده شد؛ شرط‌های قضیه یا دشواری برهان تضعیف نمی‌شوند.
شواهد: I51-SB, I7-NAIVE, S19-NAIVE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Before we depart from na\"ive set theory, we have one last na\"ive

(but sophisticated!) proof to consider. This is a proof of

Schr\"oder-Bernstein (\olref[sfr][siz][sb]{thm:schroder-bernstein}): if

$\cardle{A}{B}$ and $\cardle{B}{A}$ then $\cardeq{A}{B}$; i.e., given

!!{injection}s $f \colon A \to B$ and $g \colon B \to A$ there is

!!a{bijection} $h \colon A \to B$. 
```

ترجمهٔ فارسی:
```latex
پیش از آنکه نظریهٔ طبیعی مجموعه‌ها را ترک کنیم، باید یک برهان پایانی با رویکرد ساده‌انگارانه
(اما ظریف!) را بررسی کنیم. این، برهانِ قضیهٔ شرودر–برنشتاین
(\olref[sfr][siz][sb]{thm:schroder-bernstein}) است: اگر
$\cardle{A}{B}$ و $\cardle{B}{A}$، آنگاه $\cardeq{A}{B}$؛ یعنی، با داشتن
!!{injection}s $f \colon A \to B$ و $g \colon B \to A$، !!a{bijection}
$h \colon A \to B$ وجود دارد.
```

</details>

### OLP-0054-P06

انتساب روش به ددکیند و استناد پاتر و مثال گنگ‌بودن ریشهٔ دو حفظ‌اند؛ نسخهٔ دیگری از برهان جای متن مبنا را نگرفته است.
شواهد: I72-CLOSED, I51-SB.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: لفظ بستارها در صفحهٔ خوانده‌شده عیناً نیامده؛ بسته تحت تابع شاهد مستقیم دارد. بستار به‌عنوان نام تعریف دقیق منبع موقتاً حفظ شده است؛ انتساب تاریخی برهان مستقل بازبینی نشده.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
In this chapter, we followed Dedekind's notion of \emph{closures}. In

fact, Dedekind provided a lovely proof of Schr\"oder-Bernstein using this notion, and we

will present it here. The proof closely follows

\citet[pp.~157--8]{Potter2004}, if you want a slightly different but

essentially similar treatment. A little googling will also convince

you that this is a theorem---rather like the irrationality of

$\sqrt{2}$---for which \emph{many} interesting and different proofs

exist.
```

ترجمهٔ فارسی:
```latex
در این فصل، از مفهوم \emph{بستارها} نزد ددکیند پیروی کردیم. در واقع،
ددکیند با استفاده از این مفهوم برهانی دل‌انگیز برای شرودر–برنشتاین عرضه
کرد و ما آن را اینجا ارائه خواهیم کرد. برهان حاضر از نزدیک از
\citet[صص.~157--8]{Potter2004} پیروی می‌کند؛ اگر شرحی اندکی متفاوت اما در
اساس مشابه می‌خواهید، به آن بنگرید. اندکی جست‌وجو در وب نیز شما را متقاعد خواهد کرد که این
قضیه---همچون گنگ‌بودنِ $\sqrt{2}$---از آن قضیه‌هایی است که برهان‌های جالب
و متفاوتِ \emph{بسیاری} برایشان وجود دارد.
```

</details>

### OLP-0054-P07

اشتراک خانوادهٔ بسته‌های شامل B با فرض خودنگاشت و B در دامنه بررسی شد. تعبیر کوچک‌ترین شمولی است، نه کمترین تعداد عضو. نثر درون فرمول ترجمه شده ولی فرمول‌های توکار محفوظ‌اند.
شواهد: I72-CLOSED.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Using similar notation as \olref[sfr][infinite][dedekind]{Closure},

let

\[

\Closureofunder{f}{B} = \bigcap \Setabs{X}{B \subseteq X 

\text{ and $X$ is $f$-closed}}

\]

for each set $B$ and function~$f$. Defined thus,

$\Closureofunder{f}{B}$ is the smallest $f$-closed set containing~$B$,

in that:
```

ترجمهٔ فارسی:
```latex
با استفاده از نمادگذاری‌ای مشابه آنچه در \olref[sfr][infinite][dedekind]{Closure} آمده است،
قرار دهید
\[
\Closureofunder{f}{B} = \bigcap \Setabs{X}{B \subseteq X
\text{ و $X$ تحت $f$ بسته است}}
\]
برای هر مجموعهٔ $B \subseteq U$ و تابع~$f \colon U \to U$. با این تعریف، $\Closureofunder{f}{B}$
کوچک‌ترین مجموعهٔ بسته تحت $f$ است
که~$B$ را دربرمی‌گیرد، بدین معنا که:
```

</details>

### OLP-0054-P08

سه ویژگیِ شامل‌بودن، بسته‌بودن و کمینگی از هم جدا و ترتیب آن‌ها ثابت است. فرض‌های دامنه صریح شده‌اند؛ تعداد ویژگی‌ها یا کمیت‌گذارها تغییر دیگری ندارند.
شواهد: I72-CLOSED.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{lem}\ollabel{Closureprops}

	For any function $f$, and any $B$:

	\begin{enumerate}

		\item\ollabel{Closurehaselem} $B \subseteq \Closureofunder{f}{B}$; and

		\item\ollabel{Closureclosed} $\Closureofunder{f}{B}$ is $f$-closed; and

		\item\ollabel{Closuresmallest} if $X$ is $f$-closed and $B

		\subseteq X$, then $\Closureofunder{f}{B} \subseteq X$.

	\end{enumerate}

\end{lem}
```

ترجمهٔ فارسی:
```latex
\begin{lem}\ollabel{Closureprops}
	برای هر تابع $f \colon U \to U$ و هر $B \subseteq U$:
	\begin{enumerate}
		\item\ollabel{Closurehaselem} $B \subseteq \Closureofunder{f}{B}$؛ و
		\item\ollabel{Closureclosed} $\Closureofunder{f}{B}$ تحت $f$ بسته است؛ و
		\item\ollabel{Closuresmallest} اگر $X$ تحت $f$ بسته باشد و $B
		\subseteq X$، آنگاه $\Closureofunder{f}{B} \subseteq X$.
	\end{enumerate}
\end{lem}
```

</details>

### OLP-0054-P09

استناد به برهان بخش قبل حفظ شد؛ با فرض‌های اصلاح‌شده، شاهد U برای ناتهی‌بودن خانواده کافی است و استدلال اشتراک عیناً اعمال می‌شود.
شواهد: I72-CLOSED.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}

Exactly as in \olref[sfr][infinite][dedekind]{closureproperties}.

\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
دقیقاً همانند \olref[sfr][infinite][dedekind]{closureproperties}.
\end{proof}
```

</details>

### OLP-0054-P10

جملهٔ گذار به گزارهٔ واسطه کوتاه و مطابق منبع مانده است؛ قضیهٔ تازه‌ای افزوده نشد.
شواهد: I51-SB.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
We need one last fact to get to Schr\"oder-Bernstein:
```

ترجمهٔ فارسی:
```latex
برای رسیدن به شرودر–برنشتاین به یک واقعیت دیگر نیاز داریم:
```

</details>

### OLP-0054-P11

A⊆B⊆C و هم‌توانی دو سر زنجیر حفظ‌اند. ماکروی تو‌در‌تو همان زنجیر هم‌توانی است؛ به‌عنوان خرابی فرمول یا خطای تازه تغییر داده نمی‌شود.
شواهد: I51-SB.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}\ollabel{sbhelper}

If $A \subseteq B \subseteq C$ and $A \approx C$, then $\cardeq{\cardeq{A}{B}}{C}$.

\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop}\ollabel{sbhelper}
اگر $A \subseteq B \subseteq C$ و $A \approx C$، آنگاه $\cardeq{\cardeq{A}{B}}{C}$.
\end{prop}
```

</details>

### OLP-0054-P12

دامنهٔ C، دو شاخهٔ g، مقصد B و جهت ترکیب f معکوس سپس g بررسی شد. شرط A⊆C، کاربرد بستار را پس از اصلاح دامنه توضیح می‌دهد و دوسویی C→C ادعا نمی‌شود.
شواهد: I51-SB, I72-CLOSED.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}

Given !!a{bijection}  $f \colon C \to A$, let $F =

\Closureofunder{f}{C \setminus B}$ and define a function $g$ with

domain $C$ as follows:

\[

	g(x) = 

	\begin{cases}

			f(x) &\text{if $x \in F$}\\

			x & \text{otherwise}

		\end{cases}

\]

We'll show that $g$ is !!a{bijection} from $C \to B$, from which it

will follow that $\comp{f^{-1}}{g} \colon A \to B$ is !!a{bijection},

completing the proof.
```

ترجمهٔ فارسی:
```latex
\begin{proof}
با داشتن !!a{bijection} $f \colon C \to A$ (که با توجه به $A \subseteq C$
مقادیرش در $C$ هستند)، بگذارید $F =
\Closureofunder{f}{C \setminus B}$، و تابعی چون $g$ با دامنهٔ $C$ به‌صورت
زیر تعریف کنید:
\[
	g(x) =
	\begin{cases}
			f(x) &\text{اگر $x \in F$}\\
			x & \text{در غیر این صورت}
		\end{cases}
\]
نشان خواهیم داد که $g$ یک !!a{bijection} به‌صورت $C \to B$ است؛ از این امر
نتیجه خواهد شد که $\comp{f^{-1}}{g} \colon A \to B$ یک !!a{bijection}
است، و برهان کامل خواهد شد.
```

</details>

### OLP-0054-P13

در شاخه‌های متفاوت، فرض برابری دو تصویر به عضویت y در F می‌انجامد و با فرض آن تناقض دارد؛ نقش برهان خلف و ترتیب تساوی‌ها محفوظ‌اند.
شواهد: I51-SB, I72-CLOSED.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
First we claim that if $x \in F$ but $y\notin F$ then $g(x) \neq

g(y)$. For reductio suppose otherwise, so that $y = g(y) = g(x) =

f(x)$. Since $x \in F$ and $F$ is $f$-closed by \olref{Closureprops},

we have $y = f(x) \in F$, a contradiction. 
```

ترجمهٔ فارسی:
```latex
نخست ادعا می‌کنیم اگر $x \in F$ اما $y\notin F$، آنگاه $g(x) \neq
g(y)$. برای برهان خلف، خلاف آن را فرض کنید؛ در این صورت $y = g(y) = g(x) =
f(x)$. چون $x \in F$ و بنا بر \olref{Closureprops}، $F$ تحت $f$ بسته
است، داریم $y = f(x) \in F$، که تناقض است.
```

</details>

### OLP-0054-P14

یک‌به‌یکی از دو حالت داخل و خارج F نتیجه می‌شود؛ دوسویی f فقط در حالت اول به‌کار می‌رود. یک‌به‌یکی g به پوشابودن اشتباه نشده است.
شواهد: I51-SB.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Now suppose $g(x) = g(y)$. So, by the above, $x \in F$ iff $y \in F$.

If $x, y \in F$, then $f(x) = g (x) = g(y) = f(y)$ so that $x = y$

since $f$ is !!a{bijection}. If  $x, y \notin F$, then $x = g(x) =

g(y) = y$. So $g$ is !!a{injection}.
```

ترجمهٔ فارسی:
```latex
اکنون فرض کنید $g(x) = g(y)$. پس، بنا بر آنچه در بالا آمد، $x \in F$ اگر
و تنها اگر $y \in F$. اگر $x, y \in F$، آنگاه $f(x) = g (x) = g(y) = f(y)$؛
پس $x = y$، زیرا $f$ یک !!a{bijection} است. اگر $x, y \notin F$، آنگاه
$x = g(x) = g(y) = y$. بنابراین $g$ یک !!a{injection} است.
```

</details>

### OLP-0054-P15

برای x∈B∩F، نبودن پیش‌تصویر در F سبب بسته‌ماندن F بدون x است و چون x در B است، مجموعهٔ آغازین C بدون B باقی می‌ماند؛ این با کمینگی تعارض دارد. قسمت بیرون F ثابت می‌ماند. شمول برد g در B نیز از تعریف دو شاخه و A⊆B پیداست؛ جملهٔ آموزشی تازه‌ای اضافه نشده.
شواهد: I51-SB, I72-CLOSED.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
It remains to show that $\ran{g} = B$. So fix $x \in B \subseteq C$.

If $x \notin F$, then $g(x) = x$. If $x \in F$, then $x = f(y)$ for

some $y \in F$, since otherwise $F \setminus \{x\}$ would be $f$-closed and extend $C\setminus B$, which is impossible by \olref{Closureprops}; now $g(y) = f(y) = x$.

\end{proof}
```

ترجمهٔ فارسی:
```latex
تنها مانده است نشان دهیم $\ran{g} = B$. پس $x \in B \subseteq C$ را ثابت
بگیرید. اگر $x \notin F$، آنگاه $g(x) = x$. اگر $x \in F$، آنگاه
$x = f(y)$ برای یک $y \in F$؛ زیرا در غیر این صورت $F \setminus \{x\}$
تحت $f$ بسته می‌بود و $C\setminus B$ را دربرمی‌گرفت، که بنا بر
\olref{Closureprops} ناممکن است؛ اکنون $g(y) = f(y) = x$.
\end{proof}
```

</details>

### OLP-0054-P16

نماد تصویر مجموعه، h و D حفظ شد؛ کاربرد بعدی D را در دامنهٔ تابع می‌گیرد. این بند بهانهٔ تغییر تعریف تصویر یا ثبت خطای اثبات‌نشده نیست.
شواهد: I51-SB.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Finally, here is the proof of the main result. Recall that given a

function $h$ and set $D$, we define $\funimage{h}{D} = \Setabs{h(x)}{x

\in D}$. 
```

ترجمهٔ فارسی:
```latex
سرانجام، این هم برهان نتیجهٔ اصلی. به یاد آورید که برای تابع $h$ و مجموعهٔ
$D$، تعریف می‌کنیم $\funimage{h}{D} = \Setabs{h(x)}{x
\in D}$.
```

</details>

### OLP-0054-P17

ترکیب f سپس g، دوسویی روی تصویر، کاربرد گزارهٔ واسطه و معکوس g فقط روی g[B] بررسی شدند. ترتیب آرگومان‌های ماکرو از تعریف composition.tex خوانده شد؛ ترتیب ظاهری اشتباه تعبیر نمی‌شود.
شواهد: I51-SB.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}[Proof of Schr\"oder-Bernstein] Let $f \colon A \to B$

and $g \colon B \to A$ be !!{injection}s. Since $\funimage{f}{A}

\subseteq B$ we have that $\funimage{g}{\funimage{f}{A}} \subseteq

g[B] \subseteq A$. Also, $\comp{f}{g} \colon A \to

\funimage{g}{\funimage{f}{A}}$ is an !!{injection} since both $g$ and

$f$ are; and indeed $\comp{f}{g}$ is !!a{bijection}, just by the way

we defined its codomain. So

$\cardeq{\funimage{g}{\funimage{f}{A}}}{A}$, and hence by

\olref{sbhelper} there is !!a{bijection} $h \colon A \to

\funimage{g}{B}$. Moreover, $g^{-1}$ is !!a{bijection}

$\funimage{g}{B} \to B$. So $\comp{h}{g^{-1}} \colon A \to B$ is

!!a{bijection}. 

\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}[برهان شرودر–برنشتاین] فرض کنید $f \colon A \to B$
و $g \colon B \to A$، !!{injection}s باشند. چون $\funimage{f}{A}
\subseteq B$، داریم $\funimage{g}{\funimage{f}{A}} \subseteq
g[B] \subseteq A$. همچنین، $\comp{f}{g} \colon A \to
\funimage{g}{\funimage{f}{A}}$ یک !!{injection} است، زیرا $g$ و
$f$ هر دو چنین‌اند؛ و در واقع $\comp{f}{g}$ یک !!a{bijection} است، صرفاً
به سبب نحوه‌ای که هم‌دامنهٔ آن را تعریف کردیم. پس
$\cardeq{\funimage{g}{\funimage{f}{A}}}{A}$، و ازاین‌رو بنا بر
\olref{sbhelper}، یک !!a{bijection} چون $h \colon A \to
\funimage{g}{B}$ وجود دارد. افزون بر این، $g^{-1}$ یک !!a{bijection}
$\funimage{g}{B} \to B$ است. بنابراین $\comp{h}{g^{-1}} \colon A \to B$
یک !!a{bijection} است.
\end{proof}
```

</details>

## یافته‌های تکمیلی و حدود بازبینی

۳۷ بند/عنوان فعال در سه بخش مقابله شدند؛ دو بند فقط شناسهٔ ساختاری‌اند. اصلاح‌های لفظی آنالیز، کلیت، پارامتر و تعبیر naive به شواهد خوانده‌شده متصل‌اند. فرض دامنهٔ بسته به تعریف/لمِ بستار مجموعه‌ای و دو کاربرد بعدی منتقل شد؛ این ادامهٔ یک یافتهٔ پیشین است، نه چهار خطای مستقل. ارجاع کوتاه و ترتیب ترکیب معتبرند و تغییر نکردند. همهٔ ۸۴ اصلاح منتشرشده و ۹ اصلاح انباشتهٔ قبلی باید حفظ شوند.
 
## منابع و حدود استناد

### IUT

نظریهٔ مجموعه‌ها؛ محسن خانی و افشین زارعی؛ ۱۸ خرداد ۱۴۰۰

https://khani.iut.ac.ir/sites/khani.iut.ac.ir/files/u145/jozve-kamel.pdf

مشورت محلی؛ اصل PDF بازنشر نمی‌شود.

### SHARIF

نشریهٔ ریاضی شریف، دورهٔ سوم، شمارهٔ دوم؛ مقالهٔ ژوزه فریروس دربارهٔ مبانی ریاضیات

https://sharif-math-journal.github.io/assets/archive/thirdSeries/3rdSeries_Issue2.pdf

کانن فارسیِ فلسفه و تاریخ ریاضیات؛ فقط مشورت محلی و نقل‌های کوتاه. PDF در بستهٔ عمومی بازنشر نمی‌شود.

### DEDEKIND-BEMAN

ریشارد ددکیند، Essays on the Theory of Numbers؛ ترجمهٔ مجاز W. W. Beman، ۱۹۰۱؛ نسخهٔ متنی پروژهٔ گوتنبرگ ۲۱۰۱۶

https://www.gutenberg.org/files/21016/21016-pdf.pdf

شاهد تاریخیِ انگلیسی برای نقل‌قول‌ها؛ نه کانن فارسی و نه تصویر چاپ آلمانی. نسخهٔ گوتنبرگ در ایالات متحده در مالکیت عمومی معرفی شده است؛ اینجا فقط محلی بررسی می‌شود و ادعای مجوز جهانی یا مقابله با اصل آلمانی نداریم.

- I7-FORMULA: «متغیر آزاد»؛ صفحهٔ فایل 7، چاپی 6. تعریف متغیر آزاد، فرمول مرتبهٔ اول و کوتاه‌نویسی سورهای محدود؛ برای حفظ دامنهٔ سور و نثر معرفی فرمول، نه تبدیل فرمول به جملهٔ بی‌متغیر.
- I7-NAIVE: «نظریه‌ی ساده‌انگارانه‌ی»؛ صفحهٔ فایل 7، چاپی 6. پایان صفحه و پانوشت naive، رویکرد غیرموضوعی آغاز بحث را نام می‌برند؛ ساده‌انگارانه در این بافت وصف روش است، نه ارزش‌داوری دربارهٔ هوش خواننده.
- I34-RECURSION: «قضیۀ بازگشت»؛ صفحهٔ فایل 34، چاپی 33. عنوان و متن بخش، استقرا را از تعریف تابع با بازگشت جدا می‌کنند و جمع، ضرب و توان را نام می‌برند. همین تمایز در بند پایانی ۰۰۵۲ لازم است؛ صورت فرمول‌های کانن جای فرمول OLP نمی‌نشیند.
- I46-INDUCTION: «اصول پئانو»؛ صفحهٔ فایل 46، چاپی 45. قضیهٔ ۳۶ و برهان آن، صفر، تابع یک‌به‌یک و استقرا را در نثر فارسی به هم پیوند می‌دهند. کاربرد استقرا به مجموعهٔ دارای صفر و بسته تحت تابع محدود است؛ کمیت‌گذارهای OLP جداگانه بررسی شده‌اند.
- I46-ISO: «ایزومرفیسم بین دو ساختار»؛ صفحهٔ فایل 46، چاپی 45. برهان قضیهٔ ۳۶ همین مفهوم را دربارهٔ ساختارهای طبیعی‌ها به کار می‌برد. هم‌ریخت در خواننده قبلاً با تعریف ایزومرفیسم معرفی شده است؛ این شاهد، معنای دوسوییِ حافظ ساختار را پشتیبانی می‌کند، نه معنای ضعیف همومورفیسم.
- I51-SB: «قضیه‌ی شرودر–برنشتاین»؛ صفحهٔ فایل 51، چاپی 50. نتیجهٔ ۷: یک‌به‌یکی در دو جهت و هم‌توانی؛ پانوشت انگلیسی هویت نام را مشخص می‌کند. برهان قبلی جزوه از انتخاب استفاده می‌کند؛ آن روش یا لغزش‌های نمادی آن به برهان مستقل OLP منتقل نمی‌شوند.
- I72-CLOSED: «بسته تحت تابع»؛ صفحهٔ فایل 72، چاپی 71. پانوشت ۷، بسته‌بودن تحت G و تکرار را بیان می‌کند. برای اصطلاح و ترتیب شرطی فارسی استفاده شده است؛ وجود بستار برای تابع بدون دامنهٔ بسته را ثابت نمی‌کند.
- I72-PARAMETERS: «تعریف‌پذیر (با پارامتر)»؛ صفحهٔ فایل 72، چاپی 71. تعریف ۶، مجموعه‌های تعریف‌پذیر با پارامتر و فرمول دارای چند متغیر را می‌آورد؛ شاهد مستقیم برای پارامتر در بافت منطقی، نه ادعای اینکه هر شیء یک نماد زبان است.
- S17-ANALYSIS: «آنالیز حقیقی و آنالیز مختلط»؛ صفحهٔ فایل 17، چاپی 15. در بحث ددکیند و مبانی ریاضی، نام رشته آنالیز آمده است. سه مورد analysis در ۰۰۵۳ نام همین رشته‌اند و با تحلیل به معنای عمومی جایگزین نمی‌شوند.
- S19-NAIVE: «نظریه‌ی طبیعی»؛ صفحهٔ فایل 19، چاپی 17. متن، اصطلاح طبیعی را به کار می‌برد و پانوشت ۲، ساده‌اندیشانه را برای حفظ بازی معنایی naive پیشنهاد می‌کند. بنابراین نظریهٔ طبیعی در ترجمه خطا اعلام نمی‌شود، ولی برهان طبیعیِ نهایی روشن‌سازی می‌شود.
- S21-TOTALITY: «یک کلیت کامل»؛ صفحهٔ فایل 21، چاپی 19. بند نخست دربارهٔ تعاریف نامحمولی، کلیت را برای کلِ اشیا به کار می‌برد؛ در همان صفحه تمامیت برای خاصیت اعداد حقیقی آمده است. تمایز برای totality در نقل‌قول و نقد ددکیند مرتبط است؛ یگانه‌بودن این ترجمه ادعا نمی‌شود.
- D19-PREFACE: «arithmetic (algebra, analysis)»؛ صفحهٔ فایل 19، چاپی 14. پیشگفتار نسخهٔ نخست: نقل‌قول دربارهٔ عدد، منطق و استقلال از شهود مکان و زمان بررسی شد. تعبیر انگلیسی OLP اندکی با بمان فرق دارد؛ ترجمهٔ فارسی از OLP پیروی می‌کند و به دروغ ترجمهٔ مستقیم آلمانی معرفی نمی‌شود.
- D36-THOUGHT: «the totality S of all things»؛ صفحهٔ فایل 36، چاپی 31. قضیهٔ ۶۶: نقل‌قول OLP عمداً بخشی از استدلال را با سه‌نقطه حذف کرده است؛ حذف نشانهٔ نقص ترجمه نیست. تفاوت قلمرو افکار، مجموعهٔ واحد و کثرت اشیا در نقد پس از نقل‌قول حفظ می‌شود.

## وضعیت انتشار

در دامنهٔ ثبت‌شده، تغییر فرمول یا ارجاع فقط با پیش‌تصویر و دلیل صریح مجاز است؛ تفاوت‌های مجاز بالا ثبت شده‌اند و ساختار محیط‌ها و ورودی‌ها حفظ شده است. ساخت خواننده و بازبینی دیداری آن در این نوبت انجام نشد. این گزارش به‌خودی‌خود رسید انتشار نیست. شواهد خصوصیِ فاقد مجوز نباید در بستهٔ عمومی بازنشر شوند.
