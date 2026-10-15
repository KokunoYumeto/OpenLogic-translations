# بازبینی فارسی: دنبالهٔ ساخت، ارزش‌گذاری و مفاهیم معناشناختی

بازخوانی منبع، اصلاح فارسی و ثبت انتخاب‌ها: OpenAI Codex — GPT-6 Astra، کوشش Ultra. این کار بازبینی انسانی نیست.

تمام بندهای سه فایل، شامل تمام شاخه‌های خام، با منبع انگلیسی مقابله شدند. صفحات ۶ و ۷ شاهد خانی–زارعی و ۹ تا ۱۱ درس پورمهدیان–خانی دوباره از تصویر خوانده شدند. گزیدهٔ پایان‌نامهٔ جنگی بهادر فقط از استخراج وب خوانده شد و محدودیت آن جدا ثبت است. این بازبینی پسینی است؛ متن‌های اصلی و اصلاح‌های قبلی حفظ می‌شوند. گواهی کل کتاب یا همهٔ واژه‌ها ادعا نمی‌شود.

## نتیجه

46 بند متن/عنوان ثبت شد. 4 موضع در 4 بند اصلاح شد. نسخه‌های اصلاح‌شده برای ادغام آماده‌اند. این یک بازبینی محدود است، نه گواهی کامل کتاب.

۴: تطبیق مستقیم و شاهد روشن؛ ۳: شاهد مرتبط همراه محدودیت بافتی؛ ۲: شاهد لفظی اختصاصی کافی نیست؛ ۱: تصمیم حل‌نشده. این امتیاز اطمینان تحریری است، نه احتمال کالیبره‌شده. بازبینی انسانی بعدی امکان اصلاح است، نه شرط ادامه.

## انتخاب‌ها و اصلاح‌های مستند

### FA-PL60-SIMILAR-REASONING

در پایان برهان، parallel به تشابه شیوهٔ استدلال اشاره دارد نه موازی‌بودن هندسی. عبارت مشابه با کاربرد واقعی مقایسهٔ روش اثبات در شاهد پایان‌نامه سازگار است؛ تمام حالت‌ها همچنان به استدلال متن واگذار شده‌اند.

پیش از اصلاح:
```latex
استدلالی موازی
```

پس از اصلاح:
```latex
استدلالی مشابه
```

شواهد: J8-SIMILAR, I6-INDUCTIVE.
گزینه‌های کنارگذاشته‌شده: موازی به‌عنوان گرته قابل حدس است ولی در این بافت کمتر روشن است؛ افزودن اثبات حالت‌های دیگر ترجمه نیست. شاهد جدید فقط متنی و با محدودیت استخراج است.
اطمینان تحریری: 3 از ۴.

### FA-PL61-TRUTH-TABLES

جدول‌ها مقادیر صدق صادق/کاذب را نشان می‌دهند؛ صدق همان نوع مقدار معرفی‌شده در تعریف است و عبارت را از جدول ارزش عددی متمایز می‌کند.

پیش از اصلاح:
```latex
جدول‌های ارزش زیر
```

پس از اصلاح:
```latex
جدول‌های ارزش صدق زیر
```

شواهد: MT10-SEMANTICS, J12-VALUATION.
گزینه‌های کنارگذاشته‌شده: جدول درستی نیز ممکن است، ولی در این صفحات شاهد آن نداریم؛ اصطلاح موجود را با توضیح نوع ارزش حفظ می‌کنیم.
اطمینان تحریری: 3 از ۴.

### FA-PL61-TRUTH-TABLE-EXERCISE

همان تصمیم جدول ارزش صدق در تمرین رابط سه‌ورودی نیز اعمال می‌شود؛ هیچ پاسخ یا سطر جدول به تمرین افزوده نمی‌شود.

پیش از اصلاح:
```latex
جدول ارزش این رابط
```

پس از اصلاح:
```latex
جدول ارزش صدق این رابط
```

شواهد: MT10-SEMANTICS, J12-VALUATION.
گزینه‌های کنارگذاشته‌شده: جدول عملکرد از معنای دقیق صدق دورتر است؛ صرفاً تغییر نام به لفظ بی‌شاهد مناسب نیست.
اطمینان تحریری: 3 از ۴.

### FA-PL62-EXERCISE-SYNTAX

منبع یک دستور مستقیم دربارهٔ چهار فرمول می‌دهد. جملهٔ موجود گرته‌ای غیرطبیعی دربارهٔ «چهار مورد» بود. صورت تازه همان تعداد و سه پرسش مستقل را نگه می‌دارد؛ پس از عدد چهار، اسم فارسی مفرد می‌آید و شناسهٔ توکن formula حفظ می‌شود.

پیش از اصلاح:
```latex
!!{formula}s در چهار موردِ زیر آمده‌اند. برای هر یک، جداگانه تعیین کنید که
```

پس از اصلاح:
```latex
برای هر یک از چهار !!{formula} زیر، جداگانه تعیین کنید که
```

شواهد: MT11-SAT, MT9-ATOMIC.
گزینه‌های کنارگذاشته‌شده: حذف عدد یا ادغام سه پرسش پوشش متن را عوض می‌کند؛ افزودن پاسخ تمرین مجاز نیست.
اطمینان تحریری: 4 از ۴.

### PL60-CONSTRUCTION

دنبالهٔ ساخت و استقرا به ساختمان نحوی مربوط‌اند؛ شاخص با طول یکی نیست.

همهٔ وقوع‌ها در تعریف، مثال‌ها، وجود، عکس و اثبات بررسی شدند. اصطلاحات فاقد شاهد مستقیم جدا موقت‌اند.
مواضع بررسی‌شده: OLP-0060-P05, OLP-0060-P06, OLP-0060-P07, OLP-0060-P08, OLP-0060-P09, OLP-0060-P10, OLP-0060-P11, OLP-0060-P12, OLP-0060-P13, OLP-0060-P14, OLP-0060-P15, OLP-0060-P16.
شواهد: I6-INDUCTIVE, MT9-ATOMIC, J8-SIMILAR.
گزینه‌های بررسی‌شده: دنبالهٔ صادق‌بودن، یکتایی دنباله، یا حذف تکرارهای مجاز معنای متن را عوض می‌کند.
اطمینان تحریری: 3 از ۴.

### PL61-VALUATION-EVALUATION

ارزش‌گذاری به متغیرها مقدار می‌دهد؛ ارزش‌یابی آن را به فرمول‌ها گسترش می‌دهد.

کاربرد شاهد گزاره‌ای، دامنه‌های دو تابع و هر وقوعشان مقابله شد. نام‌های فاقد شاهد اختصاصی به‌صراحت موقت‌اند.
مواضع بررسی‌شده: OLP-0061-P05, OLP-0061-P06, OLP-0061-P07, OLP-0061-P09, OLP-0061-P10, OLP-0061-P20.
شواهد: J12-VALUATION, J11-VARIABLES, MT10-SEMANTICS.
گزینه‌های بررسی‌شده: ادغام این دو نام یا ترجمه به ارزیابی آموزشی ساخت معنایی را گم می‌کند.
اطمینان تحریری: 3 از ۴.

### PL61-TRUTH-CONDITIONS

نفی، و/یا، هر دو/هیچ‌کدام و سور هر باید جدا از رشتهٔ نمادها بررسی شوند.

هر شرط با انگلیسی و جدول متن مقابله شد؛ پنهان‌کردن نثر text برای کنترل فرمول جای این بررسی را نمی‌گیرد.
مواضع بررسی‌شده: OLP-0061-P07, OLP-0061-P08, OLP-0061-P09, OLP-0061-P12, OLP-0061-P14, OLP-0061-P15, OLP-0061-P16, OLP-0061-P17, OLP-0061-P18, OLP-0061-P19, OLP-0061-P20.
شواهد: MT10-SEMANTICS, MT11-SAT, J12-VALUATION.
گزینه‌های بررسی‌شده: فصل انحصاری، عکس شرطی یا ارزش‌گذاری متفاوت برای هر عضو مجموعه رد می‌شود.
اطمینان تحریری: 4 از ۴.

### PL62-SEMANTIC-SCOPE

وجود، همگانی‌بودن و اشتراک ارزش‌گذاری مقدمات تعیین‌کننده‌اند.

هر تعریف و کاربرد در تمرین/قضیه به همان دامنهٔ سورها برگشت داده شد؛ ممکن و نام‌های فرامنطقی گواهی کاذب نگرفتند.
مواضع بررسی‌شده: OLP-0062-P05, OLP-0062-P06, OLP-0062-P07, OLP-0062-P08, OLP-0062-P09, OLP-0062-P12, OLP-0062-P15.
شواهد: MT11-SAT, MT10-SEMANTICS, J12-VALUATION.
گزینه‌های بررسی‌شده: possible به معنای satisfiable، جابه‌جایی سورها و تبدیل استلزام به اثبات‌پذیری رد می‌شود.
اطمینان تحریری: 3 از ۴.

## بندهای هم‌تراز برای بازبینی انسانی

متن هر دو طرف، بازهٔ دقیق بایت، شمارهٔ خط و هش در PROPOSITIONAL_0060_0062.json موجود است. تکرارهای یک انتخاب در بافت بند خود بررسی شده‌اند؛ این ثبت جای ادعای بی‌پشتوانهٔ تأیید تک‌تک واژه‌ها را نمی‌گیرد.

### محل ادغام اصلاح‌ها: OLP-0060

همهٔ متن بومی، شامل شاخه‌های غیرفعال، بازبینی شده است. انتخابگر واقعی برچسب‌ها نشان می‌دهد که قطعه‌های انتخاب‌شده دقیقاً با خوانندهٔ منتشرشده برابرند. وصلهٔ بومی و اصلاح قطعه‌های خواننده جدا نگه داشته می‌شوند؛ شاهد قدیمی بازنویسی نمی‌شود.

### صورت‌بندی هم‌معنای موجود؛ نه خطای منبع: OLP-0060

یکسان‌سازی نماد همانی نحوی که از قبل در فارسی وجود داشت؛ نه تغییر قضیه و نه اصلاح تازه
منبع در همین جمله همان فرمول ساخته‌شده از دو جزء را معرفی می‌کند. متن فارسی از ماکروی همانی نحویِ به‌کاررفته در تعریف و حالت‌های مجاور استفاده می‌کند؛ معنای برابری دو رشته حفظ است. اختلاف خام مخفی نشده است.
صورت منبع: `$!A \equiv
(!A_j \land !A_k)$`؛ صورت معادل برای مقایسه: `$!A \ident
(!A_j \land !A_k)$`. شاهد اصلی تغییر نکرده است.

### محل ادغام اصلاح‌ها: OLP-0061

همهٔ متن بومی، شامل شاخه‌های غیرفعال، بازبینی شده است. انتخابگر واقعی برچسب‌ها نشان می‌دهد که قطعه‌های انتخاب‌شده دقیقاً با خوانندهٔ منتشرشده برابرند. وصلهٔ بومی و اصلاح قطعه‌های خواننده جدا نگه داشته می‌شوند؛ شاهد قدیمی بازنویسی نمی‌شود.

### محل ادغام اصلاح‌ها: OLP-0062

همهٔ متن بومی، شامل شاخه‌های غیرفعال، بازبینی شده است. انتخابگر واقعی برچسب‌ها نشان می‌دهد که قطعه‌های انتخاب‌شده دقیقاً با خوانندهٔ منتشرشده برابرند. وصلهٔ بومی و اصلاح قطعه‌های خواننده جدا نگه داشته می‌شوند؛ شاهد قدیمی بازنویسی نمی‌شود.

### OLP-0060-P04

شناسهٔ بخش حفظ شد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olfileid{pl}{syn}{fseq}
```

ترجمهٔ فارسی:
```latex
\olfileid{pl}{syn}{fseq}
```

</details>

### OLP-0060-P05

دنبالهٔ ساخت نام توالیِ مراحل تولید فرمول است؛ عنوان با تعریف بعد مقابله شد.
شواهد: I6-INDUCTIVE, MT9-ATOMIC.
اطمینان تحریری: 2 از ۴.
نیازمند بررسی: برای عین اصطلاح formation sequence در کانن حاضر شاهد مستقیم نداریم؛ معادل تعریف‌محور موجود موقتاً حفظ شد.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olsection{Formation Sequences}
```

ترجمهٔ فارسی:
```latex
\olsection{دنباله‌های ساخت}
```

</details>

### OLP-0060-P06

تعریف استقرایی و اثبات استقرایی دو کار مکمل‌اند؛ رویکرد پایین‌به‌بالا و گام‌به‌گام به ساخت مربوط است، نه محدودیت توان خواننده.
شواهد: I6-INDUCTIVE, MT9-ATOMIC.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: پایین‌به‌بالا شرح روش است، نه اصطلاحی که از این صفحات عیناً نقل شده باشد.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Defining !!{formula}s via an inductive definition, and the
complementary technique of proving properties of !!{formula}s via
induction, is an elegant and efficient approach. However, it can
also be useful to consider a more bottom-up, step-by-step approach
to the construction of !!{formula}s, which we do here using the
notion of a \emph{formation sequence}.
```

ترجمهٔ فارسی:
```latex
تعریف استقراییِ !!{formula}s و فن مکملِ اثبات ویژگی‌های !!{formula}s با
استقرا، رویکردی ظریف و کارآمد است. بااین‌همه، بررسی رویکردی از پایین به بالا
و گام‌به‌گام برای ساخت !!{formula}s نیز می‌تواند سودمند باشد؛ در اینجا این
کار را با استفاده از مفهوم یک \emph{دنبالهٔ ساخت} انجام می‌دهیم.
```

</details>

### OLP-0060-P07

متناهی‌بودن، عضو آخر، شرط همهٔ شاخص‌ها و وجود اجزای پیشین j,k<i جداگانه بررسی شدند. پنج سازنده، حتی شاخه‌های غیرفعال، حفظ‌اند. در حالت نفی شاخص k مصرف نمی‌شود؛ متن اصلی تغییر نکرد.
شواهد: I6-INDUCTIVE, MT9-ATOMIC.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{defn}[Formation sequences for formulas]
\ollabel{defn:fseq-frm}
A finite sequence $\tuple{!A_0,\dotsc,!A_n}$ of strings of
symbols from the language~$\Lang L_0$ is a \emph{formation
sequence} for $!A$ if $!A \ident !A_n$ and for all $i \leq n$,
either $!A_i$ is an atomic formula or there exist $j,k < i$
such that one of the following holds:
\begin{enumerate}
    \tagitem{prvNot}{$!A_i \ident \lnot !A_j$.}{}%
    \tagitem{prvAnd}{$!A_i \ident (!A_j \land !A_k)$.}{}%
    \tagitem{prvOr}{$!A_i \ident (!A_j \lor !A_k)$.}{}%
    \tagitem{prvIf}{$!A_i \ident (!A_j \lif !A_k)$.}{}%
    \tagitem{prvIff}{$!A_i \ident (!A_j \liff !A_k)$.}{}%
\end{enumerate}
\end{defn}
```

ترجمهٔ فارسی:
```latex
\begin{defn}[دنباله‌های ساخت برای فرمول‌ها]
\ollabel{defn:fseq-frm}
دنبالهٔ متناهیِ $\tuple{!A_0,\dotsc,!A_n}$ از رشته‌های نمادهای
زبان~$\Lang L_0$ یک \emph{دنبالهٔ ساخت} برای $!A$ است اگر
$!A \ident !A_n$ و برای هر $i \leq n$، یا $!A_i$ فرمولی اتمی باشد یا
$j,k < i$ وجود داشته باشند، به‌گونه‌ای که یکی از موارد زیر برقرار باشد:
\begin{enumerate}
    \tagitem{prvNot}{$!A_i \ident \lnot !A_j$.}{}%
    \tagitem{prvAnd}{$!A_i \ident (!A_j \land !A_k)$.}{}%
    \tagitem{prvOr}{$!A_i \ident (!A_j \lor !A_k)$.}{}%
    \tagitem{prvIf}{$!A_i \ident (!A_j \lif !A_k)$.}{}%
    \tagitem{prvIff}{$!A_i \ident (!A_j \liff !A_k)$.}{}%
\end{enumerate}
\end{defn}
```

</details>

### OLP-0060-P08

هر دو مثال با ترتیب اعضا بررسی شدند؛ مثال دوم هم تکرار p0 دارد هم شرطی نامؤثر در ساخت فرمول آخر. اجزای زائد به این دو ویژگی اشاره دارد و به فرمول کاذب تعبیر نمی‌شود.
شواهد: I6-INDUCTIVE, MT9-SYNTAX.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: تکراری در این مثال مصداق redundancy است؛ ادعای معادل یگانه و عام آن در همهٔ بافت‌ها نداریم.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{ex}
\[
\tuple{
    \Obj p_0,
    \Obj p_1,
    (\Obj p_1 \land \Obj p_0),
    \lnot (\Obj p_1 \land \Obj p_0)
}
\]
is a formation sequence of
$\lnot (\Obj p_1 \land \Obj p_0)$, as is
\[
\tuple{
    \Obj p_0,
    \Obj p_1,
    \Obj p_0,
    (\Obj p_1 \land \Obj p_0),
    (\Obj p_0 \lif \Obj p_1),
    \lnot (\Obj p_1 \land \Obj p_0)
}.
\]
%
As can be seen from the second example, formation sequences
may contain `junk': formulas which are redundant or do not
contribute to the construction.
\end{ex}
```

ترجمهٔ فارسی:
```latex
\begin{ex}
\[
\tuple{
    \Obj p_0,
    \Obj p_1,
    (\Obj p_1 \land \Obj p_0),
    \lnot (\Obj p_1 \land \Obj p_0)
}
\]
یک دنبالهٔ ساخت برای
$\lnot (\Obj p_1 \land \Obj p_0)$ است؛ دنبالهٔ زیر نیز چنین است:
\[
\tuple{
    \Obj p_0,
    \Obj p_1,
    \Obj p_0,
    (\Obj p_1 \land \Obj p_0),
    (\Obj p_0 \lif \Obj p_1),
    \lnot (\Obj p_1 \land \Obj p_0)
}.
\]
%
چنان‌که از مثال دوم پیداست، دنباله‌های ساخت ممکن است حاوی «اجزای زائد»
باشند: فرمول‌هایی که تکراری‌اند یا در ساخت نقشی ندارند.
\end{ex}
```

</details>

### OLP-0060-P09

هر فرمولِ مجموعهٔ تعیین‌شده دست‌کم یک دنبالهٔ ساخت دارد؛ یکتایی افزوده نشده است.
شواهد: I6-INDUCTIVE, MT9-ATOMIC.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}
\ollabel{prop:formed}
Every !!{formula}~$!A$ in~$\Frm[L_0]$ has a formation sequence.
\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop}
\ollabel{prop:formed}
هر !!{formula}~$!A$ در~$\Frm[L_0]$ دارای یک دنبالهٔ ساخت است.
\end{prop}
```

</details>

### OLP-0060-P10

پایهٔ تک‌عضوی و الحاق دو دنباله در تمام سازنده‌های دوتایی مقابله شدند. تکرار فرمول‌های میانی مجاز است. نتیجه از استقرا بر فرمول می‌آید، نه فرضِ مطلوب.
شواهد: I6-INDUCTIVE, MT9-CONNECTIVES.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
Suppose $!A$ is atomic. Then the sequence~$\tuple{!A}$ is a
formation sequence for~$!A$.
%
Now suppose that $!B$ and~$!C$ have formation sequences
$\tuple{!B_0,\dotsc,!B_n}$ and $\tuple{!C_0,\dotsc,!C_m}$
respectively.
%
\begin{enumerate}
  \tagitem{prvNot}{If $!A \ident \lnot !B$,
      then $\tuple{!B_0,\dotsc,!B_n,\lnot !B_n}$
      is a formation sequence for~$!A$.}{}
  \tagitem{prvAnd}{If $!A \ident (!B \land !C)$,
      then $\tuple{!B_0,\dotsc,!B_n,!C_0,\dotsc,!C_m,(!B_n \land !C_m)}$
      is a formation sequence for~$!A$.}{}
  \tagitem{prvOr}{If $!A \ident (!B \lor !C)$,
      then $\tuple{!B_0,\dotsc,!B_n,!C_0,\dotsc,!C_m,(!B_n \lor !C_m)}$
      is a formation sequence for~$!A$.}{}
  \tagitem{prvIf}{If $!A \ident (!B \lif !C)$,
      then $\tuple{!B_0,\dotsc,!B_n,!C_0,\dotsc,!C_m,(!B_n \lif !C_m)}$
      is a formation sequence for~$!A$.}{}
  \tagitem{prvIff}{If $!A \ident (!B \liff !C)$,
      then $\tuple{!B_0,\dotsc,!B_n,!C_0,\dotsc,!C_m,(!B_n \liff !C_m)}$
      is a formation sequence for~$!A$.}{}
\end{enumerate}
By the principle of induction on !!{formula}s,
every !!{formula} has a formation sequence.
\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
فرض کنید $!A$ اتمی باشد. آنگاه دنبالهٔ~$\tuple{!A}$ یک دنبالهٔ ساخت
برای~$!A$ است.
%
اکنون فرض کنید $!B$ و~$!C$ به‌ترتیب دارای دنباله‌های ساخت
$\tuple{!B_0,\dotsc,!B_n}$ و $\tuple{!C_0,\dotsc,!C_m}$ باشند.
%
\begin{enumerate}
  \tagitem{prvNot}{اگر $!A \ident \lnot !B$،
      آنگاه $\tuple{!B_0,\dotsc,!B_n,\lnot !B_n}$
      یک دنبالهٔ ساخت برای~$!A$ است.}{}
  \tagitem{prvAnd}{اگر $!A \ident (!B \land !C)$،
      آنگاه $\tuple{!B_0,\dotsc,!B_n,!C_0,\dotsc,!C_m,(!B_n \land !C_m)}$
      یک دنبالهٔ ساخت برای~$!A$ است.}{}
  \tagitem{prvOr}{اگر $!A \ident (!B \lor !C)$،
      آنگاه $\tuple{!B_0,\dotsc,!B_n,!C_0,\dotsc,!C_m,(!B_n \lor !C_m)}$
      یک دنبالهٔ ساخت برای~$!A$ است.}{}
  \tagitem{prvIf}{اگر $!A \ident (!B \lif !C)$،
      آنگاه $\tuple{!B_0,\dotsc,!B_n,!C_0,\dotsc,!C_m,(!B_n \lif !C_m)}$
      یک دنبالهٔ ساخت برای~$!A$ است.}{}
  \tagitem{prvIff}{اگر $!A \ident (!B \liff !C)$،
      آنگاه $\tuple{!B_0,\dotsc,!B_n,!C_0,\dotsc,!C_m,(!B_n \liff !C_m)}$
      یک دنبالهٔ ساخت برای~$!A$ است.}{}
\end{enumerate}
بنا بر اصل استقرا بر !!{formula}s،
هر !!{formula} دارای یک دنبالهٔ ساخت است.
\end{proof}
```

</details>

### OLP-0060-P11

عکس، هم‌ارزی دو تعریف و امکان استقرای معمولی بر طول سه گزارهٔ متمایزند. طول در این توضیح عام درست است و با خطای شاخصِ بند آخر خلط نمی‌شود.
شواهد: I6-INDUCTIVE, MT9-ATOMIC.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
We can also prove the converse. This is important because it shows
that our two ways of defining formulas are equivalent: they give
the same results. It also means that we can prove theorems about
formulas by using ordinary induction on the length of formation
sequences.
```

ترجمهٔ فارسی:
```latex
عکس این گزاره را نیز می‌توانیم اثبات کنیم. این امر مهم است، زیرا نشان می‌دهد
دو شیوهٔ ما برای تعریف فرمول‌ها هم‌ارزند: نتایج یکسانی به دست می‌دهند. همچنین
بدین معناست که می‌توانیم قضیه‌های مربوط به فرمول‌ها را با استقرای معمولی بر
طول دنباله‌های ساخت اثبات کنیم.
```

</details>

### OLP-0060-P12

قطعهٔ آغازین تا k، از جمله k=n، دنباله‌ای برای همان عضو Ak است. شرط سره در این لم افزوده نشده است.
شواهد: I6-INDUCTIVE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{lem}
\ollabel{lem:fseq-init}
Suppose that $\tuple{!A_0,\dotsc,!A_n}$ is a formation sequence
for~$!A_n$, and that $k \leq n$. Then $\tuple{!A_0,\dotsc,!A_k}$
is a formation sequence for~$!A_k$.
\end{lem}
```

ترجمهٔ فارسی:
```latex
\begin{lem}
\ollabel{lem:fseq-init}
فرض کنید $\tuple{!A_0,\dotsc,!A_n}$ دنبالهٔ ساختی برای~$!A_n$ باشد و
$k \leq n$. آنگاه $\tuple{!A_0,\dotsc,!A_k}$ دنبالهٔ ساختی
برای~$!A_k$ است.
\end{lem}
```

</details>

### OLP-0060-P13

اثبات عمداً به تمرین واگذار شده؛ متن تمرین نه حذف ترجمه است نه مجوز افزودن برهان.
شواهد: MT11-SAT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
Exercise.
\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
تمرین.
\end{proof}
```

</details>

### OLP-0060-P14

همه و فقط رشته‌های دارای دنبالهٔ ساخت در مجموعهٔ فرمول‌ها هستند؛ نام زبان و مجموعه حفظ‌اند.
شواهد: MT9-ATOMIC, I6-INDUCTIVE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{thm}
\ollabel{thm:fseq-frm-equiv}
$\Frm[L_0]$ is the set of all strings of symbols
in the language~$\Lang L_0$ with a formation sequence.
\end{thm}
```

ترجمهٔ فارسی:
```latex
\begin{thm}
\ollabel{thm:fseq-frm-equiv}
$\Frm[L_0]$ مجموعهٔ همهٔ رشته‌های نمادهای زبان~$\Lang L_0$ است که
دارای دنبالهٔ ساخت‌اند.
\end{thm}
```

</details>

### OLP-0060-P15

F با شرط داشتن دنباله تعریف شده، شمول اثبات‌شده ارجاع داده شده و شمول عکس باقی است. ترتیب دو شمول درست است.
شواهد: I6-INDUCTIVE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
Let $F$ be the set of all strings of symbols in the
language~$\Lang L_0$ that have a formation sequence.
We have seen in \olref[pl][syn][fseq]{prop:formed} that
$\Frm[L_0] \subseteq F$, so now we prove the converse.
```

ترجمهٔ فارسی:
```latex
\begin{proof}
بگذارید $F$ مجموعهٔ همهٔ رشته‌های نمادهای زبان~$\Lang L_0$ باشد که
دارای دنبالهٔ ساخت‌اند. در \olref[pl][syn][fseq]{prop:formed} دیدیم که
$\Frm[L_0] \subseteq F$؛ پس اکنون شمول عکس را اثبات می‌کنیم.
```

</details>

### OLP-0060-P16

استقرای قوی بر n، حالت اتمی و ساخت عطف و ارجاع به لم حفظ‌اند. اصلاح قبلیِ «شاخص پایانی» درست است: دنبالهٔ A0 تا An طول n+1 دارد و پیشوند تا n−1 طول n، نه کمتر از n. ماکروی همانی در فارسی از قبل یکدست شده بود. پایان برهان فقط از موازی به مشابه روان شد.
شواهد: I6-INDUCTIVE, MT9-ATOMIC, J8-SIMILAR.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: برای نام استقرای قوی و قطعهٔ آغازین سره شاهد عین‌عبارتِ مستقل در این صفحات نداریم؛ معنای تعریف و قیود مستقیماً از منبع بررسی شد.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Suppose $!A$ has a formation sequence $\tuple{!A_0,\dotsc,!A_n}$.
We prove that $!A \in \Frm[L_0]$ by strong induction on~$n$.
Our induction hypothesis is that every string of symbols with a
formation sequence of length $m < n$ is in~$\Frm[L_0]$.
By the definition of a formation sequence, either $!A_n$ is
atomic or there must exist $j,k < n$ such that one of the
following is the case:
\begin{enumerate}
    \tagitem{prvNot}{$!A_n \ident \lnot !A_j$.}{}%
    \tagitem{prvAnd}{$!A_n \ident (!A_j \land !A_k)$.}{}%
    \tagitem{prvOr}{$!A_n \ident (!A_j \lor !A_k)$.}{}%
    \tagitem{prvIf}{$!A_n \ident (!A_j \lif !A_k)$.}{}%
    \tagitem{prvIff}{$!A_n \ident (!A_j \liff !A_k)$.}{}%
\end{enumerate}
Now we reason by cases. If $!A_n$ is atomic then
$!A_n \in \Frm[L_0]$. Suppose instead that $!A \equiv
(!A_j \land !A_k)$. By \olref[pl][syn][fseq]{lem:fseq-init},
$\tuple{!A_0,\dotsc,!A_j}$ and $\tuple{!A_0,\dotsc,!A_k}$ are
formation sequences for $!A_j$ and~$!A_k$ respectively. Since
these are proper initial subsequences of the formation sequence
for~$!A$, they both have length less than~$n$. Therefore by
the induction hypothesis, $!A_j$ and~$!A_k$ are in~$\Frm[L_0]$,
and so by the definition of !!a{formula}, so is
$(!A_j \land !A_k)$. The other cases follow by parallel
reasoning.
\end{proof}
```

ترجمهٔ فارسی:
```latex
فرض کنید $!A$ دارای دنبالهٔ ساخت $\tuple{!A_0,\dotsc,!A_n}$ باشد.
اثبات می‌کنیم که $!A \in \Frm[L_0]$؛ این کار را با استقرای قوی
بر~$n$ انجام می‌دهیم.
فرض استقرای ما این است که هر رشته از نمادها که دنبالهٔ ساختی با شاخص پایانی
$m < n$ دارد، در~$\Frm[L_0]$ است. بنا بر تعریف دنبالهٔ ساخت، یا $!A_n$
اتمی است یا باید $j,k < n$ وجود داشته باشند، به‌گونه‌ای که یکی از موارد زیر
برقرار باشد:
\begin{enumerate}
    \tagitem{prvNot}{$!A_n \ident \lnot !A_j$.}{}%
    \tagitem{prvAnd}{$!A_n \ident (!A_j \land !A_k)$.}{}%
    \tagitem{prvOr}{$!A_n \ident (!A_j \lor !A_k)$.}{}%
    \tagitem{prvIf}{$!A_n \ident (!A_j \lif !A_k)$.}{}%
    \tagitem{prvIff}{$!A_n \ident (!A_j \liff !A_k)$.}{}%
\end{enumerate}
اکنون به تفکیک حالت‌ها استدلال می‌کنیم. اگر $!A_n$ اتمی باشد، آنگاه
$!A_n \in \Frm[L_0]$. حال فرض کنید $!A \ident
(!A_j \land !A_k)$. بنا بر \olref[pl][syn][fseq]{lem:fseq-init}،
$\tuple{!A_0,\dotsc,!A_j}$ و $\tuple{!A_0,\dotsc,!A_k}$ به‌ترتیب
دنباله‌های ساختی برای $!A_j$ و~$!A_k$ هستند. چون هر یک قطعهٔ آغازینِ
سره‌ای از دنبالهٔ ساختِ~$!A$ است، شاخص پایانیِ هر دو کوچک‌تر از~$n$ است.
بنابراین، بنا بر فرض استقرا، $!A_j$ و~$!A_k$ در~$\Frm[L_0]$ هستند و
ازاین‌رو، بنا بر تعریف !!a{formula}،
$(!A_j \land !A_k)$ نیز چنین است. حالت‌های دیگر با استدلالی مشابه
به دست می‌آیند.
\end{proof}
```

</details>

### OLP-0061-P04

شناسهٔ بخش حفظ شد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olfileid{pl}{syn}{val}
```

ترجمهٔ فارسی:
```latex
\olfileid{pl}{syn}{val}
```

</details>

### OLP-0061-P05

عنوان ارزش‌گذاری و ارضا دو مفهوم مرتبط اما متمایز را نام می‌برد. شاهد پایان‌نامه در برهان گزاره‌ای خودِ ارزش‌گذاری را به کار می‌برد.
شواهد: J12-VALUATION, MT11-SAT.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: این شاهد استخراج متنی است و PDF محلی یا تصویر آن هنوز نداریم؛ از آن اعتبار کامل نمایه یا همهٔ ترکیب‌ها نتیجه نمی‌شود.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olsection{\usetoken{P}{valuation} and Satisfaction}
```

ترجمهٔ فارسی:
```latex
\olsection{\usetoken{P}{valuation} و ارضا}
```

</details>

### OLP-0061-P06

دو مقدار صدق، دامنهٔ متغیرهای گزاره‌ای و انتساب یکی از آن دو حفظ‌اند. ارزش‌گذاری با تابع ارزش‌یابیِ تعریف بعد خلط نشده است.
شواهد: J12-VALUATION, J11-VARIABLES, MT10-SEMANTICS.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{defn}[!!^{valuation}s]
Let $\{\True, \False\}$ be the set of the two truth values, ``true''
and ``false.'' A \emph{!!{valuation}} for $\Lang{L_0}$ is a
function~$\pAssign{v}$ assigning either $\True$ or $\False$ to the
!!{propositional variable}s of the language, i.e., $\pAssign{v} \colon
\PVar \to \{\True, \False \}$.
\end{defn}
```

ترجمهٔ فارسی:
```latex
\begin{defn}[!!^{valuation}s]
بگذارید $\{\True, \False\}$ مجموعهٔ دو ارزش صدق، یعنی «صادق» و
«کاذب»، باشد.
\emph{!!{valuation}} برای $\Lang{L_0}$ تابعی چون~$\pAssign{v}$ است که
به !!{propositional variable}s زبان یکی از دو مقدار $\True$ یا $\False$
را نسبت می‌دهد؛ یعنی $\pAssign{v} \colon
\PVar \to \{\True, \False \}$.
\end{defn}
```

</details>

### OLP-0061-P07

تمام شرط‌های نثر داخل فرمول جدا خوانده شدند: نفی مقدار را برمی‌گرداند؛ عطف در حالت هر دو صادق، فصل در حالت دست‌کم یکی صادق، شرطی جز در حالت صادق/کاذب، و دوشرطی در حالت تساوی صادق‌اند. و/یا و درغیراین‌صورت حفظ‌اند. تطبیق نمادها به‌تنهایی این نثر را کنترل نمی‌کند.
شواهد: J12-VALUATION, MT10-SEMANTICS, MT9-CONNECTIVES.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: ارزش‌یابی برای evaluation از ارزش‌گذاری برای valuation متمایز مانده است؛ شاهد لفظی مستقیم برای این جفت در منابع حاضر نداریم، ولی دامنه‌های دو تابع صریح‌اند.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{defn}
  Given !!a{valuation}~$\pAssign{v}$, define the evaluation function
  $\pValue{v} \colon \Frm[L_0] \to \{\True, \False \}$ inductively by:
  \begin{align*}
    \iftag{prvFalse}{\pValue{v}(\lfalse) & = \False; \\}{}
    \iftag{prvTrue}{\pValue{v}(\ltrue) & = \True; \\}{}
    \pValue{v}(\Obj p_n) & = \pAssign{v}(\Obj p_n); \\
    \iftag{prvNot}{\pValue{v}(\lnot !A) & = \begin{cases}
        \True & \text{if } \pValue{v}(!A) = \False;\\
        \False & \text{otherwise.}
      \end{cases} \\ }{}
    \iftag{prvAnd}{\pValue{v}(!A \land !B) & = \begin{cases}
        \True &
        \text{if $\pValue{v}(!A) = \True$ and $\pValue{v}(!B) = \True$;}\\
        \False &
        \text{if $\pValue{v}(!A) = \False$ or $\pValue{v}(!B) = \False$}.
      \end{cases}\\}{}
    \iftag{prvOr}{\pValue{v}(!A \lor !B) & = \begin{cases}
        \True &
        \text{if $\pValue{v}(!A) = \True$ or $\pValue{v}(!B) = \True$;}\\
        \False &
        \text{if $\pValue{v}(!A) = \False$ and $\pValue{v}(!B) = \False$}.
      \end{cases}\\}{}
    \iftag{prvIf}{\pValue{v}(!A \lif !B) & = \begin{cases}
        \True &
        \text{if $\pValue{v}(!A) = \False$ or $\pValue{v}(!B) = \True$;}\\
        \False &
        \text{if $\pValue{v}(!A) = \True$ and $\pValue{v}(!B) = \False$}.
      \end{cases}\\}{}
    \iftag{prvIff}{\pValue{v}(!A \liff !B) & = \begin{cases}
        \True &
        \text{if $\pValue{v}(!A) = \pValue{v}(!B)$;}\\
        \False &
        \text{if $\pValue{v}(!A) \neq \pValue{v}(!B)$}.
      \end{cases}}{}
\end{align*}
\end{defn}
```

ترجمهٔ فارسی:
```latex
\begin{defn}
  به‌ازای !!a{valuation}~$\pAssign{v}$، تابع ارزش‌یابی
  $\pValue{v} \colon \Frm[L_0] \to \{\True, \False \}$ را به‌طور
  استقرایی چنین تعریف می‌کنیم:
  \begin{align*}
    \iftag{prvFalse}{\pValue{v}(\lfalse) & = \False; \\}{}
    \iftag{prvTrue}{\pValue{v}(\ltrue) & = \True; \\}{}
    \pValue{v}(\Obj p_n) & = \pAssign{v}(\Obj p_n); \\
    \iftag{prvNot}{\pValue{v}(\lnot !A) & = \begin{cases}
        \True & \text{اگر } \pValue{v}(!A) = \False;\\
        \False & \text{در غیر این صورت.}
      \end{cases} \\ }{}
    \iftag{prvAnd}{\pValue{v}(!A \land !B) & = \begin{cases}
        \True &
        \text{اگر $\pValue{v}(!A) = \True$ و $\pValue{v}(!B) = \True$؛}\\
        \False &
        \text{اگر $\pValue{v}(!A) = \False$ یا $\pValue{v}(!B) = \False$}.
      \end{cases}\\}{}
    \iftag{prvOr}{\pValue{v}(!A \lor !B) & = \begin{cases}
        \True &
        \text{اگر $\pValue{v}(!A) = \True$ یا $\pValue{v}(!B) = \True$؛}\\
        \False &
        \text{اگر $\pValue{v}(!A) = \False$ و $\pValue{v}(!B) = \False$}.
      \end{cases}\\}{}
    \iftag{prvIf}{\pValue{v}(!A \lif !B) & = \begin{cases}
        \True &
        \text{اگر $\pValue{v}(!A) = \False$ یا $\pValue{v}(!B) = \True$؛}\\
        \False &
        \text{اگر $\pValue{v}(!A) = \True$ و $\pValue{v}(!B) = \False$}.
      \end{cases}\\}{}
    \iftag{prvIff}{\pValue{v}(!A \liff !B) & = \begin{cases}
        \True &
        \text{اگر $\pValue{v}(!A) = \pValue{v}(!B)$؛}\\
        \False &
        \text{اگر $\pValue{v}(!A) \neq \pValue{v}(!B)$}.
      \end{cases}}{}
\end{align*}
\end{defn}
```

</details>

### OLP-0061-P08

هر هجده سطر پنج جدول با توابع صدق مقابله شد: نفی دو سطر و چهار رابط دوتایی هر کدام چهار سطر. ترتیب ستون‌ها و شرط نمایش جدول‌ها حفظ است؛ عنوان به ارزش صدق روشن شد.
شواهد: MT9-CONNECTIVES, MT10-SEMANTICS, J12-VALUATION.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{explain}
The clauses correspond to the following truth tables:
\begin{center}
\iftag{prvNot}{
  \begin{tabular}{|c||c|} \hline
    $!A$ & $ \lnot !A$ \\
    \hline \hline
    $\True$ & $\False$ \\
    $\False$ & $\True$ \\
    \hline
  \end{tabular}
}{}
\iftag{prvAnd}{
  \begin{tabular}{|cc||c|} \hline
    $!A$ & $!B$ & $!A \land !B$ \\
    \hline \hline
    $\True$ & $\True$ & $\True$ \\
    $\True$ & $\False$ & $\False$ \\
    $\False$ & $\True$ & $\False$ \\
    $\False$ & $\False$ & $\False$ \\
    \hline
  \end{tabular}
}{}
\iftag{prvOr}{
  \begin{tabular}{|cc||c|} \hline
    $!A$ & $!B$ & $!A \lor !B$ \\
    \hline \hline
    $\True$ & $\True$ & $\True$ \\
    $\True$ & $\False$ & $\True$ \\
    $\False$ & $\True$ & $\True$ \\
    $\False$ & $\False$ & $\False$ \\
    \hline
  \end{tabular}
}{}%
\iftag{notprvNot,notprvAnd,notprvOr,notprvIf}{}{\\[1em]}
\iftag{prvIf}{
  \begin{tabular}{|cc||c|} \hline
    $!A$ & $!B$ & $!A \lif !B$ \\
    \hline \hline
    $\True$ & $\True$ & $\True$ \\
    $\True$ & $\False$ & $\False$ \\
    $\False$ & $\True$ & $\True$ \\
    $\False$ & $\False$ & $\True$ \\
    \hline
  \end{tabular}
}{}
\iftag{prvIff}{
  \begin{tabular}{|cc||c|} \hline
    $!A$ & $!B$ & $!A \liff !B$ \\
    \hline \hline
    $\True$ & $\True$ & $\True$ \\
    $\True$ & $\False$ & $\False$ \\
    $\False$ & $\True$ & $\False$ \\
    $\False$ & $\False$ & $\True$ \\
    \hline
  \end{tabular}
}{}
\end{center}
\end{explain}
```

ترجمهٔ فارسی:
```latex
\begin{explain}
بندها با جدول‌های ارزش صدق زیر متناظرند:
\begin{center}
\iftag{prvNot}{
  \begin{tabular}{|c||c|} \hline
    $!A$ & $ \lnot !A$ \\
    \hline \hline
    $\True$ & $\False$ \\
    $\False$ & $\True$ \\
    \hline
  \end{tabular}
}{}
\iftag{prvAnd}{
  \begin{tabular}{|cc||c|} \hline
    $!A$ & $!B$ & $!A \land !B$ \\
    \hline \hline
    $\True$ & $\True$ & $\True$ \\
    $\True$ & $\False$ & $\False$ \\
    $\False$ & $\True$ & $\False$ \\
    $\False$ & $\False$ & $\False$ \\
    \hline
  \end{tabular}
}{}
\iftag{prvOr}{
  \begin{tabular}{|cc||c|} \hline
    $!A$ & $!B$ & $!A \lor !B$ \\
    \hline \hline
    $\True$ & $\True$ & $\True$ \\
    $\True$ & $\False$ & $\True$ \\
    $\False$ & $\True$ & $\True$ \\
    $\False$ & $\False$ & $\False$ \\
    \hline
  \end{tabular}
}{}%
\iftag{notprvNot,notprvAnd,notprvOr,notprvIf}{}{\\[1em]}
\iftag{prvIf}{
  \begin{tabular}{|cc||c|} \hline
    $!A$ & $!B$ & $!A \lif !B$ \\
    \hline \hline
    $\True$ & $\True$ & $\True$ \\
    $\True$ & $\False$ & $\False$ \\
    $\False$ & $\True$ & $\True$ \\
    $\False$ & $\False$ & $\True$ \\
    \hline
  \end{tabular}
}{}
\iftag{prvIff}{
  \begin{tabular}{|cc||c|} \hline
    $!A$ & $!B$ & $!A \liff !B$ \\
    \hline \hline
    $\True$ & $\True$ & $\True$ \\
    $\True$ & $\False$ & $\False$ \\
    $\False$ & $\True$ & $\False$ \\
    $\False$ & $\False$ & $\True$ \\
    \hline
  \end{tabular}
}{}
\end{center}
\end{explain}
```

</details>

### OLP-0061-P09

رابط سه‌جایگاهی در شاخهٔ صدق A مقدار B و در شاخهٔ کذب A مقدار C را می‌دهد. متن فارسی همین انتخاب را می‌گوید؛ کنترل تازهٔ gather* اکنون کل این عبارت را می‌سنجد، نه فقط فرمول‌های داخل text.
شواهد: MT9-CONNECTIVES, MT10-SEMANTICS, J12-VALUATION.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: سه‌جایگاهی با دوموضعی کانن از حیث تعداد ورودی قابل توضیح است؛ شاهد مستقل عین‌واژهٔ سه‌جایگاهی در صفحات حاضر نیست.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob}
Consider adding to $\Lang{L_0}$ a ternary connective $\diamondsuit$
with evaluation given by
\begin{gather*}
  \pValue{v}(\diamondsuit( !A , !B , !C ) ) = \begin{cases}
    \pValue{v}( !B ) &
    \text{if $\pValue{v}(!A) = \True$;}\\
    \pValue{v}( !C ) &
    \text{if $\pValue{v}(!A) = \False $}.
  \end{cases}
\end{gather*}
Write down the truth table for this connective.
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob}
فرض کنید به $\Lang{L_0}$ رابط سه‌جایگاهیِ $\diamondsuit$ را با
ارزش‌یابیِ زیر بیفزاییم:
\begin{gather*}
  \pValue{v}(\diamondsuit( !A , !B , !C ) ) = \begin{cases}
    \pValue{v}( !B ) &
    \text{اگر $\pValue{v}(!A) = \True$؛}\\
    \pValue{v}( !C ) &
    \text{اگر $\pValue{v}(!A) = \False $}.
  \end{cases}
\end{gather*}
جدول ارزش صدق این رابط را بنویسید.
\end{prob}
```

</details>

### OLP-0061-P10

توافق فقط روی متغیرهای همان A فرض شده و نتیجه فقط مقدار همان A است. واژهٔ همان در فارسی پیش‌تر جای some مبهم را گرفته بود. توکن جمع ارزش‌گذاری‌ها به‌علاوهٔ پسوند یی دقیقاً ارزش‌گذاری‌هایی می‌سازد؛ حذف یک ی اصلاح نیست و انجام نشد.
شواهد: J12-VALUATION, J11-VARIABLES, MT9-ATOMIC.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: نام تعیین موضعی شاهد مستقیم کافی ندارد؛ صورت قضیه معنای نام را روشن می‌کند و موقت حفظ شده است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{thm}[Local Determination]
\ollabel{thm:LocalDetermination} Suppose that $\pAssign{v_1}$ and
$\pAssign{v_2}$ are !!{valuation}s that agree on the !!{propositional
variable}s occurring in $!A$, i.e., $\pAssign{v_1}(\Obj p_n) =
\pAssign{v_2}(\Obj p_n)$ whenever $\Obj p_n$ occurs in some
!!{formula}~$!A$. Then $\pValue{v_1}$ and $\pValue{v_2}$ also agree
on~$!A$, i.e., $\pValue{v_1}(!A) = \pValue{v_2}(!A)$.
\end{thm}
```

ترجمهٔ فارسی:
```latex
\begin{thm}[تعیین موضعی]
\ollabel{thm:LocalDetermination} فرض کنید $\pAssign{v_1}$ و
$\pAssign{v_2}$، !!{valuation}sیی باشند که روی !!{propositional
variable}s رخ‌داده در $!A$ توافق دارند؛ یعنی $\pAssign{v_1}(\Obj p_n) =
\pAssign{v_2}(\Obj p_n)$ هرگاه $\Obj p_n$ در همان
!!{formula}~$!A$ رخ دهد. آنگاه $\pValue{v_1}$ و $\pValue{v_2}$ نیز
روی~$!A$ توافق دارند؛ یعنی $\pValue{v_1}(!A) = \pValue{v_2}(!A)$.
\end{thm}
```

</details>

### OLP-0061-P11

اثبات کوتاه منبع فقط استقرا بر A است؛ همان کوتاهی حفظ شده است.
شواهد: I6-INDUCTIVE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
By induction on $!A$.
\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
با استقرا بر $!A$.
\end{proof}
```

</details>

### OLP-0061-P12

ارضا، نفی ارضا و شرط کذب از هم تفکیک شدند. slash در ماکروی pSat/ خودش نفی است؛ نفی دیگری اضافه نشد.
شواهد: MT10-SEMANTICS, MT11-SAT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{defn}[Satisfaction]
\ollabel{defn:satisfaction} We can inductively define the notion of
  \emph{satisfaction of !!a{formula}~$!A$ by
  !!a{valuation}~$\pAssign{v}$}, $\pSat{v}{!A}$, as follows.
  (We write $\pSat/{v}{!A}$ to mean ``not $\pSat{v}{!A}$.'')
\begin{enumerate}
\tagitem{prvFalse}{%
  \indcase{!A}{\lfalse}{$\pSat/{v}{\indfrm}$.}}{}
```

ترجمهٔ فارسی:
```latex
\begin{defn}[ارضا]
\ollabel{defn:satisfaction} مفهوم
  \emph{ارضا شدنِ !!a{formula}~$!A$ در
  !!a{valuation}~$\pAssign{v}$}، یعنی $\pSat{v}{!A}$، را می‌توانیم
  به‌طور استقرایی به شرح زیر تعریف کنیم.
  (نماد $\pSat/{v}{!A}$ را برای بیان «چنین نیست که
  $\pSat{v}{!A}$» به کار می‌بریم.)
\begin{enumerate}
\tagitem{prvFalse}{%
  \indcase{!A}{\lfalse}{$\pSat/{v}{\indfrm}$.}}{}
```

</details>

### OLP-0061-P13

حالت ثابت صدق و شرط نمایش عیناً محفوظ‌اند.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvTrue}{%
  \indcase{!A}{\ltrue}{$\pSat{v}{\indfrm}$.}}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvTrue}{%
  \indcase{!A}{\ltrue}{$\pSat{v}{\indfrm}$.}}{}
```

</details>

### OLP-0061-P14

ارضا در حالت اتمی اگر و تنها اگر مقدار متغیر صادق باشد؛ دو جهت و شاخص i محفوظ‌اند.
شواهد: J12-VALUATION, MT10-SEMANTICS.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\item \indcase{!A}{\Obj p_i}{$\pSat{v}{\indfrm}$
  iff $\pAssign{v}(\Obj p_i) = \True$.}
```

ترجمهٔ فارسی:
```latex
\item \indcase{!A}{\Obj p_i}{$\pSat{v}{\indfrm}$ اگر و تنها اگر
  $\pAssign{v}(\Obj p_i) = \True$.}
```

</details>

### OLP-0061-P15

ارضا شدن نفی معادل ارضا نشدن جزء است؛ slash و جهت iff حفظ‌اند.
شواهد: MT10-SEMANTICS.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvNot}{%
  \indcase{!A}{\lnot !B}{$\pSat{v}{\indfrm}$ iff
    $\pSat/{v}{!B}$.}}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvNot}{%
  \indcase{!A}{\lnot !B}{$\pSat{v}{\indfrm}$ اگر و تنها اگر
    $\pSat/{v}{!B}$.}}{}
```

</details>

### OLP-0061-P16

عطف مستلزم برقراری هر دو رابطهٔ ارضاست؛ و به یا تبدیل نشده است.
شواهد: MT10-SEMANTICS.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvAnd}{%
  \indcase{!A}{(!B \land !C)}{$\pSat{v}{\indfrm}$ iff $\pSat{v}{!B}$
    and $\pSat{v}{!C}$.}}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvAnd}{%
  \indcase{!A}{(!B \land !C)}{$\pSat{v}{\indfrm}$ اگر و تنها اگر
    $\pSat{v}{!B}$ و $\pSat{v}{!C}$.}}{}
```

</details>

### OLP-0061-P17

فصل شمولی است؛ قید یا هر دو حفظ شده و به فصل انحصاری تبدیل نشده است.
شواهد: MT9-CONNECTIVES, MT10-SEMANTICS.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvOr}{%
  \indcase{!A}{(!B \lor !C)}{$\pSat{v}{\indfrm}$ iff
    $\pSat{v}{!B}$ or $\pSat{v}{!C}$ (or both).}}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvOr}{%
  \indcase{!A}{(!B \lor !C)}{$\pSat{v}{\indfrm}$ اگر و تنها اگر
    $\pSat{v}{!B}$ یا $\pSat{v}{!C}$ (یا هر دو).}}{}
```

</details>

### OLP-0061-P18

شرطی با عدم ارضای مقدم یا ارضای تالی تعریف می‌شود؛ حالت هر دو نیز محفوظ است.
شواهد: MT9-CONNECTIVES, MT10-SEMANTICS.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvIf}{%
  \indcase{!A}{(!B \lif !C)}{$\pSat{v}{\indfrm}$ iff $\pSat/{v}{!B}$
    or $\pSat{v}{!C}$ (or both).}}{}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvIf}{%
  \indcase{!A}{(!B \lif !C)}{$\pSat{v}{\indfrm}$ اگر و تنها اگر
    $\pSat/{v}{!B}$ یا $\pSat{v}{!C}$ (یا هر دو).}}{}
```

</details>

### OLP-0061-P19

دوشرطی یعنی هر دو یا هیچ‌کدام از رابطه‌های ارضا برقرار باشند. در ادامه، یک ارزش‌گذاری باید همهٔ اعضای Gamma را ارضا کند؛ یک ارزش‌گذاری جدا برای هر فرمول کافی نیست. نثر دوشرطی درست است و صرفاً برای ایجاد تغییر بازنویسی نشد.
شواهد: MT10-SEMANTICS, MT11-SAT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\tagitem{prvIff}{%
  \indcase{!A}{(!B \liff !C)}{$\pSat{v}{\indfrm}$ iff either both
    $\pSat{v}{!B}$ and $\pSat{v}{!C}$, or neither $\pSat{v}{!B}$
    nor $\pSat{v}{!C}$.}}{}
\end{enumerate}
If $\Gamma$ is a set of !!{formula}s, $\pSat{v}{\Gamma}$ iff
$\pSat{v}{!A}$ for every~$!A \in \Gamma$.
\end{defn}
```

ترجمهٔ فارسی:
```latex
\tagitem{prvIff}{%
  \indcase{!A}{(!B \liff !C)}{$\pSat{v}{\indfrm}$ اگر و تنها اگر
    یا هر دو رابطهٔ $\pSat{v}{!B}$ و $\pSat{v}{!C}$ برقرار باشند، یا نه
    $\pSat{v}{!B}$ و نه $\pSat{v}{!C}$ برقرار باشد.}}{}
\end{enumerate}
اگر $\Gamma$ مجموعه‌ای از !!{formula}s باشد، $\pSat{v}{\Gamma}$ اگر و
تنها اگر $\pSat{v}{!A}$ برای هر~$!A \in \Gamma$ برقرار باشد.
\end{defn}
```

</details>

### OLP-0061-P20

ارضا و داشتن مقدار صدق True دقیقاً با iff پیوند خورده‌اند؛ نماد انتساب با ارزیابی جابه‌جا نشده است.
شواهد: J12-VALUATION, MT10-SEMANTICS.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}\ollabel{prop:sat-value}
  $\pSat{v}{!A}$ iff $\pValue{v}(!A) = \True$.
\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop}\ollabel{prop:sat-value}
  $\pSat{v}{!A}$ اگر و تنها اگر $\pValue{v}(!A) = \True$.
\end{prop}
```

</details>

### OLP-0061-P21

اثباتِ اعلام‌شده استقرایی است؛ چیزی به آن افزوده یا از آن کاسته نشده است.
شواهد: I6-INDUCTIVE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
  By induction on~$!A$.
\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
  با استقرا بر~$!A$.
\end{proof}
```

</details>

### OLP-0061-P22

ساخت طبیعیِ ارجاع را ثابت کنید درست است و همان ارجاع محفوظ ماند.
شواهد: MT11-SAT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob}
  Prove \olref[pl][syn][val]{prop:sat-value}
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob}
  \olref[pl][syn][val]{prop:sat-value} را ثابت کنید.
\end{prob}
```

</details>

### OLP-0062-P04

شناسهٔ بخش حفظ شد.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olfileid{pl}{syn}{sem}
```

ترجمهٔ فارسی:
```latex
\olfileid{pl}{syn}{sem}
```

</details>

### OLP-0062-P05

معناشناختی ناظر به صدق و ارضاست، نه اثبات‌پذیری؛ عنوان همین مجموعهٔ مفاهیم را پوشش می‌دهد.
شواهد: MT10-SEMANTICS, MT11-SAT.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olsection{Semantic Notions}
```

ترجمهٔ فارسی:
```latex
\olsection{مفاهیم معناشناختی}
```

</details>

### OLP-0062-P06

جملهٔ معرفی تعاریف کوتاه و مستقیم حفظ شد.
شواهد: MT11-SAT.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
We define the following semantic notions:
```

ترجمهٔ فارسی:
```latex
مفاهیم معناشناختی زیر را تعریف می‌کنیم:
```

</details>

### OLP-0062-P07

هر پنج تعریف جدا مقابله شد: ارضاپذیری وجودی، ارضاناپذیری عدم وجود، همان‌گویی همگانی، contingent ارضاپذیر و غیرهمان‌گویی، و استلزام برای تمام ارزش‌گذاری‌های ارضاکنندهٔ مقدمات. در تعریف مجموعه، همان یک ارزش‌گذاری مشترک لازم است. «برای هیچ ... برقرار نباشد» ساخت نفی فارسی است و به برقرار بودن برای همه تبدیل نمی‌شود.
شواهد: MT11-SAT, MT10-SEMANTICS, J12-VALUATION.
اطمینان تحریری: 2 از ۴.
نیازمند بررسی: ممکن برای contingent ممکن است بیرون از تعریف با صرف ارضاپذیری اشتباه شود؛ شاهد اختصاصی کافی برای همین معادل یا جایگزین نداریم. تعریف دقیق آن حفظ و این انتخاب برای بررسی بعدی برجسته شد. همان‌گویی و مستلزم نیز در صفحات حاضر گواهی لفظی کامل ندارند.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{defn} 
\begin{enumerate}
\item !!^a{formula}~$!A$ is \emph{satisfiable} if for
  some~$\pAssign{v}$, $\pSat{v}{!A}$; it is
  \emph{unsatisfiable} if for no $\pAssign{v}$, $\pSat{v}{!A}$;
\item !!^a{formula}~$!A$ is a \emph{tautology} if $\pSat{v}{!A}$ for
  all !!{valuation}s~$\pAssign{v}$;
\item !!^a{formula}~$!A$ is \emph{contingent} if it is satisfiable but
  not a tautology;
\item If $\Gamma$ is a set of !!{formula}s, $\Gamma \Entails !A$ (``$\Gamma$
  entails $!A$'') if and only if $\pSat{v}{!A}$ for every
  !!{valuation}~$\pAssign{v}$ for which $\pSat{v}{\Gamma}$.
\item If $\Gamma$ is a set of !!{formula}s, $\Gamma$ is
  \emph{satisfiable} if there is !!a{valuation}~$\pAssign{v}$ for which
  $\pSat{v}{\Gamma}$, and $\Gamma$ is
  \emph{unsatisfiable} otherwise.
\end{enumerate} 
\end{defn}
```

ترجمهٔ فارسی:
```latex
\begin{defn}
\begin{enumerate}
\item !!^a{formula}~$!A$ \emph{ارضاپذیر} است هرگاه
  برای دست‌کم یک~$\pAssign{v}$، رابطهٔ $\pSat{v}{!A}$ برقرار باشد؛ و
  \emph{ارضاناپذیر} است هرگاه برای هیچ $\pAssign{v}$، رابطهٔ $\pSat{v}{!A}$
  برقرار نباشد؛
\item !!^a{formula}~$!A$ یک \emph{همان‌گویی} است هرگاه
  $\pSat{v}{!A}$ برای همهٔ !!{valuation}s~$\pAssign{v}$ برقرار باشد؛
\item !!^a{formula}~$!A$ را \emph{ممکن} می‌نامیم هرگاه ارضاپذیر باشد،
  اما همان‌گویی نباشد؛
\item اگر $\Gamma$ مجموعه‌ای از !!{formula}s باشد، $\Gamma \Entails !A$
  («$\Gamma$ مستلزم $!A$ است») اگر و تنها اگر رابطهٔ $\pSat{v}{!A}$ برای
  هر !!{valuation}~$\pAssign{v}$ که در آن $\pSat{v}{\Gamma}$ برقرار است،
  برقرار باشد.
\item اگر $\Gamma$ مجموعه‌ای از !!{formula}s باشد، $\Gamma$
  \emph{ارضاپذیر} است هرگاه !!a{valuation}~$\pAssign{v}$ وجود داشته باشد
  که در آن $\pSat{v}{\Gamma}$ برقرار باشد؛ و در غیر این صورت $\Gamma$
  \emph{ارضاناپذیر} است.
\end{enumerate}
\end{defn}
```

</details>

### OLP-0062-P08

دستور تمرین روان شد؛ چهار فرمول با تمام دهانه‌های پرانتز و شرطی‌ها حفظ‌اند. سه پرسش مستقل‌اند و صورت سومی که به contingent اشاره دارد مطابق تعریف همان بخش است.
شواهد: MT11-SAT, MT9-ATOMIC.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: انتخاب ممکن از تعریف قبل به ارث می‌رسد؛ به ممکن به معنای صرفاً ارضاپذیر تفسیر نمی‌شود.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob} 
 For each of the following four !!{formula}s determine whether it
 is (a)~satisfiable, (b)~tautology, and (c)~contingent.
\begin{enumerate}
  \item \( ( \Obj p_0 \lif ( \lnot \Obj p_1 \lif \lnot \Obj p_0 ) ) \).
  \item \( ( ( \Obj p_0 \land \lnot \Obj p_1 ) \lif ( \lnot \Obj p_0 \land \Obj p_2 )) \liff ( ( \Obj p_2 \lif \Obj p_0 ) \lif ( \Obj p_0 \lif \Obj p_1 )) \).
  \item \( ( \Obj p_0 \liff \Obj p_1 ) \lif ( \Obj p_2 \liff \lnot \Obj p_1 ) \).
  \item \( (( \Obj p_0 \liff ( \lnot \Obj p_1 \land \Obj p_2 )) \lor ( \Obj p_2 \lif ( \Obj p_0 \liff \Obj p_1 ))) \).
\end{enumerate}
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob}
 برای هر یک از چهار !!{formula} زیر، جداگانه تعیین کنید که
 (الف)~ارضاپذیر است یا نه، (ب)~همان‌گویی است یا نه، و
 (ج)~ممکن به‌شمار می‌آید یا نه.
\begin{enumerate}
  \item \( ( \Obj p_0 \lif ( \lnot \Obj p_1 \lif \lnot \Obj p_0 ) ) \).
  \item \( ( ( \Obj p_0 \land \lnot \Obj p_1 ) \lif ( \lnot \Obj p_0 \land \Obj p_2 )) \liff ( ( \Obj p_2 \lif \Obj p_0 ) \lif ( \Obj p_0 \lif \Obj p_1 )) \).
  \item \( ( \Obj p_0 \liff \Obj p_1 ) \lif ( \Obj p_2 \liff \lnot \Obj p_1 ) \).
  \item \( (( \Obj p_0 \liff ( \lnot \Obj p_1 \land \Obj p_2 )) \lor ( \Obj p_2 \lif ( \Obj p_0 \liff \Obj p_1 ))) \).
\end{enumerate}
\end{prob}
```

</details>

### OLP-0062-P09

پنج حکم حفظ‌اند: مقدمات تهی، وضع مقدم، زیرمجموعه‌های متناهی، یکنوایی با افزایش مقدمات، و تعدی با اجتماع Gamma و Delta. عکسِ حکم زیرمجموعه‌های متناهی افزوده نشده؛ آن نیازمند نتیجهٔ جداست.
شواهد: MT11-SAT, MT10-SEMANTICS.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: نام یکنوایی در این محل با معنای دقیق شمول مقدمات سنجیده شد؛ صفحات خوانده‌شده شاهد جامع همهٔ نام‌های فرامنطقی نیستند.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}
\ollabel{prop:semanticalfacts} 
\begin{enumerate} 
\item $!A$ is a tautology if and only if
  $\emptyset \Entails !A$; 
\item If $\Gamma \Entails !A$ and $\Gamma \Entails !A \lif !B$ then
  $\Gamma \Entails !B$;
\item If $\Gamma$ is satisfiable then every finite subset of $\Gamma$
  is also satisfiable; 
\item \ollabel{def:monotonicity} Monotonicity: if $\Gamma \subseteq \Delta$
  and $\Gamma \Entails !A$ then also $\Delta \Entails !A$;
\item \ollabel{def:Cut} Transitivity: if $\Gamma \Entails !A$ and
  $\Delta \cup \{ !A\} \Entails !B$ then $\Gamma \cup \Delta \Entails
  !B$.
\end{enumerate}
\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop}
\ollabel{prop:semanticalfacts}
\begin{enumerate}
\item $!A$ همان‌گویی است اگر و تنها اگر
  $\emptyset \Entails !A$؛
\item اگر $\Gamma \Entails !A$ و $\Gamma \Entails !A \lif !B$، آنگاه
  $\Gamma \Entails !B$؛
\item اگر $\Gamma$ ارضاپذیر باشد، هر زیرمجموعهٔ متناهیِ $\Gamma$ نیز
  ارضاپذیر است؛
\item \ollabel{def:monotonicity} یکنوایی: اگر $\Gamma \subseteq \Delta$
  و $\Gamma \Entails !A$، آنگاه $\Delta \Entails !A$ نیز برقرار است؛
\item \ollabel{def:Cut} تعدی: اگر $\Gamma \Entails !A$ و
  $\Delta \cup \{ !A\} \Entails !B$، آنگاه $\Gamma \cup \Delta \Entails
  !B$ برقرار است.
\end{enumerate}
\end{prop}
```

</details>

### OLP-0062-P10

واگذاری اثبات به تمرین عیناً حفظ شد.
شواهد: MT11-SAT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
Exercise.
\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
تمرین.
\end{proof}
```

</details>

### OLP-0062-P11

دستور تمرین با همان ارجاع درست است؛ تغییر بی‌دلیل لازم نیست.
شواهد: MT11-SAT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob}
Prove \olref[pl][syn][sem]{prop:semanticalfacts}
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob}
\olref[pl][syn][sem]{prop:semanticalfacts} را ثابت کنید.
\end{prob}
```

</details>

### OLP-0062-P12

استلزام معادل ارضاناپذیری Gamma به همراه نفی A است؛ عدم ارضا و ارضاناپذیری یکسان‌سازی نشده‌اند.
شواهد: MT11-SAT, MT10-SEMANTICS.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}\ollabel{prop:entails-unsat}
  $\Gamma \Entails !A$ if and only if $\Gamma \cup \{\lnot !A\}$
  is unsatisfiable.
\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop}\ollabel{prop:entails-unsat}
  $\Gamma \Entails !A$ اگر و تنها اگر $\Gamma \cup \{\lnot !A\}$
  ارضاناپذیر باشد.
\end{prop}
```

</details>

### OLP-0062-P13

علامت تمرینِ اثبات حفظ شد.
شواهد: MT11-SAT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
Exercise.
\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
تمرین.
\end{proof}
```

</details>

### OLP-0062-P14

همان گزاره باید اثبات شود و ارجاع حفظ است.
شواهد: MT11-SAT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob}
Prove \olref[pl][syn][sem]{prop:entails-unsat}
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob}
\olref[pl][syn][sem]{prop:entails-unsat} را ثابت کنید.
\end{prob}
```

</details>

### OLP-0062-P15

قضیهٔ استنتاج معنایی دربارهٔ استلزام است، نه دستگاه اشتقاق؛ جابه‌جایی A میان مقدمات و مقدم شرطی و هر دو جهت iff دقیقاً حفظ‌اند.
شواهد: MT10-SEMANTICS, MT11-SAT.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: نام فارسی این قضیه در صفحات فعلی شاهد اختصاصی ندارد؛ صورت معنایی و شرح آن مبنای حفظ موقت است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{thm}[Semantic Deduction Theorem]
  \ollabel{thm:sem-deduction} $\Gamma \Entails !A \lif !B$ if and only
  if $\Gamma \cup \{!A\} \Entails !B$.
\end{thm}
```

ترجمهٔ فارسی:
```latex
\begin{thm}[قضیهٔ استنتاج معنایی]
  \ollabel{thm:sem-deduction} $\Gamma \Entails !A \lif !B$ اگر و تنها
  اگر $\Gamma \cup \{!A\} \Entails !B$.
\end{thm}
```

</details>

### OLP-0062-P16

اثبات به تمرین واگذار شده و متنی از مترجم جای آن ننشسته است.
شواهد: MT11-SAT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
Exercise.
\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
تمرین.
\end{proof}
```

</details>

### OLP-0062-P17

ارجاع قضیه و دستور اثبات حفظ‌اند.
شواهد: MT11-SAT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob}
Prove \olref[pl][syn][sem]{thm:sem-deduction}
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob}
\olref[pl][syn][sem]{thm:sem-deduction} را ثابت کنید.
\end{prob}
```

</details>

## یافته‌های تکمیلی و حدود بازبینی

۴ اصلاح نثر و یک بررسی کامل ۴۶ بندی انجام شد. عبارت جمعِ ارزش‌گذاری‌هایی درست بود و تغییر نکرد. اصلاح پیشینِ شاخص پایانی در برهان دنبالهٔ ساخت حفظ شد. ۱۸ سطر جدول صدق، شاخه‌های رابط سه‌ورودی، و تمام شرط‌های ارضا جداگانه بررسی شدند. شاهد جدید پایان‌نامه فقط استخراج متنی است و هش PDF یا بازبینی تصویری آن ادعا نمی‌شود.
 
## منابع و حدود استناد

### IUTLOG

محسن خانی و افشین زارعی، نظریهٔ مجموعه‌ها، ۱۴۰۰؛ پیش‌نیازهای منطقی

https://khani.iut.ac.ir/sites/khani.iut.ac.ir/files/u145/jozve-kamel.pdf

نسخهٔ دانشگاهی برای مطالعهٔ محلی؛ بازنشر عمومی PDF مجاز فرض نشده و فقط نقل‌های کوتاه و ارجاع منتشر می‌شوند.

### MT

مسعود پورمهدیان و محسن خانی، مباحثی در منطق، دانشگاه صنعتی امیرکبیر، ۱۵ بهمن ۱۳۹۵؛ جلسهٔ مقدماتی

https://mohsen-khani.github.io/modeltheory/jozve1.pdf

نسخهٔ نویسندگان در صفحهٔ دوره؛ سند فارسیِ منطق مرتبهٔ اول است، نه شاهد اختصاصی همهٔ اصطلاح‌های منطق گزاره‌ای. فقط مطالعهٔ محلی، نقل کوتاه و ارجاع؛ PDF در انتشار عمومی قرار نمی‌گیرد.

### JANGI_WEB

نیر جنگی بهادر، یک قضیه درونیابی در منطق مرتبه اول، دانشگاه تبریز، پایان‌نامهٔ کارشناسی ارشد منطق ریاضی؛ سال ۱۳۹۰ در جلد و مشخصات

https://saeedsalehi.ir/pdf/thesis/MSc%20Thesis%20--%20Nayyer%20JangiBahador.pdf

۱۳ واژهٔ نقل کوتاه برای ثبت شاهد؛ متن کامل پایان‌نامه بازنشر نمی‌شود. نشانی نسخهٔ میزبان استاد راهنما حفظ شده است. مجوز بازنشر PDF فرض نشده است.

- MT9-SYNTAX: «نحو»؛ صفحهٔ فایل 9، چاپی 9. عنوان نحو و پانوشت syntax؛ نماد، متغیر، پرانتز باز و بسته و تعریف فرمول در همان صفحه خوانده شد. شاهدی برای نحو است، نه گواهی خودکار تمام معادل‌های متن.
- MT9-CONNECTIVES: «ادوات بولی یا گزاره‌ای»؛ صفحهٔ فایل 9، چاپی 9. پنج رابط گزاره‌ای در بافت صوری معرفی می‌شوند. رابط در ترجمه از ادوات در این شاهد متفاوت است؛ معنای آن با فهرست نمادها و شرح منبع سنجیده شد و انحصار یک معادل ادعا نمی‌شود.
- MT9-ATOMIC: «فرمولهای بسیط (یا اتمیک)»؛ صفحهٔ فایل 9، چاپی 9. تعریف ۱۱ و ادامهٔ آن در صفحهٔ ۱۰ مبنای مقابلهٔ حالت پایه، ساخت استقرایی و شرط انحصارند. این شاهد، فرمول اتمی را از متغیر تنها و جملهٔ بدون متغیر آزاد متمایز می‌کند.
- MT10-SEMANTICS: «به صورت استقرایی»؛ صفحهٔ فایل 10، چاپی 10. تعریف صدق در ساختار و شروط نفی و عطف واقعاً خوانده شد؛ نثر نسبت‌دادن معنا و ساختار استقرایی را پشتیبانی می‌کند. ارزش‌گذاری گزاره‌ای با تعبیر مرتبهٔ اول یکی نیست و از این شاهد چنین همانی‌ای نتیجه نمی‌شود.
- MT11-SAT: «ارضاشدنی»؛ صفحهٔ فایل 11، چاپی 11. تعریف ارضاشدنی با وجود مدل برای تمام جمله‌های نظریه و پانوشت satisfiable؛ در ترجمه ارضاپذیر حفظ شد. تمایز وجود یک ارزش‌گذاری مشترک با ارزش‌گذاری جدا برای هر فرمول بررسی شد.
- I6-INDUCTIVE: «روش استقرایی»؛ صفحهٔ فایل 6، چاپی 5. تعریف ۱، حالت‌های پایه و ساخت عطف؛ نحو جمله‌های شرطی فارسی و اصطلاح فرمول در متن تخصصی شاهد دارند. تعریف مرتبهٔ اول جایگزین تعریف گزاره‌ای OLP نمی‌شود.
- I7-FREE: «متغیر آزاد»؛ صفحهٔ فایل 7، چاپی 6. ادامهٔ ساخت فرمول با نفی و سور، محدودبودن ساخت به مراحل متناهی، و تعریف جمله خوانده شد. در این فصل سورها جزو زبان گزاره‌ای نیستند؛ استفادهٔ ما اصطلاحی و روشی است.
- I7-CLASS: «رده‌ای»؛ صفحهٔ فایل 7، چاپی 6. تعریف مجموعه در پایان صفحه نمونهٔ کاربرد رده در نثر ریاضی است. این شاهد صرفاً انتخاب واژه و ساخت فارسی را پشتیبانی می‌کند؛ استدلال کمینگی از خود OLP بررسی شد.
- J8-SIMILAR: «بطرز خیلͬ مشابهای اثبات شود»؛ صفحهٔ فایل 9، چاپی 4. مقدمه، مقایسهٔ اثبات نتیجه‌ای دربارهٔ تعریف‌پذیری با استدلال قبلی؛ فقط شاهد کاربرد مشابه در توصیف روش اثبات.
- J11-VARIABLES: «متغیرهای گزارهای»؛ صفحهٔ فایل 12، چاپی 7. بخش درونیابی منطق گزاره‌ها؛ مجموعهٔ متغیرهای ظاهرشده در فرمول در صورت قضیه معرفی می‌شود.
- J12-VALUATION: «برای هر ارزشͽذاری»؛ صفحهٔ فایل 13، چاپی 8. برهان درونیابی منطق گزاره‌ها با ارزش‌گذاری V و دو تغییر آن در یک متغیر p؛ معنای واژه انتساب مقدار صدق است، نه ارزیابی آموزشی.
- J12-SUBSTITUTION: «جانشین مͬشود»؛ صفحهٔ فایل 13، چاپی 8. توضیح جایگزینی ثابت صدق یا کذب به جای p؛ شاهد جانشینی در متن صوری، نه مجوز تعمیم به همهٔ قراردادهای OLP.

## وضعیت انتشار

در دامنهٔ ثبت‌شده، تغییر فرمول یا ارجاع فقط با پیش‌تصویر و دلیل صریح مجاز است؛ تفاوت‌های مجاز بالا ثبت شده‌اند و ساختار محیط‌ها و ورودی‌ها حفظ شده است. ساخت خواننده و بازبینی دیداری آن در این نوبت انجام نشد. این گزارش به‌خودی‌خود رسید انتشار نیست. شواهد خصوصیِ فاقد مجوز نباید در بستهٔ عمومی بازنشر شوند.
