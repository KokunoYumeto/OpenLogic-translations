(function () {
  "use strict";

  // Choose one monolingual UI. Static page headings/labels belong to the edition builder.
  const messages = {
    en: {
      incomplete: "The hands-free player files are incomplete.",
      unsupported: "This browser does not expose speech synthesis.",
      local: "on this device", remote: "online/browser", defaultVoice: ", browser default",
      automatic: "Automatic voice for {0}",
      noVoice: "No compatible voice for {0} is available. Install or enable a voice for this language, then press Play / resume. Playback will not use a different language.",
      counts: "{0} on-device and {1} online/browser voices for this language are available. Online voices may require a network connection.",
      fallback: "The saved voice is unavailable here; a compatible voice for {0} will be used. ",
      regional: "A voice for the same language ({0}) will be used because the exact locale is unavailable. ",
      play: "Play / resume", pause: "Pause",
      progress: "Chapter {0} of {1}, passage {2} of {3}.",
      end: "End of the available book.", playing: "Playing {0}.",
      unsaved: " Your place remains available while this page stays open, but this browser is not saving it for a later session.",
      paused: "Paused. Your position is saved on this device.", pausedUnsaved: "Paused.",
      finished: "Finished. Press Play / resume to begin again.",
      blocked: "The browser blocked speech in this context. Press Play / resume again or check the site's autoplay permission.",
      error: "Speech stopped with error: {0}.",
      segmentation: "This browser cannot safely divide text into speech chunks. Use a browser with Intl.Segmenter support; the written text remains available.",
      saved: " Your last known position is saved.",
      ready: "Ready. Playback starts only when you press Play / resume."
    },
    id: {
      incomplete: "Berkas pemutar baca berkelanjutan tidak lengkap.",
      unsupported: "Peramban ini tidak menyediakan sintesis suara.",
      local: "di perangkat ini", remote: "daring/peramban", defaultVoice: ", suara bawaan peramban",
      automatic: "Suara otomatis untuk {0}",
      noVoice: "Tidak tersedia suara yang sesuai untuk {0}. Pasang atau aktifkan suara untuk bahasa ini, lalu tekan Putar / lanjutkan. Pemutar tidak akan menggunakan bahasa lain.",
      counts: "Tersedia {0} suara di perangkat dan {1} suara daring/peramban untuk bahasa ini. Suara daring mungkin memerlukan koneksi jaringan.",
      fallback: "Suara yang tersimpan tidak tersedia di sini; suara yang sesuai untuk {0} akan digunakan. ",
      regional: "Suara dengan bahasa yang sama ({0}) akan digunakan karena lokal yang tepat tidak tersedia. ",
      play: "Putar / lanjutkan", pause: "Jeda",
      progress: "Bab {0} dari {1}, bagian {2} dari {3}.",
      end: "Akhir buku yang tersedia.", playing: "Membacakan {0}.",
      unsaved: " Posisi baca tetap tersedia selama halaman ini terbuka, tetapi peramban tidak menyimpannya untuk sesi berikutnya.",
      paused: "Dijeda. Posisi baca disimpan di perangkat ini.", pausedUnsaved: "Dijeda.",
      finished: "Selesai. Tekan Putar / lanjutkan untuk mulai lagi.",
      blocked: "Peramban memblokir suara dalam konteks ini. Tekan Putar / lanjutkan lagi atau periksa izin pemutaran otomatis situs.",
      error: "Pembacaan berhenti dengan galat: {0}.",
      segmentation: "Peramban ini tidak dapat membagi teks menjadi potongan suara dengan aman. Gunakan peramban yang mendukung Intl.Segmenter; teks tertulis tetap tersedia.",
      saved: " Posisi baca terakhir yang diketahui telah disimpan.",
      ready: "Siap. Pembacaan hanya dimulai saat Anda menekan Putar / lanjutkan."
    }
  };

  function byId(id) { return document.getElementById(id); }

  function start() {
    const api = globalThis.OpenLogicHandsFree;
    const manifest = globalThis.OpenLogicListenManifest;
    const language = String(manifest && manifest.language || document.documentElement.lang || "en").toLowerCase();
    const ui = messages[language.split(/[-_]/)[0]] || messages.en;
    function t(key, ...values) {
      return ui[key].replace(/\{(\d+)\}/g, function (_match, index) { return String(values[Number(index)]); });
    }
    const status = byId("player-status");
    if (!api || !manifest) {
      status.textContent = t("incomplete");
      return;
    }
    if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) {
      status.textContent = t("unsupported");
      byId("play-toggle").disabled = true;
      return;
    }

    const speech = window.speechSynthesis;
    const playButton = byId("play-toggle");
    const restartButton = byId("restart-book");
    const rate = byId("speech-rate");
    const rateOutput = byId("speech-rate-output");
    const voiceSelect = byId("speech-voice");
    const voiceNote = byId("voice-note");
    const chapterSelect = byId("chapter-select");
    const progress = byId("player-progress");
    const currentText = byId("current-text");
    let voiceMap = new Map();
    let lastVisibleBlock = "";
    let browserStorage = null;
    try { browserStorage = window.localStorage; }
    catch (_error) { browserStorage = null; }

    const controller = new api.HandsFreeController({
      manifest: manifest,
      speech: speech,
      storage: browserStorage,
      createUtterance: function (text) { return new SpeechSynthesisUtterance(text); },
      onStateChange: render,
    });

    manifest.chapters.forEach(function (chapter, index) {
      const option = document.createElement("option");
      option.value = String(index);
      option.textContent = chapter.canonical_order + ". " + chapter.title;
      chapterSelect.appendChild(option);
    });

    function voiceLabel(voice) {
      const service = voice.localService ? t("local") : t("remote");
      return voice.name + " — " + voice.lang + " (" + service + (voice.default ? t("defaultVoice") : "") + ")";
    }

    function refreshVoices() {
      let exposedVoices = [];
      try { exposedVoices = speech.getVoices(); }
      catch (_error) { exposedVoices = []; }
      const voices = api.sortVoices(exposedVoices, manifest.language).filter(function (voice) {
        return api.languageMatches(voice.lang, manifest.language);
      });
      const selectedDescriptor = controller.snapshot().settings.voice;
      voiceMap = new Map();
      voiceSelect.replaceChildren();
      const automatic = document.createElement("option");
      automatic.value = "";
      automatic.textContent = t("automatic", manifest.language);
      voiceSelect.appendChild(automatic);
      voices.forEach(function (voice) {
        const key = api.voiceKey(voice);
        voiceMap.set(key, voice);
        const option = document.createElement("option");
        option.value = key;
        option.textContent = voiceLabel(voice);
        voiceSelect.appendChild(option);
      });
      const selection = api.resolveVoice(voices, selectedDescriptor, manifest.language);
      const selectedKey = selection.voice && selectedDescriptor && selection.matched ? api.voiceKey(selection.voice) : "";
      voiceSelect.value = selectedKey && voiceMap.has(selectedKey) ? selectedKey : "";
      const localCount = voices.filter(function (voice) { return voice.localService; }).length;
      // The user must click again after voices arrive; voiceschanged never starts speech.
      playButton.disabled = !selection.voice && !controller.activeUtterance;
      if (!selection.voice) {
        voiceNote.textContent = t("noVoice", manifest.language);
      } else {
        voiceNote.textContent = selectedDescriptor && !selection.matched ? t("fallback", selection.voice.lang) : "";
        if (selection.strategy === "same-language-fallback") voiceNote.textContent += t("regional", selection.voice.lang);
        voiceNote.textContent += t("counts", localCount, voices.length - localCount);
      }
    }

    function render(snapshot, reason) {
      rate.value = String(snapshot.settings.rate);
      rateOutput.value = snapshot.settings.rate.toFixed(1) + "×";
      playButton.textContent = snapshot.status === "playing" ? t("pause") : t("play");
      playButton.setAttribute("aria-pressed", snapshot.status === "playing" ? "true" : "false");

      if (snapshot.current) {
        const chapter = snapshot.current.chapter;
        const block = snapshot.current.block;
        chapterSelect.value = String(snapshot.current.chapterIndex);
        progress.textContent = t("progress", snapshot.current.chapterIndex + 1, manifest.chapters.length,
          snapshot.current.blockIndex + 1, chapter.blocks.length);
        const visibleBlock = chapter.chapter_key + "|" + block.block_id;
        if (visibleBlock !== lastVisibleBlock) {
          currentText.textContent = block.text;
          lastVisibleBlock = visibleBlock;
        }
      } else {
        progress.textContent = t("end");
        currentText.textContent = "";
      }

      if (snapshot.status === "playing") {
        status.textContent = t("playing", snapshot.current.chapter.title);
        if (!snapshot.persistence.available) status.textContent += t("unsaved");
      } else if (snapshot.status === "paused") {
        status.textContent = snapshot.persistence.available ? t("paused") : t("pausedUnsaved") + t("unsaved");
      } else if (snapshot.status === "ended") {
        status.textContent = t("finished");
      } else if (snapshot.status === "error") {
        if (snapshot.error === "not-allowed") status.textContent = t("blocked");
        else if (snapshot.error === "no-compatible-voice") status.textContent = t("noVoice", manifest.language);
        else if (snapshot.error === "grapheme-segmentation-unavailable") status.textContent = t("segmentation");
        else status.textContent = t("error", snapshot.error);
        status.textContent += snapshot.persistence.available ? t("saved") : t("unsaved");
      } else {
        status.textContent = t("ready");
        if (!snapshot.persistence.available) status.textContent += t("unsaved");
      }
      if (reason === "voice-fallback" || reason === "voice-unavailable") refreshVoices();
    }

    // The only playback entry point is this explicit button gesture.
    playButton.addEventListener("click", function () { controller.toggle(); });
    restartButton.addEventListener("click", function () { controller.restart(); });
    rate.addEventListener("input", function () { controller.setRate(rate.value); });
    voiceSelect.addEventListener("change", function () {
      controller.setVoice(voiceMap.get(voiceSelect.value) || null);
      refreshVoices();
    });
    chapterSelect.addEventListener("change", function () { controller.seek(Number(chapterSelect.value), 0, 0); });
    speech.addEventListener("voiceschanged", refreshVoices);
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "hidden") controller.persist();
    });
    window.addEventListener("pagehide", function () { controller.persist(); });

    const requestedChapter = new URLSearchParams(window.location.search).get("chapter");
    if (requestedChapter && manifest.chapters.some(function (chapter) { return chapter.chapter_key === requestedChapter; })) {
      controller.seekChapter(requestedChapter);
    }
    refreshVoices();
    render(controller.snapshot(), "ready");
    globalThis.OpenLogicHandsFreePlayer = controller;
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
  else start();
})();
