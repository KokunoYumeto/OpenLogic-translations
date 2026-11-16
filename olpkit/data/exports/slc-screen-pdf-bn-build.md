# সেট, যুক্তি, গণনা — উৎস থেকে PDF তৈরি

ZIP ফাইলটি একটি খালি ফোল্ডারে খুলুন। ফাইল ও ফোল্ডারগুলির নাম এবং অবস্থান যেমন আছে তেমনই রাখুন। বইটি তৈরি করতে XeLaTeX, BibTeX ও MakeIndex লাগে। বাংলা লেখার জন্য Noto Serif Bengali ফন্টটি উৎসের সঙ্গে আছে। লাতিন অক্ষরের জন্য ব্যবহৃত Latin Modern Roman ফন্টটি আপনার TeX ব্যবস্থায় থাকতে হবে।

উৎসের মূল ফোল্ডার থেকে বইটির ফোল্ডারে যান।

    cd locale/bn/courses/sets-logic-computation

BibTeX-কে তথ্যসূত্রের বিন্যাস খুঁজে পেতে মূল ফোল্ডারের `bib` ডিরেক্টরিটি দেখিয়ে দিন। একই তারিখ ব্যবহার করে PDF তৈরির জন্য নিচের দুটি পরিবেশ চলকের মানও নির্দিষ্ট করুন।

PowerShell-এ লিখুন

    $env:BSTINPUTS = (Resolve-Path '../../../../bib').Path + [IO.Path]::PathSeparator
    $env:SOURCE_DATE_EPOCH = '@SOURCE_DATE_EPOCH@'
    $env:FORCE_SOURCE_DATE = '1'

Linux বা macOS-এর শেলে লিখুন

    export BSTINPUTS="$(cd ../../../../bib && pwd):"
    export SOURCE_DATE_EPOCH=@SOURCE_DATE_EPOCH@ FORCE_SOURCE_DATE=1

প্রতিটি বিভাগের জন্য আলাদা উৎস ফাইল ব্যবহার করতে নিচের নির্দেশগুলি ক্রমানুসারে চালান। প্রথমে বইটি সংকলিত হয়। তারপর BibTeX তথ্যসূত্র সাজায় এবং MakeIndex পরিভাষার তালিকা তৈরি করে। পরের সংকলনগুলিতে পৃষ্ঠাসংখ্যা ও পারস্পরিক উল্লেখ স্থির হয়।

    xelatex -no-shell-escape -halt-on-error slc-screen.tex
    bibtex slc-screen
    makeindex -s slc-screen.ist -t slc-screen.glg -o slc-screen.gls slc-screen.glo
    xelatex -no-shell-escape -halt-on-error slc-screen.tex
    bibtex slc-screen
    makeindex -s slc-screen.ist -t slc-screen.glg -o slc-screen.gls slc-screen.glo
    xelatex -no-shell-escape -halt-on-error slc-screen.tex
    xelatex -no-shell-escape -halt-on-error slc-screen.tex

বইটির PDF একই ফোল্ডারে `slc-screen.pdf` নামে পাবেন। পুরো বইয়ের লেখা একটি ফাইলে সম্পাদনা করতে চাইলে নতুন একটি খালি ফোল্ডারে উৎসের ZIP খুলুন। উপরের নির্দেশগুলিতে `slc-screen` নামটির প্রতিটি জায়গায় `slc-screen-bn` লিখুন। এই পদ্ধতিতে `slc-screen-bn.tex` থেকে বইয়ের বিভাগগুলি তৈরি হয়। ছবি, ফন্ট, তথ্যসূত্র ও বিন্যাসের জন্য ZIP-এর বাকি ফাইলগুলিও লাগে।
