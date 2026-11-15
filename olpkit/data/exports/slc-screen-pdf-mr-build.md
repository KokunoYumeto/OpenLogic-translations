# संच, तर्कशास्त्र, संगणन — PDF तयार करणे

संपूर्ण स्रोतसंच एका स्वतंत्र फोल्डरमध्ये उलगडा. फोल्डरची रचना जशी आहे तशी ठेवा. XeLaTeX, BibTeX आणि MakeIndex आवश्यक आहेत. पुस्तकातील परवान्यांच्या आणि श्रेयाच्या नोंदी स्रोतसंचात समाविष्ट आहेत.

स्रोतसंचाच्या मूळ फोल्डरमधून पुढील निर्देशिकेत जा.

    cd locale/mr/courses/sets-logic-computation

संदर्भसूचीची शैली स्रोतसंचाच्या मूळ फोल्डरमधील `bib` मध्ये आहे. PowerShell वापरत असल्यास वरच्या निर्देशिकेतून पुढील आज्ञा द्या.

    $env:BSTINPUTS = (Resolve-Path '../../../../bib').Path + [IO.Path]::PathSeparator
    $env:SOURCE_DATE_EPOCH = '@SOURCE_DATE_EPOCH@'
    $env:FORCE_SOURCE_DATE = '1'

Linux किंवा macOS वरील शेलमध्ये त्याऐवजी या आज्ञा द्या.

    export BSTINPUTS="$(cd ../../../../bib && pwd):"
    export SOURCE_DATE_EPOCH=@SOURCE_DATE_EPOCH@ FORCE_SOURCE_DATE=1

विभागांच्या स्वतंत्र फायली संपादित केल्या असल्यास पुढील आज्ञा क्रमाने चालवा.

    xelatex -no-shell-escape -halt-on-error slc-screen.tex
    bibtex slc-screen
    makeindex -s slc-screen.ist -t slc-screen.glg -o slc-screen.gls slc-screen.glo
    xelatex -no-shell-escape -halt-on-error slc-screen.tex
    bibtex slc-screen
    makeindex -s slc-screen.ist -t slc-screen.glg -o slc-screen.gls slc-screen.glo
    xelatex -no-shell-escape -halt-on-error slc-screen.tex
    makeindex -s slc-screen.ist -t slc-screen.glg -o slc-screen.gls slc-screen.glo
    xelatex -no-shell-escape -halt-on-error slc-screen.tex

याच निर्देशिकेत तयार झालेली फाइल `slc-screen.pdf` आहे. एकत्रित संपादनयोग्य स्रोत वापरण्यासाठी वरच्या आज्ञांमध्ये `slc-screen` हे नाव सर्वत्र `slc-screen-mr` असे बदला. एकत्रित फाइलमधून पुस्तकातील विभाग पुन्हा तयार होतात. चित्रे, मुद्राक्षरे, संदर्भसूची आणि शैली यांच्या फायलींसाठी पूर्ण स्रोतसंच आवश्यक आहे.
