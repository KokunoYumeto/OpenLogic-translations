# بازبینی فارسی: مثال‌های حساب رشته و تعریف‌های اشتقاق‌پذیری و سازگاری

بازخوانی منبع، اصلاح فارسی و ثبت انتخاب‌ها: OpenAI Codex — GPT-6 Astra، کوشش Ultra. این کار بازبینی انسانی نیست.

چهار فایل ۰۰۷۵ تا ۰۰۷۸ به‌طور کامل با انگلیسی تثبیت‌شده و قطعه‌های واقعی خواننده مقابله شدند؛ ۰۰۷۶ فقط بافت مرتبهٔ اول دارد. همهٔ نمایش‌های نمونه‌برهان و فرمول تمرین‌ها تطبیق یافتند؛ این کار ادعای حل دوبارهٔ همهٔ تمرین‌ها یا اثبات مستقل ضرورت انقباض برای تک‌تک آن‌ها نیست. کانن فارسی همان مقالهٔ حسینی و درس نظریهٔ مدل است؛ صفحات ۲۳۴ و ۲۳۶ و صفحهٔ ۱۱ درس مدل دوباره از تصویر خوانده شدند و مواضع دقیقِ پیش‌تر خوانده‌شده برای نحو و قواعد نیز هنگام تصمیم مراجعه شدند. مقالهٔ ابتنا شاهد زبان است، نه مرجع جایگزین برای قواعد کلاسیک. بازبینی پسینی و محدود به همین چهار واحد است.

## نتیجه

59 بند متن/عنوان ثبت شد. 48 موضع در 25 بند اصلاح شد. نسخه‌های اصلاح‌شده برای ادغام آماده‌اند. این یک بازبینی محدود است، نه گواهی کامل کتاب.

۴: تطبیق مستقیم و شاهد روشن؛ ۳: شاهد مرتبط همراه محدودیت بافتی؛ ۲: شاهد لفظی اختصاصی کافی نیست؛ ۱: تصمیم حل‌نشده. این امتیاز اطمینان تحریری است، نه احتمال کالیبره‌شده. بازبینی انسانی بعدی امکان اصلاح است، نه شرط ادامه.

## انتخاب‌ها و اصلاح‌های مستند

### FA-SEQ75-SEQUENT

هر وقوع نام sequent در تعریف، نثر نمونه‌برهان و صورت تمرین بررسی و با رشته یکدست شد؛ sequence در این فایل‌ها با این واژه بیان نشده است.

پیش از اصلاح:
```latex
دنباله
```

پس از اصلاح:
```latex
رشته
```

شواهد: H14-SEQUENT, H17-TREE.
گزینه‌های کنارگذاشته‌شده: این تغییر به فایل‌های بررسی‌نشده تعمیم نمی‌یابد؛ توالی نام فهرستِ جمله‌ها باقی می‌ماند.
اطمینان تحریری: 3 از ۴.

### FA-SEQ75-EXCHANGE-POSITION

outside در این نمونه یعنی ابتدای فهرست مقدم تا قاعدهٔ فصلِ چپ قابل اعمال شود، نه بیرونِ رشته.

پیش از اصلاح:
```latex
بیرونی‌ترین جای مقدم
```

پس از اصلاح:
```latex
منتهی‌الیه چپِ مقدم
```

شواهد: H17-TREE, H14-SEQUENT.
گزینه‌های کنارگذاشته‌شده: بیرونی‌ترین جای بدون تعیین جهت مبهم است؛ حرکت به طرف راست علامت رشته نادرست است.
اطمینان تحریری: 3 از ۴.

### FA-SEQ75-MISSING-NEGATIONS

در مثال سوم هدف از آغاز نقیض A یا نقیض B است. اعمال عطف چپ فقط A∧B را به A یا B تبدیل می‌کند و حق حذف نفی B از جملهٔ دیگر را ندارد. هر دو درختِ مجاور همان نفی را دارند؛ دو وقوعِ نثر منبع و فارسی نفی را انداخته‌اند.

پیش از اصلاح:
```latex
\lnot !A \lor !B \Sequent \quad
```

پس از اصلاح:
```latex
\lnot !A \lor \lnot !B \Sequent \quad
```

شواهد: MT9-CONNECTIVES, H17-TREE.
گزینه‌های کنارگذاشته‌شده: نگه‌داشتن !B مثبت، مقدمهٔ مسئله را تغییر می‌دهد؛ این افزودن مطلب یا تغییر راه‌حل نیست.
اطمینان تحریری: 4 از ۴.

### FA-SEQ76-SEQUENT

هر وقوع نام sequent در تعریف، نثر نمونه‌برهان و صورت تمرین بررسی و با رشته یکدست شد؛ sequence در این فایل‌ها با این واژه بیان نشده است.

پیش از اصلاح:
```latex
دنباله
```

پس از اصلاح:
```latex
رشته
```

شواهد: H14-SEQUENT, H17-TREE.
گزینه‌های کنارگذاشته‌شده: این تغییر به فایل‌های بررسی‌نشده تعمیم نمی‌یابد؛ توالی نام فهرستِ جمله‌ها باقی می‌ماند.
اطمینان تحریری: 3 از ۴.

### FA-SEQ76-SCHEMA-NOT-EVERY-INSTANCE

بحث دربارهٔ شِمای دلخواه A و دو ثابت است؛ بعضی نمونه‌های خاص، مانند A مستقل از متغیر، ممکن است اشتقاق‌پذیر باشند. در حالت کلی همان مقصود مثال را دقیق می‌کند.

پیش از اصلاح:
```latex
می‌رسیدیم که البته اشتقاق‌پذیر نیست.
```

پس از اصلاح:
```latex
می‌رسیدیم که در حالت کلی اشتقاق‌پذیر نیست.
```

شواهد: MT10-FREE-BOUND, H17-TREE.
گزینه‌های کنارگذاشته‌شده: خوانش هیچ نمونه‌ای اشتقاق‌پذیر نیست از استدلال منبع نتیجه نمی‌شود.
اطمینان تحریری: 3 از ۴.

### FA-SEQ77-P04

نام حساب با عنوان فصل یکدست شد؛ فارسی از قبل خطای کپیِ natural deduction را در یادداشت انگلیسی اصلاح کرده بود.

پیش از اصلاح:
```latex
\begin{editorial}
  این بخش تعریف‌های رابطهٔ اثبات‌پذیری و سازگاری را برای حساب دنباله‌ای
  گرد می‌آورد.
\end{editorial}
```

پس از اصلاح:
```latex
\begin{editorial}
  این بخش تعریف‌های رابطهٔ اثبات‌پذیری و سازگاری را برای حساب رشته
  گرد می‌آورد.
\end{editorial}
```

شواهد: H14-SEQUENT.
گزینه‌های کنارگذاشته‌شده: استنتاج طبیعی و LK یک دستگاه نیستند؛ اصلاح قدیمی به عنوان یافتهٔ تازه شمرده نمی‌شود.
اطمینان تحریری: 3 از ۴.

### FA-SEQ77-SEMANTIC-CONTRAST

نام شیء نحوی عوض شد؛ در شاخهٔ PL ارزش‌گذاری و در FOL ساختار حفظ شده‌اند.

پیش از اصلاح:
```latex
برخی دنباله‌ها
```

پس از اصلاح:
```latex
برخی رشته‌ها
```

شواهد: MT11-SAT, H16-COMPLETE, H14-SEQUENT.
گزینه‌های کنارگذاشته‌شده: ارضاشدن و اشتقاق‌پذیری نباید مترادف تعریف شوند؛ هم‌ارزیِ قضیه بعدی نتیجه است نه تعریف.
اطمینان تحریری: 3 از ۴.

### FA-SEQ77-P08

تمام وقوع‌های رشته در این بند با تعریف کتاب و صورت نمادین مقابله شدند؛ توالی Γ0 و قواعد ساختاری عوض نشده‌اند.

پیش از اصلاح:
```latex
\begin{defn}[قضایا]
!!^a{sentence}~$!A$ \emph{قضیه} است هرگاه در~$\Log{LK}$،
!!a{derivation}ی برای دنبالهٔ $\quad \Sequent !A$ وجود داشته باشد.
$\Proves !A$ می‌نویسیم اگر $!A$ قضیه باشد، و اگر قضیه نباشد
$\Proves/ !A$ می‌نویسیم.
\end{defn}
```

پس از اصلاح:
```latex
\begin{defn}[قضایا]
!!^a{sentence}~$!A$ \emph{قضیه} است هرگاه در~$\Log{LK}$،
!!a{derivation}ی برای رشتهٔ $\quad \Sequent !A$ وجود داشته باشد.
$\Proves !A$ می‌نویسیم اگر $!A$ قضیه باشد، و اگر قضیه نباشد
$\Proves/ !A$ می‌نویسیم.
\end{defn}
```

شواهد: H14-SEQUENT, H17-TREE.
گزینه‌های کنارگذاشته‌شده: مجموعهٔ مقدمات می‌تواند نامتناهی باشد ولی هر شاهد اشتقاق تنها از زیرمجموعه‌ای متناهی استفاده می‌کند.
اطمینان تحریری: 3 از ۴.

### FA-SEQ77-P10

تمام وقوع‌های رشته در این بند با تعریف کتاب و صورت نمادین مقابله شدند؛ توالی Γ0 و قواعد ساختاری عوض نشده‌اند.

پیش از اصلاح:
```latex
به سبب قواعد انقباض، تضعیف و تبادل، ترتیب و شمار !!{sentence}s در
~$\Gamma_0'$ اهمیتی ندارد: اگر دنبالهٔ
$\Gamma_0' \Sequent !A$ !!{derivable} باشد، آنگاه
$\Gamma_0'' \Sequent !A$ نیز برای هر $\Gamma_0''$ که همان
!!{sentence}s موجود در~$\Gamma_0'$ را دربر دارد چنین است.
برای نمونه، اگر $\Gamma_0 = \{!B, !C\}$ باشد، آنگاه هم
$\Gamma_0' = \tuple{!B, !B, !C}$ و هم
$\Gamma_0'' = \tuple{!C, !C, !B}$ توالی‌هایی‌اند که دقیقاً
!!{sentence}s موجود در~$\Gamma_0$ را دربر دارند. اگر دنباله‌ای که
یکی از آن‌ها را دربر دارد !!{derivable} باشد، دنبالهٔ دیگر نیز چنین
است؛ برای نمونه:
\begin{prooftree}
  \AxiomC{}
  \Deduce$!B, !B, !C \fCenter !A$
  \RightLabel{\LeftR{\Contraction}}
  \UnaryInf$!B, !C \fCenter !A$
  \RightLabel{\LeftR{\Exchange}}
  \UnaryInf$!C, !B \fCenter !A$
  \RightLabel{\LeftR{\Weakening}}
  \UnaryInf$!C, !C, !B \fCenter !A$
\end{prooftree}
از این پس می‌گوییم اگر $\Gamma_0$ مجموعه‌ای متناهی از !!{sentence}s
باشد، آنگاه $\Gamma_0 \Sequent !A$ هر دنباله‌ای است که مقدمش توالی‌ای
از !!{sentence}s موجود در~$\Gamma_0$ باشد؛ و در صورت لزوم انقباض‌ها،
تبادل‌ها و تضعیف‌ها را به‌طور ضمنی منظور می‌کنیم.
```

پس از اصلاح:
```latex
به سبب قواعد انقباض، تضعیف و تبادل، ترتیب و شمار !!{sentence}s در
~$\Gamma_0'$ اهمیتی ندارد: اگر رشتهٔ
$\Gamma_0' \Sequent !A$ !!{derivable} باشد، آنگاه
$\Gamma_0'' \Sequent !A$ نیز برای هر $\Gamma_0''$ که همان
!!{sentence}s موجود در~$\Gamma_0'$ را دربر دارد چنین است.
برای نمونه، اگر $\Gamma_0 = \{!B, !C\}$ باشد، آنگاه هم
$\Gamma_0' = \tuple{!B, !B, !C}$ و هم
$\Gamma_0'' = \tuple{!C, !C, !B}$ توالی‌هایی‌اند که دقیقاً
!!{sentence}s موجود در~$\Gamma_0$ را دربر دارند. اگر رشته‌ای که
یکی از آن‌ها را دربر دارد !!{derivable} باشد، رشتهٔ دیگر نیز چنین
است؛ برای نمونه:
\begin{prooftree}
  \AxiomC{}
  \Deduce$!B, !B, !C \fCenter !A$
  \RightLabel{\LeftR{\Contraction}}
  \UnaryInf$!B, !C \fCenter !A$
  \RightLabel{\LeftR{\Exchange}}
  \UnaryInf$!C, !B \fCenter !A$
  \RightLabel{\LeftR{\Weakening}}
  \UnaryInf$!C, !C, !B \fCenter !A$
\end{prooftree}
از این پس می‌گوییم اگر $\Gamma_0$ مجموعه‌ای متناهی از !!{sentence}s
باشد، آنگاه $\Gamma_0 \Sequent !A$ هر رشته‌ای است که مقدمش توالی‌ای
از !!{sentence}s موجود در~$\Gamma_0$ باشد؛ و در صورت لزوم انقباض‌ها،
تبادل‌ها و تضعیف‌ها را به‌طور ضمنی منظور می‌کنیم.
```

شواهد: H14-SEQUENT, H17-TREE.
گزینه‌های کنارگذاشته‌شده: مجموعهٔ مقدمات می‌تواند نامتناهی باشد ولی هر شاهد اشتقاق تنها از زیرمجموعه‌ای متناهی استفاده می‌کند.
اطمینان تحریری: 3 از ۴.

### FA-SEQ77-P13

تمام وقوع‌های رشته در این بند با تعریف کتاب و صورت نمادین مقابله شدند؛ توالی Γ0 و قواعد ساختاری عوض نشده‌اند.

پیش از اصلاح:
```latex
\begin{proof}
دنبالهٔ آغازینِ $!A \Sequent !A$ !!{derivable} است و
$\{!A\} \subseteq \Gamma$.
\end{proof}
```

پس از اصلاح:
```latex
\begin{proof}
رشتهٔ آغازینِ $!A \Sequent !A$ !!{derivable} است و
$\{!A\} \subseteq \Gamma$.
\end{proof}
```

شواهد: H14-SEQUENT, H17-TREE.
گزینه‌های کنارگذاشته‌شده: مجموعهٔ مقدمات می‌تواند نامتناهی باشد ولی هر شاهد اشتقاق تنها از زیرمجموعه‌ای متناهی استفاده می‌کند.
اطمینان تحریری: 3 از ۴.

### FA-SEQ77-P23

تمام وقوع‌های رشته در این بند با تعریف کتاب و صورت نمادین مقابله شدند؛ توالی Γ0 و قواعد ساختاری عوض نشده‌اند.

پیش از اصلاح:
```latex
\begin{proof}
  \begin{enumerate}
    \item اگر $\Gamma \Proves !A$، آنگاه زیرمجموعهٔ متناهی
      $\Gamma_0 \subseteq \Gamma$ وجود دارد که دنبالهٔ
      $\Gamma_0 \Sequent !A$ دارای !!a{derivation} است. در نتیجه،
      $\Gamma_0 \Proves !A$.
    \item اگر $\Gamma$ ناسازگار باشد، زیرمجموعهٔ متناهی
      ~$\Gamma_0 \subseteq \Gamma$ وجود دارد که $\Log{LK}$،
      $\Gamma_0 \Sequent \quad$ را !!{derive}s می‌کند. اما در این صورت،
      $\Gamma_0$ زیرمجموعه‌ای متناهی و ناسازگار از~$\Gamma$ است.
  \end{enumerate}
\end{proof}
```

پس از اصلاح:
```latex
\begin{proof}
  \begin{enumerate}
    \item اگر $\Gamma \Proves !A$، آنگاه زیرمجموعهٔ متناهی
      $\Gamma_0 \subseteq \Gamma$ وجود دارد که رشتهٔ
      $\Gamma_0 \Sequent !A$ دارای !!a{derivation} است. در نتیجه،
      $\Gamma_0 \Proves !A$.
    \item اگر $\Gamma$ ناسازگار باشد، زیرمجموعهٔ متناهی
      ~$\Gamma_0 \subseteq \Gamma$ وجود دارد که $\Log{LK}$،
      $\Gamma_0 \Sequent \quad$ را !!{derive}s می‌کند. اما در این صورت،
      $\Gamma_0$ زیرمجموعه‌ای متناهی و ناسازگار از~$\Gamma$ است.
  \end{enumerate}
\end{proof}
```

شواهد: H14-SEQUENT, H17-TREE.
گزینه‌های کنارگذاشته‌شده: مجموعهٔ مقدمات می‌تواند نامتناهی باشد ولی هر شاهد اشتقاق تنها از زیرمجموعه‌ای متناهی استفاده می‌کند.
اطمینان تحریری: 3 از ۴.

### FA-SEQ78-SEQUENT

هر وقوع نام sequent در تعریف، نثر نمونه‌برهان و صورت تمرین بررسی و با رشته یکدست شد؛ sequence در این فایل‌ها با این واژه بیان نشده است.

پیش از اصلاح:
```latex
دنباله
```

پس از اصلاح:
```latex
رشته
```

شواهد: H14-SEQUENT, H17-TREE.
گزینه‌های کنارگذاشته‌شده: این تغییر به فایل‌های بررسی‌نشده تعمیم نمی‌یابد؛ توالی نام فهرستِ جمله‌ها باقی می‌ماند.
اطمینان تحریری: 3 از ۴.

### FA-SEQ78-FINITE-P11

Γ در قضیه مجموعهٔ دلخواه است، اما طبق تعریف ۰۰۷۰ دو طرف رشته متناهی‌اند و طبق ۰۰۷۷ رابطهٔ اشتقاق از Γ با شاهد Γ0 متناهی تعریف می‌شود. نوشتن Γ⇒A برای Γ دلخواه در دو بند برهان از این قرارداد بیرون است. Γ0⊆Γ و گواه متناهی را صریح می‌کنیم؛ همان دو قاعده و همان نتیجه حفظ می‌شوند. در جهت عکس اگر ¬A در شاهد نبود، تضعیف آن را وارد می‌کند.

پیش از اصلاح:
```latex
\begin{proof}
نخست فرض کنید $\Gamma \Proves !A$؛ یعنی !!a{derivation}~$\pi_0$
برای $\Gamma \Sequent !A$ وجود دارد. با افزودن قاعدهٔ
$\LeftR{\lnot}$، !!a{derivation} برای
~$\lnot !A, \Gamma \Sequent \quad$ به دست می‌آوریم؛ یعنی
$\Gamma \cup \{\lnot !A\}$ ناسازگار است.
```

پس از اصلاح:
```latex
\begin{proof}
نخست فرض کنید $\Gamma \Proves !A$. زیرمجموعه‌ای متناهی
$\Gamma_0 \subseteq \Gamma$ و !!a{derivation}~$\pi_0$ برای
$\Gamma_0 \Sequent !A$ وجود دارند. با افزودن قاعدهٔ
$\LeftR{\lnot}$، !!a{derivation} برای~$\lnot !A, \Gamma_0
\Sequent \quad$ به دست می‌آوریم؛ پس $\Gamma \cup \{\lnot !A\}$ ناسازگار است.
```

شواهد: H14-SEQUENT, H17-TREE, MT11-SAT.
گزینه‌های کنارگذاشته‌شده: فرض متناهی‌بودن خود Γ قضیه را محدود می‌کند؛ حذف شرط متناهی تعریف رشته را تغییر می‌دهد. هیچ‌یک پذیرفته نشد.
اطمینان تحریری: 4 از ۴.

### FA-SEQ78-FINITE-P12

Γ در قضیه مجموعهٔ دلخواه است، اما طبق تعریف ۰۰۷۰ دو طرف رشته متناهی‌اند و طبق ۰۰۷۷ رابطهٔ اشتقاق از Γ با شاهد Γ0 متناهی تعریف می‌شود. نوشتن Γ⇒A برای Γ دلخواه در دو بند برهان از این قرارداد بیرون است. Γ0⊆Γ و گواه متناهی را صریح می‌کنیم؛ همان دو قاعده و همان نتیجه حفظ می‌شوند. در جهت عکس اگر ¬A در شاهد نبود، تضعیف آن را وارد می‌کند.

پیش از اصلاح:
```latex
اگر $\Gamma \cup \{\lnot !A\}$ ناسازگار باشد، !!a{derivation}~$\pi_1$
برای $\lnot !A, \Gamma \Sequent \quad$ وجود دارد. عبارت زیر
!!a{derivation} برای $\Gamma \Sequent !A$ است:
\begin{prooftree}
  \Axiom$!A \fCenter !A$
  \RightLabel{\RightR{\lnot}}
  \UnaryInf$\fCenter !A, \lnot !A$
  \AxiomC{}
  \RightLabel{$\pi_1$}
  \Deduce$\lnot !A, \Gamma \fCenter$
  \RightLabel{\Cut}
  \BinaryInf$\Gamma \fCenter !A$
\end{prooftree}
\end{proof}
```

پس از اصلاح:
```latex
اگر $\Gamma \cup \{\lnot !A\}$ ناسازگار باشد، زیرمجموعه‌ای متناهی
$\Gamma_0 \subseteq \Gamma$ و !!a{derivation}~$\pi_1$ برای
$\lnot !A, \Gamma_0 \Sequent \quad$ وجود دارند. عبارت زیر
!!a{derivation} برای $\Gamma_0 \Sequent !A$ است:
\begin{prooftree}
  \Axiom$!A \fCenter !A$
  \RightLabel{\RightR{\lnot}}
  \UnaryInf$\fCenter !A, \lnot !A$
  \AxiomC{}
  \RightLabel{$\pi_1$}
  \Deduce$\lnot !A, \Gamma_0 \fCenter$
  \RightLabel{\Cut}
  \BinaryInf$\Gamma_0 \fCenter !A$
\end{prooftree}
بنابراین $\Gamma \Proves !A$.
\end{proof}
```

شواهد: H14-SEQUENT, H17-TREE, MT11-SAT.
گزینه‌های کنارگذاشته‌شده: فرض متناهی‌بودن خود Γ قضیه را محدود می‌کند؛ حذف شرط متناهی تعریف رشته را تغییر می‌دهد. هیچ‌یک پذیرفته نشد.
اطمینان تحریری: 4 از ۴.

### SEQ75-SEARCH-AND-ERRATA

مسیر جست‌وجوی ناتمام، خطای واقعیِ نفی و نام نادرست قاعده سه چیز متفاوت‌اند.

علامت پرسش و گره‌های بازِ تعمدی حفظ شدند؛ فقط نفی‌های افتاده اصلاح و برچسب‌های درستِ قبلی نگهداری شدند.
مواضع بررسی‌شده: OLP-0075-P06, OLP-0075-P07, OLP-0075-P08, OLP-0075-P09, OLP-0075-P10, OLP-0075-P11, OLP-0075-P12, OLP-0075-P13, OLP-0075-P14, OLP-0075-P15, OLP-0075-P16, OLP-0075-P17, OLP-0075-P18, OLP-0075-P19, OLP-0075-P20, OLP-0075-P21.
شواهد: H17-TREE, MT9-CONNECTIVES, H14-SEQUENT.
گزینه‌های بررسی‌شده: نباید مثالِ شکست جست‌وجو را به اثبات موفق تبدیل کرد یا اصلاح قبلی را کار تازه شمرد.
اطمینان تحریری: 4 از ۴.

### SEQ76-EIGENCONSTANT

ثابتِ مشترک برای دو نمونه‌گذاری و تازگیِ محلیِ همان گام حفظ می‌شود.

شرط ویژه محدود به رشتهٔ پایینِ گام است؛ استفاده از a در شاخهٔ بالاتر مجاز است و همان رسیدن به رشتهٔ آغازین را ممکن می‌کند.
مواضع بررسی‌شده: OLP-0076-P06, OLP-0076-P07, OLP-0076-P08, OLP-0076-P09, OLP-0076-P10.
شواهد: MT10-FREE-BOUND, H17-TREE.
گزینه‌های بررسی‌شده: منعِ a در کل برهان یا اشتقاق‌ناپذیریِ همهٔ نمونه‌های A(a)⇒A(b) از متن نتیجه نمی‌شود.
اطمینان تحریری: 3 از ۴.

### SEQ77-FINITE-WITNESS

مجموعهٔ فرض‌ها و توالیِ متناهیِ یک رشته دو سطح متفاوت‌اند.

تمام تعریف‌ها و سه خاصیت و فشردگی با این تفکیک خوانده شدند؛ اشتقاق‌ناپذیری به اثبات نقیض تعبیر نمی‌شود.
مواضع بررسی‌شده: OLP-0077-P07, OLP-0077-P08, OLP-0077-P09, OLP-0077-P10, OLP-0077-P11, OLP-0077-P12, OLP-0077-P13, OLP-0077-P14, OLP-0077-P15, OLP-0077-P16, OLP-0077-P17, OLP-0077-P18, OLP-0077-P19, OLP-0077-P20, OLP-0077-P21, OLP-0077-P22, OLP-0077-P23.
شواهد: H14-SEQUENT, H17-TREE, MT11-SAT.
گزینه‌های بررسی‌شده: نام‌های موقتِ بدون شاهد لفظیِ تازه به عنوان اجماع معرفی نمی‌شوند؛ تعریف ریاضی و مقدار اطمینان ثبت است.
اطمینان تحریری: 3 از ۴.

### SEQ78-FINITE-REPAIR

برهانِ مجموعهٔ دلخواه با شاهد متناهی نوشته می‌شود، نه رشتهٔ نامتناهی.

فقط دو بندِ ناسازگار با قراردادِ متناهی‌بودن صریح اصلاح شدند؛ صورت قضیه، قواعد، و نتیجهٔ کلی تغییر نکردند.
مواضع بررسی‌شده: OLP-0078-P07, OLP-0078-P08, OLP-0078-P09, OLP-0078-P10, OLP-0078-P11, OLP-0078-P12, OLP-0078-P13, OLP-0078-P14, OLP-0078-P15, OLP-0078-P16, OLP-0078-P17.
شواهد: H14-SEQUENT, H17-TREE.
گزینه‌های بررسی‌شده: فرض متناهی‌بودن Γ یا اختراع قاعدهٔ بی‌نهایت‌مقدمه رد شد؛ جابه‌جایی مجازِ ترتیب مقدمات خطا محسوب نشد.
اطمینان تحریری: 4 از ۴.

## بندهای هم‌تراز برای بازبینی انسانی

متن هر دو طرف، بازهٔ دقیق بایت، شمارهٔ خط و هش در SEQUENT_EXAMPLES_0075_0078.json موجود است. تکرارهای یک انتخاب در بافت بند خود بررسی شده‌اند؛ این ثبت جای ادعای بی‌پشتوانهٔ تأیید تک‌تک واژه‌ها را نمی‌گیرد.

### محل ادغام اصلاح‌ها: OLP-0075

همهٔ متن بومی، شامل شاخه‌های غیرفعال، بازبینی شده است. انتخابگر واقعی برچسب‌ها نشان می‌دهد که قطعه‌های انتخاب‌شده دقیقاً با خوانندهٔ منتشرشده برابرند. وصلهٔ بومی و اصلاح قطعه‌های خواننده جدا نگه داشته می‌شوند؛ شاهد قدیمی بازنویسی نمی‌شود.

### تفاوت مستند با فرمول منبع: OLP-0075

اصلاح مستندِ منبع/رونویسی؛ نه پیشنهاد افزودن محتوا
در مثال سوم هدف از آغاز نقیض A یا نقیض B است. اعمال عطف چپ فقط A∧B را به A یا B تبدیل می‌کند و حق حذف نفی B از جملهٔ دیگر را ندارد. هر دو درختِ مجاور همان نفی را دارند؛ دو وقوعِ نثر منبع و فارسی نفی را انداخته‌اند.
منبع تثبیت‌شده: `!A,
\lnot !A \lor !B \Sequent \quad`؛ صورت بررسی‌شده برای تطبیق: `!A,
\lnot !A \lor \lnot !B \Sequent \quad`. متن منبع دست‌نخورده نگه داشته شده است؛ جدول پیش و پس از اصلاح، تفاوت خوانندهٔ جاری و پیشنهاد را مشخص می‌کند.

### تفاوت مستند با فرمول منبع: OLP-0075

اصلاح مستندِ منبع/رونویسی؛ نه پیشنهاد افزودن محتوا
در مثال سوم هدف از آغاز نقیض A یا نقیض B است. اعمال عطف چپ فقط A∧B را به A یا B تبدیل می‌کند و حق حذف نفی B از جملهٔ دیگر را ندارد. هر دو درختِ مجاور همان نفی را دارند؛ دو وقوعِ نثر منبع و فارسی نفی را انداخته‌اند.
منبع تثبیت‌شده: `!B, \lnot !A
\lor !B \Sequent \quad`؛ صورت بررسی‌شده برای تطبیق: `!B, \lnot !A
\lor \lnot !B \Sequent \quad`. متن منبع دست‌نخورده نگه داشته شده است؛ جدول پیش و پس از اصلاح، تفاوت خوانندهٔ جاری و پیشنهاد را مشخص می‌کند.

### اصلاح صریح ارجاع منبع: OLP-0075

اصلاح مستندِ منبع/رونویسی؛ نه پیشنهاد افزودن محتوا
این گام A و ¬A∨B را در مقدم جابه‌جا می‌کند؛ نام قاعده باید تبادل چپ باشد. چهار وقوع در فارسی از قبل درست بوده‌اند؛ کار تازه شمرده نمی‌شوند.
ارجاع منبع: `\RightLabel{\RightR{\Exchange}}
\UnaryInf$ !A, \lnot !A \lor !B \fCenter !B $`؛ ارجاع اصلاح‌شده: `\RightLabel{\LeftR{\Exchange}}
\UnaryInf$ !A, \lnot !A \lor !B \fCenter !B $`. این تفاوت ثبت شده است؛ ادعای یکسان‌ماندن همهٔ ارجاع‌ها نمی‌شود.

### محل ادغام اصلاح‌ها: OLP-0076

همهٔ متن بومی، شامل شاخه‌های غیرفعال، بازبینی شده است. انتخابگر واقعی برچسب‌ها نشان می‌دهد که قطعه‌های انتخاب‌شده دقیقاً با خوانندهٔ منتشرشده برابرند. وصلهٔ بومی و اصلاح قطعه‌های خواننده جدا نگه داشته می‌شوند؛ شاهد قدیمی بازنویسی نمی‌شود.

### محل ادغام اصلاح‌ها: OLP-0077

همهٔ متن بومی، شامل شاخه‌های غیرفعال، بازبینی شده است. انتخابگر واقعی برچسب‌ها نشان می‌دهد که قطعه‌های انتخاب‌شده دقیقاً با خوانندهٔ منتشرشده برابرند. وصلهٔ بومی و اصلاح قطعه‌های خواننده جدا نگه داشته می‌شوند؛ شاهد قدیمی بازنویسی نمی‌شود.

### محل ادغام اصلاح‌ها: OLP-0078

همهٔ متن بومی، شامل شاخه‌های غیرفعال، بازبینی شده است. انتخابگر واقعی برچسب‌ها نشان می‌دهد که قطعه‌های انتخاب‌شده دقیقاً با خوانندهٔ منتشرشده برابرند. وصلهٔ بومی و اصلاح قطعه‌های خواننده جدا نگه داشته می‌شوند؛ شاهد قدیمی بازنویسی نمی‌شود.

### تفاوت مستند با فرمول منبع: OLP-0078

اصلاح مستندِ منبع/رونویسی؛ نه پیشنهاد افزودن محتوا
Γ در قضیه مجموعهٔ دلخواه است، اما طبق تعریف ۰۰۷۰ دو طرف رشته متناهی‌اند و طبق ۰۰۷۷ رابطهٔ اشتقاق از Γ با شاهد Γ0 متناهی تعریف می‌شود. نوشتن Γ⇒A برای Γ دلخواه در دو بند برهان از این قرارداد بیرون است. Γ0⊆Γ و گواه متناهی را صریح می‌کنیم؛ همان دو قاعده و همان نتیجه حفظ می‌شوند. در جهت عکس اگر ¬A در شاهد نبود، تضعیف آن را وارد می‌کند.
منبع تثبیت‌شده: `\begin{proof}
First suppose $\Gamma \Proves !A$, i.e., there is
!!a{derivation}~$\pi_0$ of $\Gamma \Sequent !A$. By adding a
$\LeftR{\lnot}$ rule, we obtain !!a{derivation} of~$\lnot !A, \Gamma
\Sequent \quad$, i.e., $\Gamma \cup \{\lnot !A\}$ is inconsistent.`؛ صورت بررسی‌شده برای تطبیق: `\begin{proof}
First suppose $\Gamma \Proves !A$. There is a finite subset
$\Gamma_0 \subseteq \Gamma$ and !!a{derivation}~$\pi_0$ of
$\Gamma_0 \Sequent !A$. By adding a
$\LeftR{\lnot}$ rule, we obtain !!a{derivation} of~$\lnot !A, \Gamma_0
\Sequent \quad$, so $\Gamma \cup \{\lnot !A\}$ is inconsistent.`. متن منبع دست‌نخورده نگه داشته شده است؛ جدول پیش و پس از اصلاح، تفاوت خوانندهٔ جاری و پیشنهاد را مشخص می‌کند.

### تفاوت مستند با فرمول منبع: OLP-0078

اصلاح مستندِ منبع/رونویسی؛ نه پیشنهاد افزودن محتوا
Γ در قضیه مجموعهٔ دلخواه است، اما طبق تعریف ۰۰۷۰ دو طرف رشته متناهی‌اند و طبق ۰۰۷۷ رابطهٔ اشتقاق از Γ با شاهد Γ0 متناهی تعریف می‌شود. نوشتن Γ⇒A برای Γ دلخواه در دو بند برهان از این قرارداد بیرون است. Γ0⊆Γ و گواه متناهی را صریح می‌کنیم؛ همان دو قاعده و همان نتیجه حفظ می‌شوند. در جهت عکس اگر ¬A در شاهد نبود، تضعیف آن را وارد می‌کند.
منبع تثبیت‌شده: `If $\Gamma \cup \{\lnot !A\}$ is inconsistent, there is
!!a{derivation}~$\pi_1$ of $\lnot !A, \Gamma \Sequent \quad$. The
following is !!a{derivation} of $\Gamma \Sequent !A$:
\begin{prooftree}
  \Axiom$!A \fCenter !A$
  \RightLabel{\RightR{\lnot}}
  \UnaryInf$\fCenter !A, \lnot !A$
  \AxiomC{}
  \RightLabel{$\pi_1$}
  \Deduce$\lnot !A, \Gamma \fCenter$
  \RightLabel{\Cut}
  \BinaryInf$\Gamma \fCenter !A$
\end{prooftree}
\end{proof}`؛ صورت بررسی‌شده برای تطبیق: `If $\Gamma \cup \{\lnot !A\}$ is inconsistent, there is a finite
subset $\Gamma_0 \subseteq \Gamma$ and !!a{derivation}~$\pi_1$ of
$\lnot !A, \Gamma_0 \Sequent \quad$. The following is
!!a{derivation} of $\Gamma_0 \Sequent !A$:
\begin{prooftree}
  \Axiom$!A \fCenter !A$
  \RightLabel{\RightR{\lnot}}
  \UnaryInf$\fCenter !A, \lnot !A$
  \AxiomC{}
  \RightLabel{$\pi_1$}
  \Deduce$\lnot !A, \Gamma_0 \fCenter$
  \RightLabel{\Cut}
  \BinaryInf$\Gamma_0 \fCenter !A$
\end{prooftree}
Thus $\Gamma \Proves !A$.
\end{proof}`. متن منبع دست‌نخورده نگه داشته شده است؛ جدول پیش و پس از اصلاح، تفاوت خوانندهٔ جاری و پیشنهاد را مشخص می‌کند.

### OLP-0075-P04

شناسهٔ دو بافت عیناً حفظ است.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\iftag{FOL}
      {\olfileid{fol}{seq}{pro}}
      {\olfileid{pl}{seq}{pro}}
```

ترجمهٔ فارسی:
```latex
\iftag{FOL}
      {\olfileid{fol}{seq}{pro}}
      {\olfileid{pl}{seq}{pro}}
```

</details>

### OLP-0075-P05

عنوان نمونه‌هایی از اشتقاق‌ها به نمونه‌سازیِ درخت‌های همین دستگاه اشاره دارد.
شواهد: H17-TREE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olsection{Examples of \usetoken{P}{derivation}}
```

ترجمهٔ فارسی:
```latex
\olsection{نمونه‌هایی از \usetoken{P}{derivation}}
```

</details>

### OLP-0075-P06

هدف A∧B⇒A حفظ است؛ رشته نام شیء است و LK همان دستگاه معرفی‌شده است.
شواهد: H14-SEQUENT, MT9-CONNECTIVES.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{ex}
Give an $\Log{LK}$-!!{derivation} for the sequent $!A \land !B \Sequent !A$.
```

ترجمهٔ فارسی:
```latex
\begin{ex}
یک $\Log{LK}$-!!{derivation} برای رشتهٔ
$!A \land !B \Sequent !A$ به دست دهید.
```

</details>

### OLP-0075-P07

جست‌وجو از پایین به بالا، انتخاب عطف چپ و تمایز A⇒A آغازین با B⇒Aِ عموماً اشتقاق‌ناپذیر، هر سه نمودار و نتیجهٔ نهایی مقابله شدند.
شواهد: H17-TREE, MT9-CONNECTIVES.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
We begin by writing the desired end-sequent at the bottom of the
!!{derivation}.
\begin{prooftree}
\AxiomC{}
\UnaryInf$!A\land !B \fCenter !A$
\end{prooftree}
Next, we need to figure out what kind of inference could have a lower
sequent of this form. This could be a structural rule, but it is a
good idea to start by looking for a logical rule. The only logical
connective occurring in the lower sequent is $\land$,
so we're looking for an $\land$ rule, and since the $\land$ symbol
occurs in the antecedent, we're looking at the \LeftR{\land}
rule.
\begin{prooftree}
\AxiomC{}
\RightLabel{\LeftR{\land}}
\UnaryInf$!A\land !B \fCenter !A$
\end{prooftree}
There are two options for what could have been the upper sequent of
the \LeftR{\land} inference: we could have an upper sequent of $!A
\Sequent !A$, or of $!B \Sequent !A$. Clearly, $!A \Sequent !A$ is an
initial sequent (which is a good thing), while $!B \Sequent !A$ is not
derivable in general. We fill in the upper sequent:
\begin{prooftree}
\Axiom$!A \fCenter !A$
\RightLabel{\LeftR{\land}}
\UnaryInf$!A\land !B \fCenter !A$
\end{prooftree}
We now have a correct $\Log{LK}$-!!{derivation} of the sequent $!A
\land !B \Sequent !A$.
\end{ex}
```

ترجمهٔ فارسی:
```latex
با نوشتن رشتهٔ پایانیِ مطلوب در پایین !!{derivation} آغاز می‌کنیم.
\begin{prooftree}
\AxiomC{}
\UnaryInf$!A\land !B \fCenter !A$
\end{prooftree}
سپس باید دریابیم چه نوع استنتاجی می‌تواند رشتهٔ پایینی‌ای به این
صورت داشته باشد. ممکن است قاعده‌ای ساختاری باشد، اما بهتر است جست‌وجو
را با یک قاعدهٔ منطقی آغاز کنیم. تنها رابط منطقیِ رشتهٔ پایینی
$\land$ است؛ پس در پی قاعده‌ای برای $\land$ هستیم، و چون نماد
$\land$ در مقدم رخ می‌دهد، قاعدهٔ \LeftR{\land} را بررسی می‌کنیم.
\begin{prooftree}
\AxiomC{}
\RightLabel{\LeftR{\land}}
\UnaryInf$!A\land !B \fCenter !A$
\end{prooftree}
برای رشتهٔ بالاییِ استنتاج \LeftR{\land} دو امکان وجود دارد:
رشتهٔ بالایی می‌تواند $!A \Sequent !A$ یا $!B \Sequent !A$ باشد.
روشن است که $!A \Sequent !A$ رشته‌ای آغازین است (و این مطلوب است)،
درحالی‌که $!B \Sequent !A$ در حالت کلی اشتقاق‌پذیر نیست. رشتهٔ
بالایی را درج می‌کنیم:
\begin{prooftree}
\Axiom$!A \fCenter !A$
\RightLabel{\LeftR{\land}}
\UnaryInf$!A\land !B \fCenter !A$
\end{prooftree}
اکنون $\Log{LK}$-!!{derivation} درستی برای رشتهٔ
$!A \land !B \Sequent !A$ داریم.
\end{ex}
```

</details>

### OLP-0075-P08

هدف ¬A∨B⇒A→B دقیقاً حفظ شد.
شواهد: MT9-CONNECTIVES, H14-SEQUENT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{ex}
Give an $\Log{LK}$-!!{derivation} for the sequent $\lnot !A \lor !B
\Sequent !A \lif !B$.
```

ترجمهٔ فارسی:
```latex
\begin{ex}
یک $\Log{LK}$-!!{derivation} برای رشتهٔ
$\lnot !A \lor !B \Sequent !A \lif !B$ به دست دهید.
```

</details>

### OLP-0075-P09

تنها رابط‌های اصلیِ آخرین رشته برای گام آخر مناسب‌اند؛ نفی زیر فصل است. انتخاب شرطی راست برای تأخیر در انشعاب، قاعدهٔ اجباری خوانده نشد.
شواهد: H17-TREE, MT9-CONNECTIVES.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Begin by writing the desired end-sequent at the bottom of the !!{derivation}.
\begin{prooftree}
\AxiomC{}
\UnaryInf$\lnot !A \lor !B \fCenter !A \lif !B$
\end{prooftree}
To find a logical rule that could give us this end-sequent, we look at
the logical connectives in the end-sequent: $\lnot$, $\lor$, and
$\lif$. We only care at the moment about $\lor$ and $\lif$ because
they are !!{main operator}s of !!{sentence}s in the end-sequent,
while $\lnot$ is inside the scope of another connective, so we will
take care of it later. Our options for logical rules for the final
inference are therefore the \LeftR{\lor} rule and the \RightR{\lif}
rule. We could pick either rule, really, but let's pick the \RightR{\lif}
rule (if for no reason other than it allows us to put off
splitting into two branches). According to the form of \RightR{\lif}
inferences which can yield the lower sequent, this must look like:
\begin{prooftree}
\AxiomC{}
\UnaryInf$ !A, \lnot !A \lor !B \fCenter !B $
\RightLabel{\RightR{\lif}} \UnaryInf$ \lnot !A \lor !B \fCenter !A \lif !B $
\end{prooftree}
```

ترجمهٔ فارسی:
```latex
با نوشتن رشتهٔ پایانیِ مطلوب در پایین !!{derivation} آغاز کنید.
\begin{prooftree}
\AxiomC{}
\UnaryInf$\lnot !A \lor !B \fCenter !A \lif !B$
\end{prooftree}
برای یافتن قاعده‌ای منطقی که بتواند این رشتهٔ پایانی را به دست دهد،
به رابط‌های منطقی آن نگاه می‌کنیم: $\lnot$، $\lor$ و $\lif$. اکنون
فقط $\lor$ و $\lif$ برای ما مهم‌اند، زیرا در رشتهٔ پایانی نقش
!!{main operator}s را برای !!{sentence}s دارند؛ اما $\lnot$ در دامنهٔ
رابط دیگری است و بعداً به آن می‌پردازیم. پس گزینه‌های ما برای قاعدهٔ
منطقیِ استنتاج نهایی، قاعدهٔ \LeftR{\lor} و قاعدهٔ \RightR{\lif}
هستند. در واقع هر کدام را می‌توان برگزید، اما قاعدهٔ
\RightR{\lif} را برمی‌گزینیم (حتی اگر تنها دلیل این باشد که انشعاب
به دو شاخه را به تعویق می‌اندازد). بنا بر صورت استنتاج‌های
\RightR{\lif} که می‌توانند رشتهٔ پایینی را به دست دهند، باید چنین
داشته باشیم:
\begin{prooftree}
\AxiomC{}
\UnaryInf$ !A, \lnot !A \lor !B \fCenter !B $
\RightLabel{\RightR{\lif}} \UnaryInf$ \lnot !A \lor !B \fCenter !A \lif !B $
\end{prooftree}
```

</details>

### OLP-0075-P10

فصلِ مقدم به منتهی‌الیه چپ می‌رود؛ تبادل سمت چپ است. هر دو برچسبِ درستِ فارسی حفظ شد؛ شاخهٔ راست با تضعیف و تبادل از B⇒B می‌آید.
شواهد: H17-TREE, H15-WEAKEN.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
If we move $\lnot !A \lor !B$ to the outside of the antecedent, we can
apply the \LeftR{\lor} rule. According to the schema, this must split
into two upper sequents as follows:
\begin{prooftree}
\AxiomC{}
\UnaryInf$\lnot !A, !A \fCenter !B$
\AxiomC{}
\UnaryInf$!B, !A \fCenter !B$
\RightLabel{\LeftR{\lor}}
\BinaryInf$ \lnot !A \lor !B, !A \fCenter !B $
\RightLabel{\RightR{\Exchange}}
\UnaryInf$ !A, \lnot !A \lor !B \fCenter !B $
\RightLabel{\RightR{\lif}}
\UnaryInf$ \lnot !A \lor !B \fCenter !A \lif !B $
\end{prooftree}
Remember that we are trying to wind our way up to initial sequents; we
seem to be pretty close!{} The right branch is just one weakening and
one exchange away from an initial sequent and then it is done:
\begin{prooftree}
\AxiomC{}
\UnaryInf$\lnot !A, !A \fCenter !B$
\Axiom$!B \fCenter !B$
\RightLabel{\LeftR{\Weakening}}
\UnaryInf$!A, !B \fCenter !B$
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$!B, !A \fCenter !B$
\RightLabel{\LeftR{\lor}}
\BinaryInf$\lnot !A \lor !B, !A \fCenter !B $
\RightLabel{\RightR{\Exchange}}
\UnaryInf$ !A, \lnot !A \lor !B \fCenter !B $
\RightLabel{\RightR{\lif}}
\UnaryInf$ \lnot !A \lor !B \fCenter !A \lif !B $
\end{prooftree}
```

ترجمهٔ فارسی:
```latex
اگر $\lnot !A \lor !B$ را به منتهی‌الیه چپِ مقدم منتقل کنیم، می‌توانیم
قاعدهٔ \LeftR{\lor} را اعمال کنیم. بنا بر شِما، این کار باید به دو
رشتهٔ بالاییِ زیر منشعب شود:
\begin{prooftree}
\AxiomC{}
\UnaryInf$\lnot !A, !A \fCenter !B$
\AxiomC{}
\UnaryInf$!B, !A \fCenter !B$
\RightLabel{\LeftR{\lor}}
\BinaryInf$ \lnot !A \lor !B, !A \fCenter !B $
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$ !A, \lnot !A \lor !B \fCenter !B $
\RightLabel{\RightR{\lif}}
\UnaryInf$ \lnot !A \lor !B \fCenter !A \lif !B $
\end{prooftree}
به یاد داشته باشید که می‌کوشیم مسیر خود را رو به بالا تا رشته‌های
آغازین بیابیم؛ ظاهراً بسیار نزدیک شده‌ایم!{} شاخهٔ راست فقط به یک
تضعیف و یک تبادل نیاز دارد تا به رشته‌ای آغازین برسد و کامل شود:
\begin{prooftree}
\AxiomC{}
\UnaryInf$\lnot !A, !A \fCenter !B$
\Axiom$!B \fCenter !B$
\RightLabel{\LeftR{\Weakening}}
\UnaryInf$!A, !B \fCenter !B$
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$!B, !A \fCenter !B$
\RightLabel{\LeftR{\lor}}
\BinaryInf$\lnot !A \lor !B, !A \fCenter !B $
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$ !A, \lnot !A \lor !B \fCenter !B $
\RightLabel{\RightR{\lif}}
\UnaryInf$ \lnot !A \lor !B \fCenter !A \lif !B $
\end{prooftree}
```

</details>

### OLP-0075-P11

شاخهٔ چپ با نفی چپ، و بالاتر از آن تضعیف/تبادل راست کامل می‌شود. تبادل زیر فصل همچنان چپ است؛ دو اصلاح قبلیِ برچسب حفظ شدند.
شواهد: H17-TREE, MT9-CONNECTIVES, H15-WEAKEN.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Now looking at the left branch, the only logical connective in any
!!{sentence} is the $\lnot$ symbol in the antecedent !!{sentence}s, so
we're looking at an instance of the \LeftR{\lnot} rule.
\begin{prooftree}
\AxiomC{}
\UnaryInf$ !A \fCenter !B, !A$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$\lnot !A, !A \fCenter !B$
\Axiom$!B \fCenter !B$
\RightLabel{\LeftR{\Weakening}}
\UnaryInf$!A, !B \fCenter !B$
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$!B, !A \fCenter !B$
\RightLabel{\LeftR{\lor}}
\BinaryInf$\lnot !A \lor !B, !A \fCenter !B $
\RightLabel{\RightR{\Exchange}}
\UnaryInf$ !A, \lnot !A \lor !B \fCenter !B $
\RightLabel{\RightR{\lif}}
\UnaryInf$ \lnot !A \lor !B \fCenter !A \lif !B $
\end{prooftree}
Similarly to how we finished off the right branch, we are just one
weakening and one exchange away from finishing off this left branch as well.
\begin{prooftree}
\Axiom$!A \fCenter !A$
\RightLabel{\RightR{\Weakening}}
\UnaryInf$ !A \fCenter !A, !B$
\RightLabel{\RightR{\Exchange}}
\UnaryInf$ !A \fCenter !B, !A$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$\lnot !A, !A \fCenter !B$
\Axiom$!B \fCenter !B$
\RightLabel{\LeftR{\Weakening}}
\UnaryInf$!A, !B \fCenter !B$
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$!B, !A \fCenter !B$
\RightLabel{\LeftR{\lor}}
\BinaryInf$\lnot !A \lor !B, !A \fCenter !B $
\RightLabel{\RightR{\Exchange}}
\UnaryInf$ !A, \lnot !A \lor !B \fCenter !B $
\RightLabel{\RightR{\lif}}
\UnaryInf$ \lnot !A \lor !B \fCenter !A \lif !B $
\end{prooftree}
\end{ex}
```

ترجمهٔ فارسی:
```latex
اکنون به شاخهٔ چپ نگاه می‌کنیم. تنها رابط منطقی در هر !!{sentence}،
نماد $\lnot$ در !!{sentence}s مقدم است؛ پس با نمونه‌ای از قاعدهٔ
\LeftR{\lnot} سروکار داریم.
\begin{prooftree}
\AxiomC{}
\UnaryInf$ !A \fCenter !B, !A$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$\lnot !A, !A \fCenter !B$
\Axiom$!B \fCenter !B$
\RightLabel{\LeftR{\Weakening}}
\UnaryInf$!A, !B \fCenter !B$
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$!B, !A \fCenter !B$
\RightLabel{\LeftR{\lor}}
\BinaryInf$\lnot !A \lor !B, !A \fCenter !B $
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$ !A, \lnot !A \lor !B \fCenter !B $
\RightLabel{\RightR{\lif}}
\UnaryInf$ \lnot !A \lor !B \fCenter !A \lif !B $
\end{prooftree}
همانند تکمیل شاخهٔ راست، برای تکمیل این شاخهٔ چپ نیز فقط یک تضعیف
و یک تبادل فاصله داریم.
\begin{prooftree}
\Axiom$!A \fCenter !A$
\RightLabel{\RightR{\Weakening}}
\UnaryInf$ !A \fCenter !A, !B$
\RightLabel{\RightR{\Exchange}}
\UnaryInf$ !A \fCenter !B, !A$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$\lnot !A, !A \fCenter !B$
\Axiom$!B \fCenter !B$
\RightLabel{\LeftR{\Weakening}}
\UnaryInf$!A, !B \fCenter !B$
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$!B, !A \fCenter !B$
\RightLabel{\LeftR{\lor}}
\BinaryInf$\lnot !A \lor !B, !A \fCenter !B $
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$ !A, \lnot !A \lor !B \fCenter !B $
\RightLabel{\RightR{\lif}}
\UnaryInf$ \lnot !A \lor !B \fCenter !A \lif !B $
\end{prooftree}
\end{ex}
```

</details>

### OLP-0075-P12

هدفِ دمورگان در این مثال هر دو نفیِ مقدم و نفیِ عطف نتیجه را دارد.
شواهد: MT9-CONNECTIVES.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{ex}
Give an $\Log{LK}$-!!{derivation} of the sequent $\lnot !A \lor \lnot !B
\Sequent \lnot (!A \land !B)$
```

ترجمهٔ فارسی:
```latex
\begin{ex}
یک $\Log{LK}$-!!{derivation} برای رشتهٔ
$\lnot !A \lor \lnot !B \Sequent \lnot (!A \land !B)$ به دست دهید.
```

</details>

### OLP-0075-P13

دو نفیِ افتاده در نثر اصلاح شدند. مسیر ناموفقِ انتخاب عطف چپ باید همان جملهٔ ¬A∨¬B را نگاه دارد؛ شاخهٔ ناممکنِ A⇒B همان علت شکست مسیر است. بازگشت و انتخاب فصل چپ همهٔ اطلاعات لازم را نگه می‌دارد.
شواهد: MT9-CONNECTIVES, H17-TREE.
اطمینان تحریری: 4 از ۴.
نیازمند بررسی: این مثالِ آموزشی عمداً یک درخت ناتمام دارد؛ علامت پرسش و AxiomC تهی به عنوان نقص ترجمه حذف نشدند.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Using the techniques from above, we start by writing the desired
end-sequent at the bottom.
\begin{prooftree}
\AxiomC{}
\UnaryInf$ \lnot !A \lor \lnot !B \fCenter \lnot (!A \land !B) $
\end{prooftree}
The available main connectives of !!{sentence}s in the end-sequent are
the $\lor$ symbol and the $\lnot$ symbol. It would work to apply
either the \LeftR{\lor} or the \RightR{\lnot} rule here, but we start
with the \RightR{\lnot} rule because it avoids splitting up into two
branches for a moment:
\begin{prooftree}
\AxiomC{}
\UnaryInf$!A \land !B, \lnot !A \lor \lnot !B \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$\lnot !A \lor \lnot !B \fCenter \lnot (!A \land !B)$
\end{prooftree}
Now we have a choice of whether to look at the \LeftR{\land} or the
\LeftR{\lor} rule. Let's see what happens when we apply the \LeftR{\land}
rule: we have a choice to start with either the sequent $!A,
\lnot !A \lor !B \Sequent \quad$ or the sequent $!B, \lnot !A
\lor !B \Sequent \quad$. Since the !!{derivation} is symmetric with
regards to $!A$ and $!B$, let's go with the former:
\begin{prooftree}
\AxiomC{}
\UnaryInf$!A, \lnot !A \lor \lnot !B \fCenter $
\RightLabel{\LeftR{\land}}
\UnaryInf$!A \land !B, \lnot !A \lor \lnot !B \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$\lnot !A \lor \lnot !B \fCenter \lnot (!A \land !B)$
\end{prooftree}
Continuing to fill in the !!{derivation}, we see that we run into a problem:
\begin{prooftree}
\Axiom$!A \fCenter !A$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$ \lnot !A, !A \fCenter$
\AxiomC{}
\RightLabel{?}
\UnaryInf$!A \fCenter !B$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$ \lnot !B, !A \fCenter$
\RightLabel{\LeftR{\lor}}
\BinaryInf$\lnot !A \lor \lnot !B, !A \fCenter $
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$!A, \lnot !A \lor \lnot !B \fCenter $
\RightLabel{\LeftR{\land}}
\UnaryInf$!A \land !B, \lnot !A \lor \lnot !B \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$\lnot !A \lor \lnot !B \fCenter \lnot (!A \land !B)$
\end{prooftree}
The top of the right branch cannot be reduced any further, and it
cannot be brought by way of structural inferences to an initial
sequent, so this is not the right path to take. So clearly, it was a
mistake to apply the \LeftR{\land} rule above. Going back to what we
had before and carrying out the \LeftR{\lor} rule instead, we get
\begin{prooftree}
\AxiomC{}
\UnaryInf$\lnot !A, !A \land !B \fCenter $
```

ترجمهٔ فارسی:
```latex
با استفاده از روش‌های بالا، با نوشتن رشتهٔ پایانیِ مطلوب در پایین
آغاز می‌کنیم.
\begin{prooftree}
\AxiomC{}
\UnaryInf$ \lnot !A \lor \lnot !B \fCenter \lnot (!A \land !B) $
\end{prooftree}
رابط‌های اصلیِ در دسترسِ !!{sentence}s رشتهٔ پایانی، نماد
$\lor$ و نماد $\lnot$ هستند. در اینجا اعمال هر یک از قاعدهٔ
\LeftR{\lor} یا قاعدهٔ \RightR{\lnot} نتیجه می‌دهد، اما با قاعدهٔ
\RightR{\lnot} آغاز می‌کنیم، زیرا انشعاب به دو شاخه را اندکی به
تعویق می‌اندازد:
\begin{prooftree}
\AxiomC{}
\UnaryInf$!A \land !B, \lnot !A \lor \lnot !B \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$\lnot !A \lor \lnot !B \fCenter \lnot (!A \land !B)$
\end{prooftree}
اکنون میان بررسی قاعدهٔ \LeftR{\land} و قاعدهٔ \LeftR{\lor} حق انتخاب
داریم. ببینیم با اعمال قاعدهٔ \LeftR{\land} چه رخ می‌دهد: می‌توانیم
با رشتهٔ $!A, \lnot !A \lor \lnot !B \Sequent \quad$ یا رشتهٔ
$!B, \lnot !A \lor \lnot !B \Sequent \quad$ آغاز کنیم. چون !!{derivation}
نسبت به $!A$ و $!B$ متقارن است، مورد نخست را برمی‌گزینیم:
\begin{prooftree}
\AxiomC{}
\UnaryInf$!A, \lnot !A \lor \lnot !B \fCenter $
\RightLabel{\LeftR{\land}}
\UnaryInf$!A \land !B, \lnot !A \lor \lnot !B \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$\lnot !A \lor \lnot !B \fCenter \lnot (!A \land !B)$
\end{prooftree}
با ادامهٔ پرکردن !!{derivation} می‌بینیم که به مشکلی برمی‌خوریم:
\begin{prooftree}
\Axiom$!A \fCenter !A$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$ \lnot !A, !A \fCenter$
\AxiomC{}
\RightLabel{?}
\UnaryInf$!A \fCenter !B$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$ \lnot !B, !A \fCenter$
\RightLabel{\LeftR{\lor}}
\BinaryInf$\lnot !A \lor \lnot !B, !A \fCenter $
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$!A, \lnot !A \lor \lnot !B \fCenter $
\RightLabel{\LeftR{\land}}
\UnaryInf$!A \land !B, \lnot !A \lor \lnot !B \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$\lnot !A \lor \lnot !B \fCenter \lnot (!A \land !B)$
\end{prooftree}
بالای شاخهٔ راست را نمی‌توان بیش از این فروکاست و با استنتاج‌های
ساختاری نیز نمی‌توان آن را به رشته‌ای آغازین رساند؛ پس این مسیر
درستی نیست. بنابراین آشکار است که اعمال قاعدهٔ \LeftR{\land} در بالا
خطا بود. اگر به مرحلهٔ پیشین بازگردیم و به‌جای آن قاعدهٔ
\LeftR{\lor} را اعمال کنیم، به عبارت زیر می‌رسیم:
\begin{prooftree}
\AxiomC{}
\UnaryInf$\lnot !A, !A \land !B \fCenter $
```

</details>

### OLP-0075-P14

قطعهٔ میانی درخت با سطر قبل و بعد خوانده شد؛ شاخهٔ B و هر نماد/قاعده عیناً حفظ‌اند. شکستن فایل به بند، شکستن خود برهان نیست.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\AxiomC{}
\UnaryInf$\lnot !B, !A \land !B \fCenter $
```

ترجمهٔ فارسی:
```latex
\AxiomC{}
\UnaryInf$\lnot !B, !A \land !B \fCenter $
```

</details>

### OLP-0075-P15

دو شاخه با فصل چپ ترکیب می‌شوند؛ سپس تبادل چپ و نفی راست. آغاز درخت کامل بعدی از A⇒A و عطف چپ می‌آید.
شواهد: H17-TREE, MT9-CONNECTIVES.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\RightLabel{\LeftR{\lor}}
\BinaryInf$\lnot !A \lor \lnot !B, !A \land !B \fCenter $
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$!A \land !B, \lnot !A \lor \lnot !B \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$\lnot !A \lor \lnot !B \fCenter \lnot (!A \land !B)$
\end{prooftree}
Completing each branch as we've done before, we get
\begin{prooftree}
\Axiom$ !A \fCenter!A$
\RightLabel{\LeftR{\land}}
\UnaryInf$!A \land !B \fCenter !A$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$\lnot !A, !A \land !B \fCenter $
```

ترجمهٔ فارسی:
```latex
\RightLabel{\LeftR{\lor}}
\BinaryInf$\lnot !A \lor \lnot !B, !A \land !B \fCenter $
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$!A \land !B, \lnot !A \lor \lnot !B \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$\lnot !A \lor \lnot !B \fCenter \lnot (!A \land !B)$
\end{prooftree}
با تکمیل هر شاخه به همان شیوهٔ پیشین، داریم:
\begin{prooftree}
\Axiom$ !A \fCenter!A$
\RightLabel{\LeftR{\land}}
\UnaryInf$!A \land !B \fCenter !A$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$\lnot !A, !A \land !B \fCenter $
```

</details>

### OLP-0075-P16

قطعهٔ میانی درخت با سطر قبل و بعد خوانده شد؛ شاخهٔ B و هر نماد/قاعده عیناً حفظ‌اند. شکستن فایل به بند، شکستن خود برهان نیست.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\Axiom$ !B \fCenter !B$
\RightLabel{\LeftR{\land}}
\UnaryInf$!A \land !B \fCenter !B$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$\lnot !B, !A \land !B \fCenter $
```

ترجمهٔ فارسی:
```latex
\Axiom$ !B \fCenter !B$
\RightLabel{\LeftR{\land}}
\UnaryInf$!A \land !B \fCenter !B$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$\lnot !B, !A \land !B \fCenter $
```

</details>

### OLP-0075-P17

ترکیب نهایی و امکان جابه‌جایی ترتیب عطف/نفی در شرحِ منبع حفظ شدند؛ هیچ قاعده‌ای از منطق مقالهٔ ابتنا وارد نشد.
شواهد: H17-TREE, MT9-CONNECTIVES.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\RightLabel{\LeftR{\lor}}
\BinaryInf$\lnot !A \lor \lnot !B, !A \land !B \fCenter $
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$!A \land !B, \lnot !A \lor \lnot !B \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$\lnot !A \lor \lnot !B \fCenter \lnot (!A \land !B)$
\end{prooftree}
(We could have carried out the $\land$ rules lower than the $\lnot$
rules in these steps and still obtained a correct !!{derivation}).
\end{ex}
```

ترجمهٔ فارسی:
```latex
\RightLabel{\LeftR{\lor}}
\BinaryInf$\lnot !A \lor \lnot !B, !A \land !B \fCenter $
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$!A \land !B, \lnot !A \lor \lnot !B \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$\lnot !A \lor \lnot !B \fCenter \lnot (!A \land !B)$
\end{prooftree}
(در این گام‌ها می‌توانستیم قواعد $\land$ را پایین‌تر از قواعد
$\lnot$ اعمال کنیم و باز هم !!{derivation} درستی به دست آوریم.)
\end{ex}
```

</details>

### OLP-0075-P18

جست‌وجوی نادرست دو شق و سپس استفادهٔ وارونه از انقباض برای نگه‌داشتن یک نسخهٔ دیگر A∨¬A مقابله شد. در درخت کامل نفی راست، دو فصل راست، تبادل و انقباض درست و به ترتیب‌اند.
شواهد: H17-TREE, H15-WEAKEN.
اطمینان تحریری: 4 از ۴.
نیازمند بررسی: کامل در اشتقاق کامل به معنی ناتمام‌نبودن درخت است، نه صفت فنی تام برای دستگاه؛ عمداً به تام تبدیل نشد.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{ex}
So far we haven't used the contraction rule, but it is sometimes
required. Here's an example where that happens.  Suppose we want to
prove $\quad \Sequent !A \lor \lnot !A$. Applying $\RightR{\lor}$
backwards would give us one of these two !!{derivation}s:
\begin{prooftree}
\AxiomC{}
\UnaryInf$ \fCenter !A$
\RightLabel{\RightR{\lor}}
\UnaryInf$ \fCenter !A \lor \lnot !A$
\DisplayProof\qquad\bottomAlignProof
\AxiomC{}
\UnaryInf$!A \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$ \fCenter \lnot !A$
\RightLabel{\RightR{\lor}}
\UnaryInf$ \fCenter !A \lor \lnot !A$
\end{prooftree}
Neither of these of course ends in an initial sequent.  The trick is
to realize that the contraction rule allows us to combine two copies
of !!a{sentence} into one---and when we're searching for a proof,
i.e., going from bottom to top, we can keep a copy of $!A \lor \lnot
!A$ in the premise, e.g.,
\begin{prooftree}
\AxiomC{}
\UnaryInf$ \fCenter !A \lor \lnot !A, !A$
\RightLabel{\RightR{\lor}}
\UnaryInf$ \fCenter !A \lor \lnot !A, !A \lor \lnot !A$
\RightLabel{\RightR{\Contraction}}
\UnaryInf$ \fCenter !A \lor \lnot !A$
\end{prooftree}
Now we can apply $\RightR{\lor}$ a second time, and also get~$\lnot
!A$, which leads to a complete !!{derivation}.
\begin{prooftree}
\Axiom$!A \fCenter !A$
\RightLabel{\RightR{\lnot}}
\UnaryInf$\fCenter !A, \lnot !A$
\RightLabel{\RightR{\lor}}
\UnaryInf$\fCenter !A, !A \lor \lnot !A$
\RightLabel{\RightR{\Exchange}}
\UnaryInf$ \fCenter !A \lor \lnot !A, !A$
\RightLabel{\RightR{\lor}}
\UnaryInf$ \fCenter !A \lor \lnot !A, !A \lor \lnot !A$
\RightLabel{\RightR{\Contraction}}
\UnaryInf$ \fCenter !A \lor \lnot !A$
\end{prooftree}
\end{ex}
```

ترجمهٔ فارسی:
```latex
\begin{ex}
تا اینجا از قاعدهٔ انقباض استفاده نکرده‌ایم، اما گاهی به آن نیاز
داریم. نمونه‌ای از چنین وضعی را ببینیم. فرض کنید می‌خواهیم
$\quad \Sequent !A \lor \lnot !A$ را اثبات کنیم. اعمال وارونهٔ
$\RightR{\lor}$ یکی از !!{derivation}s زیر را به ما می‌دهد:
\begin{prooftree}
\AxiomC{}
\UnaryInf$ \fCenter !A$
\RightLabel{\RightR{\lor}}
\UnaryInf$ \fCenter !A \lor \lnot !A$
\DisplayProof\qquad\bottomAlignProof
\AxiomC{}
\UnaryInf$!A \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$ \fCenter \lnot !A$
\RightLabel{\RightR{\lor}}
\UnaryInf$ \fCenter !A \lor \lnot !A$
\end{prooftree}
البته هیچ‌یک از این دو به رشته‌ای آغازین ختم نمی‌شود. نکته این است
که قاعدهٔ انقباض به ما امکان می‌دهد دو نسخه از !!a{sentence} را در
یکی ادغام کنیم---و هنگامی که در جست‌وجوی برهانیم، یعنی از پایین به
بالا می‌رویم، می‌توانیم نسخه‌ای از $!A \lor \lnot !A$ را در مقدمه
نگه داریم؛ برای نمونه:
\begin{prooftree}
\AxiomC{}
\UnaryInf$ \fCenter !A \lor \lnot !A, !A$
\RightLabel{\RightR{\lor}}
\UnaryInf$ \fCenter !A \lor \lnot !A, !A \lor \lnot !A$
\RightLabel{\RightR{\Contraction}}
\UnaryInf$ \fCenter !A \lor \lnot !A$
\end{prooftree}
اکنون می‌توانیم $\RightR{\lor}$ را بار دوم اعمال کنیم و
~$\lnot !A$ را نیز به دست آوریم؛ این به !!{derivation} کاملی می‌انجامد.
\begin{prooftree}
\Axiom$!A \fCenter !A$
\RightLabel{\RightR{\lnot}}
\UnaryInf$\fCenter !A, \lnot !A$
\RightLabel{\RightR{\lor}}
\UnaryInf$\fCenter !A, !A \lor \lnot !A$
\RightLabel{\RightR{\Exchange}}
\UnaryInf$ \fCenter !A \lor \lnot !A, !A$
\RightLabel{\RightR{\lor}}
\UnaryInf$ \fCenter !A \lor \lnot !A, !A \lor \lnot !A$
\RightLabel{\RightR{\Contraction}}
\UnaryInf$ \fCenter !A \lor \lnot !A$
\end{prooftree}
\end{ex}
```

</details>

### OLP-0075-P19

دستور ساخت اشتقاق و همهٔ فرمول‌های همین فهرست تمرین، تعداد موارد و نفی/شرطی/جهت رشته با منبع تطبیق یافتند؛ حل تمرین اضافه نشده است.
شواهد: H17-TREE, MT9-CONNECTIVES.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: ادعای منبع دربارهٔ نیاز همهٔ تمرین‌های فهرست آخر به انقباض راست، در این دور برای تک‌تک تمرین‌ها مستقل اثبات نشده؛ این محدودیت در گزارش است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob}
Give !!{derivation}s of the following sequents:
\begin{enumerate}
\item $!A \land (!B \land !C) \Sequent (!A \land !B) \land !C$.
\item $!A \lor (!B \lor !C) \Sequent (!A \lor !B) \lor !C$.
\item $!A \lif (!B \lif !C) \Sequent !B \lif (!A \lif !C)$.
\item $!A \Sequent \lnot\lnot !A$.
\end{enumerate}
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob}
برای رشته‌های زیر !!{derivation}sی لازم را به دست دهید:
\begin{enumerate}
\item $!A \land (!B \land !C) \Sequent (!A \land !B) \land !C$.
\item $!A \lor (!B \lor !C) \Sequent (!A \lor !B) \lor !C$.
\item $!A \lif (!B \lif !C) \Sequent !B \lif (!A \lif !C)$.
\item $!A \Sequent \lnot\lnot !A$.
\end{enumerate}
\end{prob}
```

</details>

### OLP-0075-P20

دستور ساخت اشتقاق و همهٔ فرمول‌های همین فهرست تمرین، تعداد موارد و نفی/شرطی/جهت رشته با منبع تطبیق یافتند؛ حل تمرین اضافه نشده است.
شواهد: H17-TREE, MT9-CONNECTIVES.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: ادعای منبع دربارهٔ نیاز همهٔ تمرین‌های فهرست آخر به انقباض راست، در این دور برای تک‌تک تمرین‌ها مستقل اثبات نشده؛ این محدودیت در گزارش است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob}
Give !!{derivation}s of the following sequents:
\begin{enumerate}
\item $(!A \lor !B) \lif !C \Sequent !A \lif !C$.
\item $(!A \lif !C) \land (!B \lif !C) \Sequent (!A \lor !B) \lif !C$.
\item $\Sequent \lnot(!A \land \lnot !A)$.
\item $!B \lif !A \Sequent \lnot !A \lif \lnot !B$.
\item $\Sequent (!A \lif \lnot !A) \lif \lnot !A$.
\item $\Sequent \lnot(!A \lif !B) \lif \lnot !B$.
\item $!A \lif !C \Sequent \lnot (!A \land \lnot !C)$.
\item $!A \land \lnot !C \Sequent \lnot (!A \lif !C)$.
\item $!A \lor !B, \lnot !B \Sequent !A$.
\item $\lnot !A \lor \lnot !B \Sequent \lnot(!A \land !B)$.
\item $\Sequent (\lnot !A \land \lnot !B) \lif\lnot(!A \lor !B)$.
\item $\Sequent \lnot(!A \lor !B) \lif (\lnot !A \land \lnot !B)$.
\end{enumerate}
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob}
برای رشته‌های زیر !!{derivation}sی لازم را به دست دهید:
\begin{enumerate}
\item $(!A \lor !B) \lif !C \Sequent !A \lif !C$.
\item $(!A \lif !C) \land (!B \lif !C) \Sequent (!A \lor !B) \lif !C$.
\item $\Sequent \lnot(!A \land \lnot !A)$.
\item $!B \lif !A \Sequent \lnot !A \lif \lnot !B$.
\item $\Sequent (!A \lif \lnot !A) \lif \lnot !A$.
\item $\Sequent \lnot(!A \lif !B) \lif \lnot !B$.
\item $!A \lif !C \Sequent \lnot (!A \land \lnot !C)$.
\item $!A \land \lnot !C \Sequent \lnot (!A \lif !C)$.
\item $!A \lor !B, \lnot !B \Sequent !A$.
\item $\lnot !A \lor \lnot !B \Sequent \lnot(!A \land !B)$.
\item $\Sequent (\lnot !A \land \lnot !B) \lif\lnot(!A \lor !B)$.
\item $\Sequent \lnot(!A \lor !B) \lif (\lnot !A \land \lnot !B)$.
\end{enumerate}
\end{prob}
```

</details>

### OLP-0075-P21

دستور ساخت اشتقاق و همهٔ فرمول‌های همین فهرست تمرین، تعداد موارد و نفی/شرطی/جهت رشته با منبع تطبیق یافتند؛ حل تمرین اضافه نشده است.
شواهد: H17-TREE, MT9-CONNECTIVES.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: ادعای منبع دربارهٔ نیاز همهٔ تمرین‌های فهرست آخر به انقباض راست، در این دور برای تک‌تک تمرین‌ها مستقل اثبات نشده؛ این محدودیت در گزارش است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob}
Give !!{derivation}s of the following sequents:
\begin{enumerate}
\item $\lnot(!A \lif !B) \Sequent !A$.
\item $\lnot(!A \land !B) \Sequent \lnot !A \lor \lnot !B$.
\item $!A \lif !B \Sequent \lnot !A \lor !B$.
\item $\Sequent \lnot \lnot !A \lif !A$.
\item $!A \lif !B, \lnot !A \lif !B \Sequent !B$.
\item $(!A \land !B) \lif !C \Sequent (!A \lif !C) \lor (!B \lif !C)$.
\item $(!A \lif !B) \lif !A \Sequent !A$.
\item $\Sequent (!A \lif !B) \lor (!B \lif !C)$.
\end{enumerate}
(These all require the $\RightR{\Contraction}$~rule.)
\end{prob}
\end{document}

```

ترجمهٔ فارسی:
```latex
\begin{prob}
برای رشته‌های زیر !!{derivation}sی لازم را به دست دهید:
\begin{enumerate}
\item $\lnot(!A \lif !B) \Sequent !A$.
\item $\lnot(!A \land !B) \Sequent \lnot !A \lor \lnot !B$.
\item $!A \lif !B \Sequent \lnot !A \lor !B$.
\item $\Sequent \lnot \lnot !A \lif !A$.
\item $!A \lif !B, \lnot !A \lif !B \Sequent !B$.
\item $(!A \land !B) \lif !C \Sequent (!A \lif !C) \lor (!B \lif !C)$.
\item $(!A \lif !B) \lif !A \Sequent !A$.
\item $\Sequent (!A \lif !B) \lor (!B \lif !C)$.
\end{enumerate}
(همهٔ این موارد به قاعدهٔ~$\RightR{\Contraction}$ نیاز دارند.)
\end{prob}
\end{document}

```

</details>

### OLP-0076-P04

شناسه و حضورِ فقط FOL حفظ‌اند.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olfileid{fol}{seq}{prq}
```

ترجمهٔ فارسی:
```latex
\olfileid{fol}{seq}{prq}
```

</details>

### OLP-0076-P05

سورها و اشتقاق دو نام تثبیت‌شدهٔ این متن‌اند؛ عنوانِ وابسته به توکن حفظ است.
شواهد: MT9-CONNECTIVES, H17-TREE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olsection{\usetoken{P}{derivation} with Quantifiers}
```

ترجمهٔ فارسی:
```latex
\olsection{\usetoken{P}{derivation} با سورها}
```

</details>

### OLP-0076-P06

هدف وجودیِ نفی به نفیِ همگانی با دامنهٔ دقیق دو سور حفظ است.
شواهد: MT9-CONNECTIVES, MT10-FREE-BOUND.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{ex}
Give an $\Log{LK}$-!!{derivation} of the sequent $\lexists[x][\lnot !A(x)]
\Sequent \lnot \lforall[x][!A(x)]$.
```

ترجمهٔ فارسی:
```latex
\begin{ex}
یک $\Log{LK}$-!!{derivation} برای رشتهٔ
$\lexists[x][\lnot !A(x)] \Sequent \lnot \lforall[x][!A(x)]$ به دست دهید.
```

</details>

### OLP-0076-P07

جست‌وجو از پایین به بالا به معنای اجرای معکوس قاعده است؛ قاعدهٔ مقید به شرط ویژه زودتر بررسی و در برهان نهایی پایین‌تر می‌آید. دو ثابت متفاوت شِمای عموماً معتبر نمی‌سازند.
شواهد: MT10-FREE-BOUND, H17-TREE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: متغیر ویژه همان نام تاریخی ثابت است؛ شاهد لفظی اختصاصیِ تازه نداریم. عبارت در حالت کلی رفعِ قرائتِ بیش‌ازحد قوی از شِماست.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
When dealing with quantifiers, we have to make sure not to violate the
eigenvariable condition, and sometimes this requires us to play around
with the order of carrying out certain inferences. In general, it
helps to try and take care of rules subject to the eigenvariable
condition first (they will be lower down in the finished proof). Also,
it is a good idea to try and look ahead and try to guess what the
initial sequent might look like. In our case, it will have to be
something like $!A(a) \Sequent !A(a)$. That means that when we are
``reversing'' the quantifier rules, we will have to pick the same
term---what we will call $a$---for both the $\lforall$ and the
$\lexists$ rule. If we picked different terms for each rule, we would
end up with something like $!A(a) \Sequent !A(b)$, which, of course,
is not derivable.
```

ترجمهٔ فارسی:
```latex
هنگام کار با سورها باید مراقب باشیم شرط متغیر ویژه را نقض نکنیم، و
گاهی این امر ایجاب می‌کند ترتیب انجام برخی استنتاج‌ها را پس‌وپیش کنیم.
به‌طور کلی، بهتر است ابتدا به قواعد مشمول شرط متغیر ویژه بپردازیم
(این قواعد در برهان نهایی پایین‌تر قرار خواهند گرفت). همچنین بهتر است
کمی جلوتر را ببینیم و حدس بزنیم رشتهٔ آغازین چه صورتی خواهد داشت.
در مورد ما، باید چیزی مانند $!A(a) \Sequent !A(a)$ باشد. یعنی هنگام
«وارونه‌کردن» قواعد سورها باید همان ترم---که آن را $a$ می‌نامیم---را
برای هر دو قاعدهٔ $\lforall$ و $\lexists$ برگزینیم. اگر برای
هر قاعده ترم متفاوتی برمی‌گزیدیم، به چیزی مانند
$!A(a) \Sequent !A(b)$ می‌رسیدیم که در حالت کلی اشتقاق‌پذیر نیست.
```

</details>

### OLP-0076-P08

درخت از A(a)⇒A(a)، همگانی چپ، نفی چپ، تبادل چپ، نفی راست و وجودی چپ ساخته می‌شود؛ تنها گام دارای شرط ویژه وجودی چپ است و a در رشتهٔ پایین آن نیست. نمادهای ماکروی forall/exists و lforall/lexists همان‌گونه که در منبع‌اند حفظ شدند.
شواهد: MT10-FREE-BOUND, H17-TREE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Starting as usual, we write
\begin{prooftree}
\AxiomC{}
\UnaryInf$\lexists[x][\lnot !A(x)] \fCenter \lnot \lforall[x][!A(x)]$
\end{prooftree}
We could either carry out the \LeftR{\exists} rule or the \RightR{\lnot}
rule. Since the \LeftR{\exists} rule is subject to the eigenvariable
condition, it's a good idea to take care of it sooner rather than
later, so we'll do that one first.
\begin{prooftree}
\AxiomC{}
\UnaryInf$ \lnot !A(a) \fCenter \lnot \lforall[x][!A(x)]$
\RightLabel{\LeftR{\lexists}}
\UnaryInf$ \lexists[x][\lnot !A(x)] \fCenter \lnot \lforall[x][!A(x)]$
\end{prooftree}
Applying the \LeftR{\lnot} and \RightR{\lnot} rules backwards, we get
\begin{prooftree}
\AxiomC{}
\UnaryInf$\lforall[x][!A(x)] \fCenter !A(a)$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$\lnot !A(a), \lforall[x][!A(x)] \fCenter $
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$\lforall[x][!A(x)], \lnot !A(a) \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$ \lnot !A(a) \fCenter \lnot \lforall[x] !A(x)$
\RightLabel{\LeftR{\lexists}}
\UnaryInf$ \lexists[x] \lnot !A(x) \fCenter \lnot \lforall[x] !A(x)$
\end{prooftree}
At this point, our only option is to carry out the \LeftR{\forall}
rule. Since this rule is not subject to the eigenvariable restriction,
we're in the clear. Remember, we want to try and obtain an initial
sequent (of the form $!A(a) \Sequent !A(a)$), so we should choose $a$
as our argument for $!A$ when we apply the rule.
\begin{prooftree}
\Axiom$!A(a) \fCenter !A(a)$
\RightLabel{\LeftR{\lforall}}
\UnaryInf$\lforall[x][!A(x)] \fCenter !A(a)$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$\lnot !A(a), \lforall[x][!A(x)] \fCenter $
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$\lforall[x][!A(x)], \lnot !A(a) \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$ \lnot !A(a) \fCenter \lnot \lforall[x][!A(x)]$
\RightLabel{\LeftR{\lexists}}
\UnaryInf$ \lexists[x][ \lnot !A(x)] \fCenter \lnot \lforall[x][!A(x)]$
\end{prooftree}
It is important, especially when dealing with quantifiers, to double
check at this point that the eigenvariable condition has not been
violated. Since the only rule we applied that is subject to the
eigenvariable condition was \LeftR{\exists}, and the eigenvariable~$a$
does not occur in its lower sequent (the end-sequent), this is a
correct !!{derivation}.
\end{ex}
```

ترجمهٔ فارسی:
```latex
طبق معمول، با نوشتن عبارت زیر آغاز می‌کنیم:
\begin{prooftree}
\AxiomC{}
\UnaryInf$\lexists[x][\lnot !A(x)] \fCenter \lnot \lforall[x][!A(x)]$
\end{prooftree}
می‌توانیم یا قاعدهٔ \LeftR{\exists} را اجرا کنیم یا قاعدهٔ
\RightR{\lnot} را. چون قاعدهٔ \LeftR{\exists} مشمول شرط متغیر ویژه
است، بهتر است زودتر به آن بپردازیم؛ پس آن را نخست اجرا می‌کنیم.
\begin{prooftree}
\AxiomC{}
\UnaryInf$ \lnot !A(a) \fCenter \lnot \lforall[x][!A(x)]$
\RightLabel{\LeftR{\lexists}}
\UnaryInf$ \lexists[x][\lnot !A(x)] \fCenter \lnot \lforall[x][!A(x)]$
\end{prooftree}
با اعمال وارونهٔ قواعد \LeftR{\lnot} و \RightR{\lnot} به عبارت زیر
می‌رسیم:
\begin{prooftree}
\AxiomC{}
\UnaryInf$\lforall[x][!A(x)] \fCenter !A(a)$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$\lnot !A(a), \lforall[x][!A(x)] \fCenter $
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$\lforall[x][!A(x)], \lnot !A(a) \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$ \lnot !A(a) \fCenter \lnot \lforall[x] !A(x)$
\RightLabel{\LeftR{\lexists}}
\UnaryInf$ \lexists[x] \lnot !A(x) \fCenter \lnot \lforall[x] !A(x)$
\end{prooftree}
در این مرحله تنها گزینهٔ ما اجرای قاعدهٔ \LeftR{\forall} است. چون این
قاعده مشمول محدودیت متغیر ویژه نیست، مشکلی نداریم. به یاد آورید که
می‌خواهیم رشته‌ای آغازین (به صورت $!A(a) \Sequent !A(a)$) به دست
آوریم؛ پس هنگام اعمال قاعده باید $a$ را به‌عنوان آرگومان $!A$ برگزینیم.
\begin{prooftree}
\Axiom$!A(a) \fCenter !A(a)$
\RightLabel{\LeftR{\lforall}}
\UnaryInf$\lforall[x][!A(x)] \fCenter !A(a)$
\RightLabel{\LeftR{\lnot}}
\UnaryInf$\lnot !A(a), \lforall[x][!A(x)] \fCenter $
\RightLabel{\LeftR{\Exchange}}
\UnaryInf$\lforall[x][!A(x)], \lnot !A(a) \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$ \lnot !A(a) \fCenter \lnot \lforall[x][!A(x)]$
\RightLabel{\LeftR{\lexists}}
\UnaryInf$ \lexists[x][ \lnot !A(x)] \fCenter \lnot \lforall[x][!A(x)]$
\end{prooftree}
به‌ویژه هنگام کار با سورها مهم است که در این مرحله دوباره بررسی کنیم
شرط متغیر ویژه نقض نشده باشد. چون تنها قاعدهٔ اعمال‌شده‌ای که مشمول
شرط متغیر ویژه بود \LeftR{\exists} است و متغیر ویژهٔ~$a$ در رشتهٔ
پایینیِ آن (رشتهٔ پایانی) رخ نمی‌دهد، این !!{derivation} درست است.
\end{ex}
```

</details>

### OLP-0076-P09

تمام فرمول‌ها و متغیرهای مقید، از جمله فرمول قطری با A(y,y)، عیناً حفظ‌اند. در فهرست آخر از جمله گزارهٔ نوشنده با دامنهٔ ناتهیِ قرارداد کتاب استفاده می‌شود.
شواهد: MT10-FREE-BOUND, MT9-CONNECTIVES.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: حل کاملِ تمرین‌ها یا اثباتِ ضرورت انقباض برای هر یک ادعا نشده است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob}
Give !!{derivation}s of the following sequents:
\begin{enumerate}
\item $\Sequent (\lforall[x][!A(x)] \land \lforall[y][!B(y)]) \lif
\lforall[z][(!A(z) \land !B(z))]$.
\item $\Sequent (\lexists[x][!A(x)] \lor \lexists[y][!B(y)]) \lif
\lexists[z][(!A(z) \lor !B(z))]$.
\item $\lforall[x][(!A(x) \lif !B)] \Sequent \lexists[y][!A(y)] \lif !B$.
\item $\lforall[x][\lnot !A(x)] \Sequent \lnot\lexists[x][!A(x)]$.
\item $\Sequent \lnot\lexists[x][!A(x)] \lif \lforall[x][\lnot !A(x)]$.
\item $\Sequent \lnot\lexists[x][\lforall[y][((!A(x,y) \lif \lnot
!A(y,y)) \land (\lnot !A(y,y) \lif !A(x,y)))]]$.
\end{enumerate}
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob}
برای رشته‌های زیر !!{derivation}sی لازم را به دست دهید:
\begin{enumerate}
\item $\Sequent (\lforall[x][!A(x)] \land \lforall[y][!B(y)]) \lif
\lforall[z][(!A(z) \land !B(z))]$.
\item $\Sequent (\lexists[x][!A(x)] \lor \lexists[y][!B(y)]) \lif
\lexists[z][(!A(z) \lor !B(z))]$.
\item $\lforall[x][(!A(x) \lif !B)] \Sequent \lexists[y][!A(y)] \lif !B$.
\item $\lforall[x][\lnot !A(x)] \Sequent \lnot\lexists[x][!A(x)]$.
\item $\Sequent \lnot\lexists[x][!A(x)] \lif \lforall[x][\lnot !A(x)]$.
\item $\Sequent \lnot\lexists[x][\lforall[y][((!A(x,y) \lif \lnot
!A(y,y)) \land (\lnot !A(y,y) \lif !A(x,y)))]]$.
\end{enumerate}
\end{prob}
```

</details>

### OLP-0076-P10

تمام فرمول‌ها و متغیرهای مقید، از جمله فرمول قطری با A(y,y)، عیناً حفظ‌اند. در فهرست آخر از جمله گزارهٔ نوشنده با دامنهٔ ناتهیِ قرارداد کتاب استفاده می‌شود.
شواهد: MT10-FREE-BOUND, MT9-CONNECTIVES.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: حل کاملِ تمرین‌ها یا اثباتِ ضرورت انقباض برای هر یک ادعا نشده است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob}
Give !!{derivation}s of the following sequents:
\begin{enumerate}
\item $\Sequent \lnot\lforall[x][!A(x)] \lif \lexists[x][\lnot!A(x)]$.
\item $(\lforall[x][!A(x)] \lif !B) \Sequent \lexists[y][(!A(y) \lif !B)]$.
\item $\Sequent \lexists[x][(!A(x) \lif \lforall[y][!A(y)])]$.
\end{enumerate}
(These all require the $\RightR{\Contraction}$~rule.)
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob}
برای رشته‌های زیر !!{derivation}sی لازم را به دست دهید:
\begin{enumerate}
\item $\Sequent \lnot\lforall[x][!A(x)] \lif \lexists[x][\lnot!A(x)]$.
\item $(\lforall[x][!A(x)] \lif !B) \Sequent \lexists[y][(!A(y) \lif !B)]$.
\item $\Sequent \lexists[x][(!A(x) \lif \lforall[y][!A(y)])]$.
\end{enumerate}
(همهٔ این موارد به قاعدهٔ~$\RightR{\Contraction}$ نیاز دارند.)
\end{prob}
```

</details>

### OLP-0077-P04

موضوع یادداشت حساب رشته است؛ natural deduction در انگلیسی یک خطای کپیِ آشکار با عنوان/قواعد همین بخش است و فارسی قبلاً آن را اصلاح کرده بود.
شواهد: H14-SEQUENT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{editorial}
  This section collects the definitions of the provability relation and
  consistency for natural deduction.
\end{editorial}
```

ترجمهٔ فارسی:
```latex
\begin{editorial}
  این بخش تعریف‌های رابطهٔ اثبات‌پذیری و سازگاری را برای حساب رشته
  گرد می‌آورد.
\end{editorial}
```

</details>

### OLP-0077-P05

شناسهٔ دو زمینه حفظ است.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\iftag{FOL}
      {\olfileid{fol}{seq}{ptn}}
      {\olfileid{pl}{seq}{ptn}}
```

ترجمهٔ فارسی:
```latex
\iftag{FOL}
      {\olfileid{fol}{seq}{ptn}}
      {\olfileid{pl}{seq}{ptn}}
```

</details>

### OLP-0077-P06

برهان‌نظری نام بررسیِ دستگاه نحوی است.
شواهد: H17-TREE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: ترکیب دقیق برهان‌نظری در صفحات حاضر شاهد لفظی مستقل ندارد؛ تعریف و تمایز با معناشناسی روشن است.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olsection{Proof-Theoretic Notions}
```

ترجمهٔ فارسی:
```latex
\olsection{مفاهیم برهان‌نظری}
```

</details>

### OLP-0077-P07

تعریف نحو به ارضا ارجاع نمی‌دهد؛ هم‌ارزی با معناشناسی مضمون صحت/تمامیت است. شاخهٔ فارسیِ PL با ارزش‌گذاری به جای ساختار از قبل وجود دارد و درست حفظ شد.
شواهد: MT11-SAT, H16-COMPLETE, H17-TREE.
اطمینان تحریری: 4 از ۴.
نیازمند بررسی: این فرق شاخهٔ بومی با انگلیسی ثبت می‌شود؛ ادعای هویت لفظیِ دو منبع نداریم.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{explain}
Just as we've defined a number of important semantic notions
(validity, entailment, satisfiability), we now define corresponding
\emph{proof-theoretic notions}.  These are not defined by appeal to
satisfaction of !!{sentence}s in !!{structure}s, but by appeal to the
!!{derivability} or !!{nonderivability} of certain sequents.  It was
an important discovery that these notions coincide.  That they do is
the content of the \emph{soundness} and \emph{completeness theorem}.
\end{explain}
```

ترجمهٔ فارسی:
```latex
\begin{explain}
همان‌گونه که چند مفهوم معناشناختی مهم (اعتبار، استلزام و ارضاپذیری)
را تعریف کردیم، اکنون \emph{مفاهیم برهان‌نظریِ} متناظر را تعریف
می‌کنیم. این مفاهیم نه با توسل به ارضای !!{sentence}s در
\iftag{FOL}{!!{structure}s}{!!{valuation}s}، بلکه با توسل به
!!{derivability} یا !!{nonderivability} برخی رشته‌ها تعریف می‌شوند.
کشف انطباق این مفاهیم اهمیتی بسیار داشت. این انطباق محتوای قضیه‌های
\emph{صحت} و \emph{تمامیت} است.
\end{explain}
```

</details>

### OLP-0077-P08

قضیه دقیقاً رشته با مقدم تهی و نتیجهٔ تنها A دارد؛ Proves/ نفی وجود اشتقاق است نه اثبات نفی A.
شواهد: H17-TREE, H14-SEQUENT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{defn}[Theorems]
!!^a{sentence}~$!A$ is a \emph{theorem} if there is !!a{derivation}
in~$\Log{LK}$ of the sequent $\quad \Sequent !A$.  We write $\Proves
!A$ if $!A$ is a theorem and $\Proves/ !A$ if it is not.
\end{defn}
```

ترجمهٔ فارسی:
```latex
\begin{defn}[قضایا]
!!^a{sentence}~$!A$ \emph{قضیه} است هرگاه در~$\Log{LK}$،
!!a{derivation}ی برای رشتهٔ $\quad \Sequent !A$ وجود داشته باشد.
$\Proves !A$ می‌نویسیم اگر $!A$ قضیه باشد، و اگر قضیه نباشد
$\Proves/ !A$ می‌نویسیم.
\end{defn}
```

</details>

### OLP-0077-P09

Γ دلخواه است؛ شاهد Γ0 متناهی و Γ0-prime توالی جمله‌های آن است. رابطهٔ از Γ اشتقاق‌پذیر با شیء اشتقاق تفاوت دارد.
شواهد: H14-SEQUENT, H17-TREE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{defn}[!!^{derivability}]
!!^a{sentence}~$!A$ is \emph{!!{derivable} from} a set of
!!{sentence}s~$\Gamma$, $\Gamma \Proves !A$, iff there is a
finite subset~$\Gamma_0 \subseteq \Gamma$ and a sequence $\Gamma_0'$
of the !!{sentence}s in~$\Gamma_0$ such that $\Log{LK}$ !!{derive}s
$\Gamma_0' \Sequent !A$.  If $!A$ is not !!{derivable} from $\Gamma$
we write $\Gamma \Proves/ !A$.
\end{defn}
```

ترجمهٔ فارسی:
```latex
\begin{defn}[!!^{derivability}]
برای !!^a{sentence}~$!A$، عبارت \emph{!!{derivable} از مجموعه‌ای از}
!!{sentence}s چون~$\Gamma$ را به کار می‌بریم، و
$\Gamma \Proves !A$ می‌نویسیم، اگر و تنها اگر
زیرمجموعهٔ متناهی~$\Gamma_0 \subseteq \Gamma$ و توالی‌ای چون
$\Gamma_0'$ از !!{sentence}s موجود در~$\Gamma_0$ وجود داشته باشد
به‌طوری‌که $\Log{LK}$، $\Gamma_0' \Sequent !A$ را !!{derive}s کند.
اگر $!A$ از $\Gamma$ !!{derivable} نباشد، $\Gamma \Proves/ !A$
می‌نویسیم.
\end{defn}
```

</details>

### OLP-0077-P10

ترتیب و تکرار با سه قاعدهٔ ساختاری قابل تغییرند؛ مجموعهٔ جمله‌ها ثابت است. مثال B,B,C به C,C,B با انقباض/تبادل/تضعیف حفظ شد. قرارداد نوشتن مجموعهٔ متناهی به جای توالی از این پس صریح است.
شواهد: H15-WEAKEN, H17-TREE, H14-SEQUENT.
اطمینان تحریری: 4 از ۴.
نیازمند بررسی: عبارت توالی جمله‌های Γ0 با جملهٔ قبل، شامل همان جمله‌ها خوانده می‌شود؛ مجوز حذف هر مقدمهٔ لازم نیست.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Because of the contraction, weakening, and exchange rules, the order
and number of !!{sentence}s in~$\Gamma_0'$ does not matter: if a
sequent $\Gamma_0' \Sequent !A$ is !!{derivable}, then so is
$\Gamma_0'' \Sequent !A$ for any $\Gamma_0''$ that contains the same
!!{sentence}s as~$\Gamma_0'$.  For instance, if $\Gamma_0 = \{!B, !C\}$
then both $\Gamma_0' = \tuple{!B, !B, !C}$ and $\Gamma_0'' =
\tuple{!C, !C, !B}$ are sequences containing just the !!{sentence}s
in~$\Gamma_0$. If a sequent containing one is !!{derivable}, so is the
other, e.g.:
\begin{prooftree}
  \AxiomC{}
  \Deduce$!B, !B, !C \fCenter !A$
  \RightLabel{\LeftR{\Contraction}}
  \UnaryInf$!B, !C \fCenter !A$
  \RightLabel{\LeftR{\Exchange}}
  \UnaryInf$!C, !B \fCenter !A$
  \RightLabel{\LeftR{\Weakening}}
  \UnaryInf$!C, !C, !B \fCenter !A$
\end{prooftree}
From now on we'll say that if $\Gamma_0$ is a finite set of
!!{sentence}s then $\Gamma_0 \Sequent !A$ is any sequent where the
antecedent is a sequence of !!{sentence}s in~$\Gamma_0$ and tacitly include
contractions, exchanges, and weakenings if necessary.
```

ترجمهٔ فارسی:
```latex
به سبب قواعد انقباض، تضعیف و تبادل، ترتیب و شمار !!{sentence}s در
~$\Gamma_0'$ اهمیتی ندارد: اگر رشتهٔ
$\Gamma_0' \Sequent !A$ !!{derivable} باشد، آنگاه
$\Gamma_0'' \Sequent !A$ نیز برای هر $\Gamma_0''$ که همان
!!{sentence}s موجود در~$\Gamma_0'$ را دربر دارد چنین است.
برای نمونه، اگر $\Gamma_0 = \{!B, !C\}$ باشد، آنگاه هم
$\Gamma_0' = \tuple{!B, !B, !C}$ و هم
$\Gamma_0'' = \tuple{!C, !C, !B}$ توالی‌هایی‌اند که دقیقاً
!!{sentence}s موجود در~$\Gamma_0$ را دربر دارند. اگر رشته‌ای که
یکی از آن‌ها را دربر دارد !!{derivable} باشد، رشتهٔ دیگر نیز چنین
است؛ برای نمونه:
\begin{prooftree}
  \AxiomC{}
  \Deduce$!B, !B, !C \fCenter !A$
  \RightLabel{\LeftR{\Contraction}}
  \UnaryInf$!B, !C \fCenter !A$
  \RightLabel{\LeftR{\Exchange}}
  \UnaryInf$!C, !B \fCenter !A$
  \RightLabel{\LeftR{\Weakening}}
  \UnaryInf$!C, !C, !B \fCenter !A$
\end{prooftree}
از این پس می‌گوییم اگر $\Gamma_0$ مجموعه‌ای متناهی از !!{sentence}s
باشد، آنگاه $\Gamma_0 \Sequent !A$ هر رشته‌ای است که مقدمش توالی‌ای
از !!{sentence}s موجود در~$\Gamma_0$ باشد؛ و در صورت لزوم انقباض‌ها،
تبادل‌ها و تضعیف‌ها را به‌طور ضمنی منظور می‌کنیم.
```

</details>

### OLP-0077-P11

ناسازگاری وجود شاهد متناهی برای نتیجهٔ تهی است؛ سازگاری نفی این وجود برای هر زیرمجموعهٔ متناهی است. ارضاپذیری در تعریف نحوی وارد نشده است.
شواهد: MT11-SAT, H14-SEQUENT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{defn}[Consistency]
A set of sentences~$\Gamma$ is \emph{inconsistent} iff there is a
finite subset~$\Gamma_0 \subseteq \Gamma$ such that $\Log{LK}$
!!{derive}s $\Gamma_0 \Sequent \quad$. If $\Gamma$ is not
inconsistent, i.e., if for every finite $\Gamma_0 \subseteq \Gamma$,
$\Log{LK}$ does not !!{derive} $\Gamma_0 \Sequent \quad$, we say it is
\emph{consistent}.
\end{defn}
```

ترجمهٔ فارسی:
```latex
\begin{defn}[سازگاری]
مجموعه‌ای از جمله‌ها چون~$\Gamma$ \emph{ناسازگار} است اگر و تنها اگر
زیرمجموعهٔ متناهی~$\Gamma_0 \subseteq \Gamma$ وجود داشته باشد
به‌طوری‌که $\Log{LK}$، $\Gamma_0 \Sequent \quad$ را !!{derive}s کند.
اگر $\Gamma$ ناسازگار نباشد، یعنی اگر برای هر
$\Gamma_0 \subseteq \Gamma$ متناهی، $\Log{LK}$،
$\Gamma_0 \Sequent \quad$ را !!{derive} نکند، می‌گوییم
\emph{سازگار} است.
\end{defn}
```

</details>

### OLP-0077-P12

عضویت A در Γ نتیجهٔ Γ⊢A می‌دهد.
شواهد: H17-TREE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: بازتابی نام این خاصیت است؛ شاهد لفظیِ خاص این کاربرد در صفحات حاضر ادعا نمی‌شود.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}[Reflexivity]
\ollabel{prop:reflexivity}
If $!A \in \Gamma$, then $\Gamma \Proves !A$.
\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop}[بازتابی]
\ollabel{prop:reflexivity}
اگر $!A \in \Gamma$، آنگاه $\Gamma \Proves !A$.
\end{prop}
```

</details>

### OLP-0077-P13

شاهد تک‌عضوی {A} و رشتهٔ آغازین A⇒A دقیقاً شرطِ تعریف را برآورده می‌کنند.
شواهد: H14-SEQUENT, H17-TREE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
The initial sequent $!A \Sequent !A$ is !!{derivable}, and $\{!A\}
\subseteq \Gamma$.
\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
رشتهٔ آغازینِ $!A \Sequent !A$ !!{derivable} است و
$\{!A\} \subseteq \Gamma$.
\end{proof}
```

</details>

### OLP-0077-P14

یکنوایی فقط افزودن فرض‌هاست؛ جهتِ شامل‌بودن Γ⊆Δ حفظ است.
شواهد: H17-TREE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: یکنوایی در این کاننِ خاص شاهد لفظی مستقیم ندارد؛ گزاره تعریفش را تعیین می‌کند.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}[Monotonicity]
\ollabel{prop:monotonicity}
If $\Gamma \subseteq \Delta$ and $\Gamma \Proves !A$, then $\Delta
\Proves !A$.
\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop}[یکنوایی]
\ollabel{prop:monotonicity}
اگر $\Gamma \subseteq \Delta$ و $\Gamma \Proves !A$، آنگاه
$\Delta \Proves !A$.
\end{prop}
```

</details>

### OLP-0077-P15

همان Γ0 متناهی در Δ نیز جا دارد؛ برهانِ Γ0⇒A بدون تغییر شاهدِ Δ⊢A است.
شواهد: H14-SEQUENT, H17-TREE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
Suppose $\Gamma \Proves !A$, i.e., there is a finite $\Gamma_0
\subseteq \Gamma$ such that $\Gamma_0 \Sequent !A$ is
!!{derivable}. Since $\Gamma \subseteq \Delta$, then $\Gamma_0$ is
also a finite subset of~$\Delta$. The !!{derivation} of $\Gamma_0
\Sequent !A$ thus also shows $\Delta \Proves !A$.
\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
فرض کنید $\Gamma \Proves !A$؛ یعنی $\Gamma_0 \subseteq \Gamma$
متناهی‌ای وجود دارد که $\Gamma_0 \Sequent !A$ !!{derivable} است.
چون $\Gamma \subseteq \Delta$، پس $\Gamma_0$ زیرمجموعه‌ای متناهی
از~$\Delta$ نیز هست. بنابراین !!{derivation} مربوط به
$\Gamma_0 \Sequent !A$ همچنین $\Delta \Proves !A$ را نشان می‌دهد.
\end{proof}
```

</details>

### OLP-0077-P16

تعدی با Γ⊢A و {A}∪Δ⊢B، نتیجهٔ Γ∪Δ⊢B دارد؛ اجتماع به اشتراک تبدیل نشده است.
شواهد: H17-TREE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}[Transitivity]
\ollabel{prop:transitivity}
If $\Gamma \Proves !A$ and $\{!A\} \cup \Delta \Proves
!B$, then $\Gamma \cup \Delta \Proves !B$.
\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop}[تعدی]
\ollabel{prop:transitivity}
اگر $\Gamma \Proves !A$ و $\{!A\} \cup \Delta \Proves !B$، آنگاه
$\Gamma \cup \Delta \Proves !B$.
\end{prop}
```

</details>

### OLP-0077-P17

دو شاهد متناهی با برش روی A ترکیب می‌شوند؛ اگر A در شاهدِ دوم نبود، تضعیف آن را می‌افزاید. اجتماع دو شاهد متناهی در اجتماع دو مجموعهٔ اصلی جا دارد.
شواهد: H17-TREE, H15-WEAKEN.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
If $\Gamma \Proves !A$, there is a finite $\Gamma_0 \subseteq \Gamma$
and !!a{derivation}~$\pi_0$ of $\Gamma_0 \Sequent !A$.  If $\{!A\}
\cup \Delta \Proves !B$, then for some finite subset $\Delta_0
\subseteq \Delta$, there is !!a{derivation}~$\pi_1$ of $!A, \Delta_0
\Sequent !B$. Consider the following !!{derivation}:
\begin{prooftree}
  \AxiomC{}
  \RightLabel{$\pi_0$}
  \Deduce$\Gamma_0 \fCenter !A$
  \AxiomC{}
  \RightLabel{$\pi_1$}
  \Deduce$!A, \Delta_0 \fCenter !B$
  \RightLabel{\Cut}
  \BinaryInf$\Gamma_0, \Delta_0 \fCenter !B$
\end{prooftree}
Since $\Gamma_0 \cup \Delta_0 \subseteq \Gamma \cup \Delta$, this
shows $\Gamma \cup \Delta \Proves !B$.
\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
اگر $\Gamma \Proves !A$، آنگاه مجموعهٔ متناهی
$\Gamma_0 \subseteq \Gamma$ و !!a{derivation}~$\pi_0$ برای
$\Gamma_0 \Sequent !A$ وجود دارند. اگر
$\{!A\} \cup \Delta \Proves !B$، آنگاه برای زیرمجموعهٔ متناهی‌ای چون
$\Delta_0 \subseteq \Delta$، !!a{derivation}~$\pi_1$ برای
$!A, \Delta_0 \Sequent !B$ وجود دارد. !!{derivation} زیر را در نظر
بگیرید:
\begin{prooftree}
  \AxiomC{}
  \RightLabel{$\pi_0$}
  \Deduce$\Gamma_0 \fCenter !A$
  \AxiomC{}
  \RightLabel{$\pi_1$}
  \Deduce$!A, \Delta_0 \fCenter !B$
  \RightLabel{\Cut}
  \BinaryInf$\Gamma_0, \Delta_0 \fCenter !B$
\end{prooftree}
چون $\Gamma_0 \cup \Delta_0 \subseteq \Gamma \cup \Delta$، این
نشان می‌دهد $\Gamma \cup \Delta \Proves !B$.
\end{proof}
```

</details>

### OLP-0077-P18

دو نتیجهٔ خاصِ جایگزینی یک فرض و سپس n فرض اثبات‌شده حفظ‌اند؛ برای هر i قید ضروری است.
شواهد: H17-TREE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Note that this means that in particular if $\Gamma \Proves !A$ and $!A
\Proves !B$, then $\Gamma \Proves !B$. It follows also that if $!A_1,
\dots, !A_n \Proves !B$ and $\Gamma \Proves !A_i$ for each~$i$, then
$\Gamma \Proves !B$.
```

ترجمهٔ فارسی:
```latex
توجه کنید که این به‌ویژه بدان معناست که اگر $\Gamma \Proves !A$ و
$!A \Proves !B$، آنگاه $\Gamma \Proves !B$. همچنین نتیجه می‌شود که
اگر $!A_1, \dots, !A_n \Proves !B$ و $\Gamma \Proves !A_i$ برای
هر~$i$، آنگاه $\Gamma \Proves !B$.
```

</details>

### OLP-0077-P19

ناسازگاری با اثبات هر جمله هم‌ارز است؛ هر با برخی عوض نشده است.
شواهد: H14-SEQUENT, H17-TREE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}
\ollabel{prop:incons}
$\Gamma$ is inconsistent iff $\Gamma \Proves {!A}$ for every
  sentence~$!A$.
\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop}
\ollabel{prop:incons}
$\Gamma$ ناسازگار است اگر و تنها اگر $\Gamma \Proves {!A}$ برای هر
جملهٔ~$!A$.
\end{prop}
```

</details>

### OLP-0077-P20

جای برهان عمداً تمرین است؛ پاسخ تازه‌ای به متن افزوده نشده است.
شواهد: H17-TREE.
اطمینان تحریری: 3 از ۴.

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

### OLP-0077-P21

ارجاع صریح fol در هر دو نسخهٔ بومی حفظ شد؛ به گزارهٔ همان محتوا در قسمت مرتبهٔ اول می‌رود.
شواهد: H17-TREE.
اطمینان تحریری: 2 از ۴.
نیازمند بررسی: بهتر است ارجاع هر زمینه به گزارهٔ محلی خودش برود؛ نیازمند بررسی مقصدِ واقعی صادرکننده است و فعلاً به عنوان اصلاحِ تأییدشده اجرا نشد.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob}
Prove \olref[fol][seq][ptn]{prop:incons}
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob}
\olref[fol][seq][ptn]{prop:incons} را ثابت کنید.
\end{prob}
```

</details>

### OLP-0077-P22

دو ادعای فشردگی نحوی‌اند: شاهد متناهیِ اثبات و سازگاری مجموعه اگر همهٔ زیرمجموعه‌های متناهی سازگارند. با قضیهٔ فشردگی معناشناختیِ اثبات‌نشده خلط نشد.
شواهد: MT11-SAT, H17-TREE.
اطمینان تحریری: 3 از ۴.
نیازمند بررسی: فشردگی معادل موجود است؛ صفحات مدل‌نظری خوانده‌شده در این دور نام آن را مستقلاً تثبیت نمی‌کنند.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}[Compactness]
  \ollabel{prop:proves-compact}
  \begin{enumerate}
  \item If $\Gamma \Proves !A$ then there is a finite subset $\Gamma_0
    \subseteq \Gamma$ such that $\Gamma_0 \Proves !A$.
  \item If every finite subset of~$\Gamma$ is
    consistent, then $\Gamma$ is consistent.
  \end{enumerate}
\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop}[فشردگی]
  \ollabel{prop:proves-compact}
  \begin{enumerate}
  \item اگر $\Gamma \Proves !A$، آنگاه زیرمجموعهٔ متناهی
    $\Gamma_0 \subseteq \Gamma$ وجود دارد که $\Gamma_0 \Proves !A$.
  \item اگر هر زیرمجموعهٔ متناهیِ~$\Gamma$ سازگار باشد، آنگاه
    $\Gamma$ سازگار است.
  \end{enumerate}
\end{prop}
```

</details>

### OLP-0077-P23

بخش اول از تعریف شاهد و بخش دوم از عکس نقیض تعریف ناسازگاری نتیجه می‌شوند؛ قید متناهی در هر دو محفوظ است.
شواهد: H14-SEQUENT, H17-TREE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
  \begin{enumerate}
    \item If $\Gamma \Proves !A$, then there is a finite subset
      $\Gamma_0 \subseteq \Gamma$ such that the sequent $\Gamma_0
      \Sequent !A$ has !!a{derivation}. Consequently, $\Gamma_0
      \Proves !A$.
    \item If $\Gamma$ is inconsistent, there is a finite
      subset~$\Gamma_0 \subseteq \Gamma$ such that $\Log{LK}$
      !!{derive}s $\Gamma_0 \Sequent \quad$. But then $\Gamma_0$ is a
      finite subset of~$\Gamma$ that is inconsistent.
  \end{enumerate}
\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
  \begin{enumerate}
    \item اگر $\Gamma \Proves !A$، آنگاه زیرمجموعهٔ متناهی
      $\Gamma_0 \subseteq \Gamma$ وجود دارد که رشتهٔ
      $\Gamma_0 \Sequent !A$ دارای !!a{derivation} است. در نتیجه،
      $\Gamma_0 \Proves !A$.
    \item اگر $\Gamma$ ناسازگار باشد، زیرمجموعهٔ متناهی
      ~$\Gamma_0 \subseteq \Gamma$ وجود دارد که $\Log{LK}$،
      $\Gamma_0 \Sequent \quad$ را !!{derive}s می‌کند. اما در این صورت،
      $\Gamma_0$ زیرمجموعه‌ای متناهی و ناسازگار از~$\Gamma$ است.
  \end{enumerate}
\end{proof}
```

</details>

### OLP-0078-P04

شناسهٔ دو بافت محفوظ است.
شواهد: کنترل ساختاری؛ شاهد اصطلاح‌شناختی لازم نیست.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\iftag{FOL}
      {\olfileid{fol}{seq}{prv}}
      {\olfileid{pl}{seq}{prv}}
```

ترجمهٔ فارسی:
```latex
\iftag{FOL}
      {\olfileid{fol}{seq}{prv}}
      {\olfileid{pl}{seq}{prv}}
```

</details>

### OLP-0078-P05

اشتقاق‌پذیری و سازگاری دو مفهوم نحویِ بخش پیش‌اند؛ نام‌ها یکدست‌اند.
شواهد: H17-TREE, MT11-SAT.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\olsection{\usetoken{S}{derivability} and Consistency}
```

ترجمهٔ فارسی:
```latex
\olsection{\usetoken{S}{derivability} و سازگاری}
```

</details>

### OLP-0078-P06

نقش این خواص در اثبات تمامیت به‌عنوان هدف بعدی حفظ است؛ ادعای اثبات تمامیت در همین بخش افزوده نشد.
شواهد: H16-COMPLETE, H17-TREE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
We will now establish a number of properties of the !!{derivability}
relation.  They are independently interesting, but each will play a
role in the proof of the completeness theorem.
```

ترجمهٔ فارسی:
```latex
اکنون چند ویژگیِ رابطهٔ !!{derivability} را اثبات می‌کنیم. این
ویژگی‌ها مستقلاً جالب‌اند، اما هر یک در اثبات قضیهٔ تمامیت نقشی
خواهند داشت.
```

</details>

### OLP-0078-P07

اگر A از Γ به دست آید و افزودن A ناسازگار باشد، Γ نیز ناسازگار است؛ هر دو فرض حفظ‌اند.
شواهد: H14-SEQUENT, H17-TREE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}\ollabel{prop:provability-contr}
  If $\Gamma \Proves !A$ and $\Gamma \cup \{!A\}$ is
  inconsistent, then $\Gamma$ is inconsistent.
\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop}\ollabel{prop:provability-contr}
  اگر $\Gamma \Proves !A$ و $\Gamma \cup \{!A\}$ ناسازگار باشد،
  آنگاه $\Gamma$ ناسازگار است.
\end{prop}
```

</details>

### OLP-0078-P08

دو شاهد متناهی با برش روی A نتیجهٔ تهی می‌دهند؛ تغییر ترتیب Γ1,A در نثر و A,Γ1 در نمودار با قرارداد تبادل ضمنیِ ۰۰۷۷ مجاز است و خطا نامیده نشد.
شواهد: H17-TREE, H14-SEQUENT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
There are finite $\Gamma_0$ and $\Gamma_1 \subseteq \Gamma$ such that
$\Log{LK}$ !!{derive}s $\Gamma_0 \Sequent !A$ and $!A, \Gamma_1
\Sequent \quad$.  Let the $\Log{LK}$-!!{derivation} of $\Gamma_0 \Sequent
!A$ be~$\pi_0$ and the $\Log{LK}$-!!{derivation} of $\Gamma_1, !A
\Sequent \quad$ be~$\pi_1$. We can then !!{derive}
\begin{prooftree}
\AxiomC{}
\RightLabel{$\pi_0$}
\Deduce$ \Gamma_0 \fCenter !A $
\AxiomC{}
\RightLabel{$\pi_1$}
\Deduce$!A, \Gamma_1 \fCenter $
\RightLabel{\Cut}
\BinaryInf$ \Gamma_0,\Gamma_1 \fCenter $
\end{prooftree}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
$\Gamma_0$ و $\Gamma_1 \subseteq \Gamma$ متناهی‌ای وجود دارند
به‌طوری‌که $\Log{LK}$، $\Gamma_0 \Sequent !A$ و
$!A, \Gamma_1 \Sequent \quad$ را !!{derive}s می‌کند. فرض کنید
$\Log{LK}$-!!{derivation} برای $\Gamma_0 \Sequent !A$ همان~$\pi_0$
و $\Log{LK}$-!!{derivation} برای $\Gamma_1, !A \Sequent \quad$
همان~$\pi_1$ باشد. آنگاه می‌توانیم عبارت زیر را !!{derive} کنیم:
\begin{prooftree}
\AxiomC{}
\RightLabel{$\pi_0$}
\Deduce$ \Gamma_0 \fCenter !A $
\AxiomC{}
\RightLabel{$\pi_1$}
\Deduce$!A, \Gamma_1 \fCenter $
\RightLabel{\Cut}
\BinaryInf$ \Gamma_0,\Gamma_1 \fCenter $
\end{prooftree}
```

</details>

### OLP-0078-P09

اجتماع دو زیرمجموعهٔ متناهی شاهد ناسازگاری Γ است؛ هر دو رابطهٔ شمول حفظ‌اند.
شواهد: H14-SEQUENT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
Since $\Gamma_0 \subseteq \Gamma$ and $\Gamma_1 \subseteq \Gamma$,
$\Gamma_0 \cup \Gamma_1 \subseteq \Gamma$, hence $\Gamma$~is inconsistent.
\end{proof}
```

ترجمهٔ فارسی:
```latex
چون $\Gamma_0 \subseteq \Gamma$ و $\Gamma_1 \subseteq \Gamma$،
$\Gamma_0 \cup \Gamma_1 \subseteq \Gamma$؛ پس $\Gamma$~ناسازگار است.
\end{proof}
```

</details>

### OLP-0078-P10

هم‌ارزی Γ⊢A با ناسازگاری افزودن ¬A حفظ است؛ جای نفی در مجموعهٔ افزوده تغییر نکرد.
شواهد: MT11-SAT, H17-TREE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}
\ollabel{prop:prov-incons}
$\Gamma \Proves !A$ iff $\Gamma \cup \{\lnot !A\}$ is inconsistent.
\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop}
\ollabel{prop:prov-incons}
$\Gamma \Proves !A$ اگر و تنها اگر
$\Gamma \cup \{\lnot !A\}$ ناسازگار باشد.
\end{prop}
```

</details>

### OLP-0078-P11

جهت اول اکنون Γ0 متناهی را صریح دارد. نفی چپ از Γ0⇒A نتیجهٔ تهی با ¬A می‌دهد؛ این شاهدی در Γ∪{¬A} است.
شواهد: H14-SEQUENT, H17-TREE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
First suppose $\Gamma \Proves !A$, i.e., there is
!!a{derivation}~$\pi_0$ of $\Gamma \Sequent !A$. By adding a
$\LeftR{\lnot}$ rule, we obtain !!a{derivation} of~$\lnot !A, \Gamma
\Sequent \quad$, i.e., $\Gamma \cup \{\lnot !A\}$ is inconsistent.
```

ترجمهٔ فارسی:
```latex
\begin{proof}
نخست فرض کنید $\Gamma \Proves !A$. زیرمجموعه‌ای متناهی
$\Gamma_0 \subseteq \Gamma$ و !!a{derivation}~$\pi_0$ برای
$\Gamma_0 \Sequent !A$ وجود دارند. با افزودن قاعدهٔ
$\LeftR{\lnot}$، !!a{derivation} برای~$\lnot !A, \Gamma_0
\Sequent \quad$ به دست می‌آوریم؛ پس $\Gamma \cup \{\lnot !A\}$ ناسازگار است.
```

</details>

### OLP-0078-P12

جهت عکس شاهد متناهی Γ0 و π1 را از تعریف می‌گیرد؛ A⇒A با نفی راست به ⇒A,¬A می‌رود و برش، Γ0⇒A می‌دهد. سپس تعریفِ رابطه نتیجهٔ Γ⊢A را می‌دهد.
شواهد: H14-SEQUENT, H17-TREE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
If $\Gamma \cup \{\lnot !A\}$ is inconsistent, there is
!!a{derivation}~$\pi_1$ of $\lnot !A, \Gamma \Sequent \quad$. The
following is !!a{derivation} of $\Gamma \Sequent !A$:
\begin{prooftree}
  \Axiom$!A \fCenter !A$
  \RightLabel{\RightR{\lnot}}
  \UnaryInf$\fCenter !A, \lnot !A$
  \AxiomC{}
  \RightLabel{$\pi_1$}
  \Deduce$\lnot !A, \Gamma \fCenter$
  \RightLabel{\Cut}
  \BinaryInf$\Gamma \fCenter !A$
\end{prooftree}
\end{proof}
```

ترجمهٔ فارسی:
```latex
اگر $\Gamma \cup \{\lnot !A\}$ ناسازگار باشد، زیرمجموعه‌ای متناهی
$\Gamma_0 \subseteq \Gamma$ و !!a{derivation}~$\pi_1$ برای
$\lnot !A, \Gamma_0 \Sequent \quad$ وجود دارند. عبارت زیر
!!a{derivation} برای $\Gamma_0 \Sequent !A$ است:
\begin{prooftree}
  \Axiom$!A \fCenter !A$
  \RightLabel{\RightR{\lnot}}
  \UnaryInf$\fCenter !A, \lnot !A$
  \AxiomC{}
  \RightLabel{$\pi_1$}
  \Deduce$\lnot !A, \Gamma_0 \fCenter$
  \RightLabel{\Cut}
  \BinaryInf$\Gamma_0 \fCenter !A$
\end{prooftree}
بنابراین $\Gamma \Proves !A$.
\end{proof}
```

</details>

### OLP-0078-P13

صورت تمرین برای Γ⊢¬A و افزودن A دقیقاً حفظ است؛ حل به جای تمرین اضافه نشد.
شواهد: MT9-CONNECTIVES, H17-TREE.
اطمینان تحریری: 3 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prob}
Prove that $\Gamma \Proves \lnot !A$ iff $\Gamma \cup \{!A\}$ is inconsistent.
\end{prob}
```

ترجمهٔ فارسی:
```latex
\begin{prob}
ثابت کنید $\Gamma \Proves \lnot !A$ اگر و تنها اگر
$\Gamma \cup \{!A\}$ ناسازگار باشد.
\end{prob}
```

</details>

### OLP-0078-P14

فرض دوم عضویتِ ¬A در Γ است، نه صرفاً اشتقاق‌پذیریِ آن؛ صورت قضیه حفظ شد.
شواهد: MT9-CONNECTIVES, H17-TREE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}\ollabel{prop:explicit-inc}
  If $\Gamma \Proves !A$ and $\lnot !A \in \Gamma$, then $\Gamma$ is
  inconsistent.
\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop}\ollabel{prop:explicit-inc}
  اگر $\Gamma \Proves !A$ و $\lnot !A \in \Gamma$، آنگاه
  $\Gamma$ ناسازگار است.
\end{prop}
```

</details>

### OLP-0078-P15

تعریف Γ⊢A شاهد متناهی Γ0 را می‌دهد؛ درخت با نفی چپ، تبادل و برش نتیجهٔ تهی می‌سازد. دو ترتیب Γ0,¬A و ¬A,Γ0 به قرارداد تبادل ضمنی مربوط‌اند.
شواهد: H17-TREE, H14-SEQUENT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
  Suppose $\Gamma \Proves !A$ and $\lnot !A \in \Gamma$.  Then there
  is !!a{derivation}~$\pi$ of a sequent $\Gamma_0 \Sequent !A$. The
  sequent $\lnot !A, \Gamma_0 \Sequent \quad$ is also !!{derivable}:
  \begin{prooftree}
    \AxiomC{}
    \RightLabel{$\pi$}
    \Deduce$\Gamma_0 \fCenter !A$
    \Axiom$!A \fCenter !A$
    \RightLabel{\LeftR{\lnot}}
    \UnaryInf$\lnot !A, !A \fCenter$
    \RightLabel{\LeftR{\Exchange}}
    \UnaryInf$!A, \lnot !A \fCenter$
    \RightLabel{\Cut}
    \BinaryInf$\Gamma_0, \lnot !A \fCenter$
  \end{prooftree}
  Since $\lnot !A \in \Gamma$ and $\Gamma_0 \subseteq \Gamma$, this
  shows that $\Gamma$ is inconsistent.
\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
  فرض کنید $\Gamma \Proves !A$ و $\lnot !A \in \Gamma$. آنگاه
  !!a{derivation}~$\pi$ برای رشتهٔ $\Gamma_0 \Sequent !A$ وجود
  دارد. رشتهٔ $\lnot !A, \Gamma_0 \Sequent \quad$ نیز
  !!{derivable} است:
  \begin{prooftree}
    \AxiomC{}
    \RightLabel{$\pi$}
    \Deduce$\Gamma_0 \fCenter !A$
    \Axiom$!A \fCenter !A$
    \RightLabel{\LeftR{\lnot}}
    \UnaryInf$\lnot !A, !A \fCenter$
    \RightLabel{\LeftR{\Exchange}}
    \UnaryInf$!A, \lnot !A \fCenter$
    \RightLabel{\Cut}
    \BinaryInf$\Gamma_0, \lnot !A \fCenter$
  \end{prooftree}
  چون $\lnot !A \in \Gamma$ و $\Gamma_0 \subseteq \Gamma$، این
  نشان می‌دهد که $\Gamma$ ناسازگار است.
\end{proof}
```

</details>

### OLP-0078-P16

ناسازگاریِ هر دو افزودن A و ¬A لازم است؛ یا جای و ننشسته است.
شواهد: MT9-CONNECTIVES, H17-TREE.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{prop}\ollabel{prop:provability-exhaustive}
  If $\Gamma \cup \{!A\}$ and $\Gamma \cup \{\lnot !A\}$ are both
  inconsistent, then $\Gamma$ is inconsistent.
\end{prop}
```

ترجمهٔ فارسی:
```latex
\begin{prop}\ollabel{prop:provability-exhaustive}
  اگر $\Gamma \cup \{!A\}$ و $\Gamma \cup \{\lnot !A\}$ هر دو
  ناسازگار باشند، آنگاه $\Gamma$ ناسازگار است.
\end{prop}
```

</details>

### OLP-0078-P17

دو شاهد متناهی، نفی راست در شاخهٔ نخست و برش روی ¬A نتیجهٔ تهی می‌دهند؛ اجتماع شاهدها همچنان زیرمجموعهٔ متناهی Γ است.
شواهد: H17-TREE, H14-SEQUENT.
اطمینان تحریری: 4 از ۴.

<details><summary>متن منبع و ترجمهٔ بررسی‌شده</summary>

منبع انگلیسی:
```latex
\begin{proof}
There are finite sets $\Gamma_0 \subseteq \Gamma$ and $\Gamma_1
\subseteq \Gamma$ and $\Log{LK}$-!!{derivation}s $\pi_0$ and $\pi_1$
of $!A, \Gamma_0 \Sequent \quad$ and $\lnot !A, \Gamma_1 \Sequent
\quad$, respectively. We can then !!{derive}
\begin{prooftree}
\AxiomC{}
\RightLabel{$\pi_0$}
\Deduce$ !A, \Gamma_0 \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$ \Gamma_0 \fCenter \lnot !A$
\AxiomC{}
\RightLabel{$\pi_1$}
\Deduce$\lnot !A, \Gamma_1 \fCenter  $
\RightLabel{\Cut}
\BinaryInf$ \Gamma_0, \Gamma_1 \fCenter $
\end{prooftree}
Since $\Gamma_0 \subseteq \Gamma$ and $\Gamma_1 \subseteq \Gamma$,
$\Gamma_0 \cup \Gamma_1 \subseteq \Gamma$. Hence $\Gamma$ is
inconsistent.
\end{proof}
```

ترجمهٔ فارسی:
```latex
\begin{proof}
مجموعه‌های متناهی $\Gamma_0 \subseteq \Gamma$ و
$\Gamma_1 \subseteq \Gamma$ و $\Log{LK}$-!!{derivation}s
$\pi_0$ و $\pi_1$ به‌ترتیب برای
$!A, \Gamma_0 \Sequent \quad$ و
$\lnot !A, \Gamma_1 \Sequent \quad$ وجود دارند. آنگاه می‌توانیم
عبارت زیر را !!{derive} کنیم:
\begin{prooftree}
\AxiomC{}
\RightLabel{$\pi_0$}
\Deduce$ !A, \Gamma_0 \fCenter $
\RightLabel{\RightR{\lnot}}
\UnaryInf$ \Gamma_0 \fCenter \lnot !A$
\AxiomC{}
\RightLabel{$\pi_1$}
\Deduce$\lnot !A, \Gamma_1 \fCenter  $
\RightLabel{\Cut}
\BinaryInf$ \Gamma_0, \Gamma_1 \fCenter $
\end{prooftree}
چون $\Gamma_0 \subseteq \Gamma$ و $\Gamma_1 \subseteq \Gamma$،
$\Gamma_0 \cup \Gamma_1 \subseteq \Gamma$. بنابراین $\Gamma$
ناسازگار است.
\end{proof}
```

</details>

## یافته‌های تکمیلی و حدود بازبینی

دو نفیِ افتاده در مثال سوم ۰۰۷۵ و شاهد متناهیِ دو بند ۰۰۷۸ با پیش‌تصویر دقیق اصلاح شدند. چهار نام قاعدهٔ تبادل در ۰۰۷۵ و یادداشت natural deduction در ۰۰۷۷ از قبل در فارسی اصلاح بودند و نگهداری شدند. صورت فارسیِ شاخهٔ PL در تعریف معناشناختی از قبل ارزش‌گذاری دارد؛ این تفاوت درست با ساختارِ FOL حفظ شد. گزارش‌های قدیمیِ نفی‌ها و برچسب‌های تبادل در فهرست مرکزی پیدا شدند؛ هیچ ادعای کشف مستقل تازه یا مسئلهٔ تکراری برای مؤلف مطرح نمی‌شود. ارجاعِ صریح fol در ۰۰۷۷ به عنوان نیازمند بررسی مقصد ثبت است، نه اصلاحِ اجراشده. نام‌های بدون شاهد اختصاصی با اطمینان محدود نگه داشته می‌شوند. ساخت/انتشار تازه در این بازبینی انجام نمی‌شود؛ اصلاح‌ها برای جمع‌شدن با آغاز فصل‌اند.
 
## منابع و حدود استناد

### MT

مسعود پورمهدیان و محسن خانی، مباحثی در منطق، دانشگاه صنعتی امیرکبیر، ۱۵ بهمن ۱۳۹۵؛ جلسهٔ مقدماتی

https://mohsen-khani.github.io/modeltheory/jozve1.pdf

نسخهٔ نویسندگان در صفحهٔ دوره؛ سند فارسیِ منطق مرتبهٔ اول است، نه شاهد اختصاصی همهٔ اصطلاح‌های منطق گزاره‌ای. فقط مطالعهٔ محلی، نقل کوتاه و ارجاع؛ PDF در انتشار عمومی قرار نمی‌گیرد.

### HOSSEINI

داود حسینی، حساب رشتۀ سطح بالاتر برای منطق ناسرۀ ابتنای دروست و فاین، منطق‌پژوهی ۱۵(۲)، ۱۴۰۳، صص ۲۲۱–۲۳۸

https://logicalstudy.ihcs.ac.ir/article_10146_f52a7b2610fb4d3f74b4106fb80b233d.pdf

نشان CC BY در صفحهٔ فارسی مقاله دیده شد؛ نسخهٔ مجوز در نشان مشخص نیست. این بسته فقط نقل‌های کوتاه و ارجاع را همراه دارد؛ PDF کانن در بستهٔ خواننده کپی نمی‌شود.

- MT9-SYNTAX: «نحو»؛ صفحهٔ فایل 9، چاپی 9. عنوان نحو و پانوشت syntax؛ نماد، متغیر، پرانتز باز و بسته و تعریف فرمول در همان صفحه خوانده شد. شاهدی برای نحو است، نه گواهی خودکار تمام معادل‌های متن.
- MT9-CONNECTIVES: «ادوات بولی یا گزاره‌ای»؛ صفحهٔ فایل 9، چاپی 9. پنج رابط گزاره‌ای در بافت صوری معرفی می‌شوند. رابط در ترجمه از ادوات در این شاهد متفاوت است؛ معنای آن با فهرست نمادها و شرح منبع سنجیده شد و انحصار یک معادل ادعا نمی‌شود.
- MT9-ATOMIC: «فرمولهای بسیط (یا اتمیک)»؛ صفحهٔ فایل 9، چاپی 9. تعریف ۱۱ و ادامهٔ آن در صفحهٔ ۱۰ مبنای مقابلهٔ حالت پایه، ساخت استقرایی و شرط انحصارند. این شاهد، فرمول اتمی را از متغیر تنها و جملهٔ بدون متغیر آزاد متمایز می‌کند.
- MT10-SEMANTICS: «به صورت استقرایی»؛ صفحهٔ فایل 10، چاپی 10. تعریف صدق در ساختار و شروط نفی و عطف واقعاً خوانده شد؛ نثر نسبت‌دادن معنا و ساختار استقرایی را پشتیبانی می‌کند. ارزش‌گذاری گزاره‌ای با تعبیر مرتبهٔ اول یکی نیست و از این شاهد چنین همانی‌ای نتیجه نمی‌شود.
- MT11-SAT: «ارضاشدنی»؛ صفحهٔ فایل 11، چاپی 11. تعریف ارضاشدنی با وجود مدل برای تمام جمله‌های نظریه و پانوشت satisfiable؛ در ترجمه ارضاپذیر حفظ شد. تمایز وجود یک ارزش‌گذاری مشترک با ارزش‌گذاری جدا برای هر فرمول بررسی شد.
- H14-SEQUENT: «حساب رشتۀ سطح بالاتر»؛ صفحهٔ فایل 14، چاپی 234. نام حساب و توضیح صریح نقش رشته و دستگاه؛ با حذف قید سطح بالاتر، نام حساب کلاسیک را از منطق خاص مقاله متمایز می‌کنیم.
- H14-AXIOM: «اصل موضوع»؛ صفحهٔ فایل 14، چاپی 234. تمایز اصل موضوع از قاعده و ساخت درختی اشتقاق در ابتدای بخش چهارم.
- H15-WEAKEN: «تضعیف»؛ صفحهٔ فایل 15، چاپی 235. نام فارسی Weakening در توضیح زیر قواعد؛ کاربرد راست/چپ را خود OpenLogic تعیین می‌کند.
- H16-COMPLETE: «صحیح و تام»؛ صفحهٔ فایل 16، چاپی 236. صفت‌های متناظر با صحت و تمامیت در انتهای استدلال هم‌ارزی.
- H17-TREE: «درخت متشکل از قاعده‌ها»؛ صفحهٔ فایل 17، چاپی 237. بیان نحویِ اشتقاق؛ تمایز قاعدهٔ استنتاج و رابطهٔ استنتاج در متن کامل همین بند خوانده شد.
- MT10-FREE-BOUND: «متغیرهای آزاد»؛ صفحهٔ فایل 10، چاپی 10. بند بالای عنوان تئوری صدق تارسکی، رخداد آزاد و مقید و امکان حضور هر دو برای یک متغیر را توضیح می‌دهد؛ این شاهد برای تمایز ترم، فرمول و جانشینی است، نه گواه لفظ متغیر ویژه.

## وضعیت انتشار

در دامنهٔ ثبت‌شده، تغییر فرمول یا ارجاع فقط با پیش‌تصویر و دلیل صریح مجاز است؛ تفاوت‌های مجاز بالا ثبت شده‌اند و ساختار محیط‌ها و ورودی‌ها حفظ شده است. ساخت خواننده و بازبینی دیداری آن در این نوبت انجام نشد. این گزارش به‌خودی‌خود رسید انتشار نیست. شواهد خصوصیِ فاقد مجوز نباید در بستهٔ عمومی بازنشر شوند.
