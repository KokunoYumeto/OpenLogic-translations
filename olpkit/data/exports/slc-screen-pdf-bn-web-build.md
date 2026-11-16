# সেট, যুক্তি, গণনা — HTML, EPUB ও PDF তৈরি

এই উৎস-প্যাকেজে বইটির সম্পাদনযোগ্য LaTeX ফাইল, চিত্র, ফন্ট, তথ্যসূত্র এবং HTML ও EPUB তৈরির প্রোগ্রাম আছে। বইয়ের শুরুতে মূল লেখক, অনুবাদ ও চিত্রের স্বীকৃতি এবং ব্যবহারের শর্ত দেওয়া আছে। ছবি ও ফন্টের নিজস্ব লাইসেন্সও উৎসের সঙ্গে আছে।

## HTML ও EPUB

ZIP ফাইলটি একটি খালি ফোল্ডারে খুলুন। সেখানে `rebuild_web.py` ফাইলটি পাবেন। বইটির এই সংস্করণ তৈরিতে Python 3.13, Pandoc 3.9.0.2, Poppler-এর `pdftocairo` এবং Java 21 ব্যবহার করা হয়েছে। EPUB যাচাই করতে EPUBCheck 5.3.0-এর সম্পূর্ণ প্যাকেজটি খুলে রাখুন। `epubcheck.jar` ও তার `lib` ফোল্ডারটি পাশাপাশি থাকা দরকার।

PowerShell-এ উৎসের মূল ফোল্ডার থেকে চালান

    python -m venv .venv
    ./.venv/Scripts/python -m pip install -r requirements.txt
    ./.venv/Scripts/python rebuild_web.py --epubcheck-jar ../epubcheck-5.3.0/epubcheck.jar --out ../readers

Linux বা macOS-এ একই নির্দেশগুলিতে `./.venv/Scripts/python`-এর জায়গায় `./.venv/bin/python` ব্যবহার করুন। EPUBCheck অন্য কোথাও রাখা থাকলে `--epubcheck-jar`-এর পরে তার পথটি লিখুন। ফলাফলের জন্য উৎসের বাইরে নতুন একটি ফোল্ডার বেছে নিন।

`readers/reader.html` ব্রাউজারে খুলতে পারেন। চিত্র ও ফন্টগুলি পড়ার জন্য তার পাশের `assets` ফোল্ডারটি রাখুন। সম্পূর্ণ HTML সংস্করণটি অন্য কোথাও নিয়ে যেতে `reader-html.zip` ব্যবহার করুন। ই-বুক রিডারে পড়ার ফাইলটি `reader.epub`। সমীকরণগুলি MathML-এ লেখা। চিত্রের পাশের দৃষ্টিগ্রাহ্য লিঙ্ক থেকে তার বিস্তারিত বাংলা বিবরণে যেতে পারবেন।

## PDF ও সম্পাদনযোগ্য LaTeX

`source/BUILD.md`-তে XeLaTeX দিয়ে PDF তৈরির নির্দেশ আছে। পৃথক বিভাগ সম্পাদনার জন্য মূল ফাইল `source/locale/bn/courses/sets-logic-computation/slc-screen.tex`। সব বিভাগের লেখা একই ফাইলে পেতে তার পাশের `slc-screen-bn.tex` খুলুন।
