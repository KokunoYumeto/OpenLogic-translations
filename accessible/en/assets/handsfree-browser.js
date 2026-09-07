(function () {
  "use strict";

  function byId(id) { return document.getElementById(id); }

  function start() {
    const api = globalThis.OpenLogicHandsFree;
    const manifest = globalThis.OpenLogicListenManifest;
    const status = byId("player-status");
    if (!api || !manifest) {
      status.textContent = "The hands-free player files are incomplete.";
      return;
    }
    if (!("speechSynthesis" in window) || !("SpeechSynthesisUtterance" in window)) {
      status.textContent = "This browser does not expose speech synthesis.";
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
    let latestSnapshot = null;
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
      const service = voice.localService ? "on this device" : "online/browser";
      const defaultLabel = voice.default ? ", browser default" : "";
      return voice.name + " — " + voice.lang + " (" + service + defaultLabel + ")";
    }

    function refreshVoices() {
      let exposedVoices = [];
      try { exposedVoices = speech.getVoices(); }
      catch (_error) { exposedVoices = []; }
      const voices = api.sortVoices(exposedVoices, manifest.language);
      const selectedDescriptor = controller.snapshot().settings.voice;
      voiceMap = new Map();
      voiceSelect.replaceChildren();
      const browserDefault = document.createElement("option");
      browserDefault.value = "";
      browserDefault.textContent = "Browser default voice";
      voiceSelect.appendChild(browserDefault);
      voices.forEach(function (voice) {
        const key = api.voiceKey(voice);
        voiceMap.set(key, voice);
        const option = document.createElement("option");
        option.value = key;
        option.textContent = voiceLabel(voice);
        voiceSelect.appendChild(option);
      });
      const selection = api.resolveVoice(voices, selectedDescriptor);
      const selectedKey = selection.voice ? api.voiceKey(selection.voice) : "";
      voiceSelect.value = selectedKey && voiceMap.has(selectedKey) ? selectedKey : "";
      const localCount = voices.filter(function (voice) { return voice.localService; }).length;
      if (!voices.length) {
        voiceNote.textContent = "The browser has not reported its voice list yet. Play uses its default voice.";
      } else if (selectedDescriptor && !selection.matched) {
        voiceNote.textContent = "The saved voice is unavailable here; playback falls back to the browser default. "
          + localCount + " on-device and " + (voices.length - localCount) + " online/browser voices are currently exposed.";
      } else if (selectedDescriptor && selection.strategy !== "exact") {
        voiceNote.textContent = "The saved voice was matched by "
          + (selection.strategy === "voice-uri" ? "its voice identifier" : "its name and language") + ". "
          + localCount + " on-device and " + (voices.length - localCount)
          + " online/browser voices are currently exposed. Online voices may require a network connection.";
      } else {
        voiceNote.textContent = localCount + " on-device and " + (voices.length - localCount)
          + " online/browser voices are currently exposed. Online voices may require a network connection.";
      }
    }

    function render(snapshot, reason) {
      latestSnapshot = snapshot;
      rate.value = String(snapshot.settings.rate);
      rateOutput.value = snapshot.settings.rate.toFixed(1) + "×";
      playButton.textContent = snapshot.status === "playing" ? "Pause" : "Play / resume";
      playButton.setAttribute("aria-pressed", snapshot.status === "playing" ? "true" : "false");

      if (snapshot.current) {
        const chapter = snapshot.current.chapter;
        const block = snapshot.current.block;
        chapterSelect.value = String(snapshot.current.chapterIndex);
        progress.textContent = "Chapter " + (snapshot.current.chapterIndex + 1) + " of " + manifest.chapters.length
          + ", passage " + (snapshot.current.blockIndex + 1) + " of " + chapter.blocks.length + ".";
        const visibleBlock = chapter.chapter_key + "|" + block.block_id;
        if (visibleBlock !== lastVisibleBlock) {
          currentText.textContent = block.text;
          lastVisibleBlock = visibleBlock;
        }
      } else {
        progress.textContent = "End of the available book.";
        currentText.textContent = "";
      }

      if (snapshot.status === "playing") {
        status.textContent = "Playing " + snapshot.current.chapter.title + ".";
        if (!snapshot.persistence.available) {
          status.textContent += " Your place is available for this open page, but this browser is not saving it for a later session.";
        }
      } else if (snapshot.status === "paused") {
        status.textContent = snapshot.persistence.available
          ? "Paused. Your position is saved on this device."
          : "Paused. Your place remains available while this page stays open, but this browser is not saving it for a later session.";
      } else if (snapshot.status === "ended") {
        status.textContent = "Finished. Press Play / resume to begin again.";
      } else if (snapshot.status === "error") {
        const blocked = snapshot.error === "not-allowed";
        status.textContent = blocked
          ? "The browser blocked speech in this context. Press Play / resume again or check the site's autoplay permission."
          : "Speech stopped with error: " + snapshot.error + ".";
        status.textContent += snapshot.persistence.available
          ? " Your last known position is saved."
          : " Your place remains available while this page stays open, but this browser is not saving it for a later session.";
      } else {
        status.textContent = "Ready. Playback starts only when you press Play / resume.";
        if (!snapshot.persistence.available) {
          status.textContent += " Your place is available for this open page, but this browser is not saving it for a later session.";
        }
      }
      if (reason === "voice-fallback") refreshVoices();
    }

    // The only playback entry point is this explicit button gesture.
    playButton.addEventListener("click", function () { controller.toggle(); });
    restartButton.addEventListener("click", function () { controller.restart(); });
    rate.addEventListener("input", function () { controller.setRate(rate.value); });
    voiceSelect.addEventListener("change", function () {
      controller.setVoice(voiceMap.get(voiceSelect.value) || null);
      refreshVoices();
    });
    chapterSelect.addEventListener("change", function () {
      controller.seek(Number(chapterSelect.value), 0, 0);
    });
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
