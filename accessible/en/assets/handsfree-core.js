/*
 * Silent-by-default, dependency-free core for the Open Logic hands-free player.
 * This file never calls speak() by itself. A caller must invoke controller.play()
 * from a user gesture.
 */
(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.OpenLogicHandsFree = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const STATE_VERSION = 2;
  const DEFAULT_STORAGE_KEY = "openlogic-handsfree-listen-state-v2";
  const DEFAULT_RATE = 1;
  const DEFAULT_MAX_CHUNK = 280;

  function clamp(value, minimum, maximum) {
    const number = Number(value);
    return Number.isFinite(number) ? Math.min(maximum, Math.max(minimum, number)) : minimum;
  }

  function normalizeLanguage(value) {
    const tag = String(value || "").trim().replace(/_/g, "-");
    try {
      return Intl.getCanonicalLocales(tag)[0].toLowerCase();
    } catch (_error) {
      return tag.toLowerCase();
    }
  }

  function languageMatches(candidate, wanted) {
    const left = normalizeLanguage(candidate);
    const right = normalizeLanguage(wanted);
    if (!left || !right) return false;
    return left === right || left.split("-")[0] === right.split("-")[0];
  }

  function editionId(manifest) {
    return String(manifest.edition_id || manifest.corpus_id);
  }

  function storageKeyFor(manifest, prefix) {
    return (prefix || DEFAULT_STORAGE_KEY) + ":" + encodeURIComponent(editionId(manifest))
      + ":" + encodeURIComponent(normalizeLanguage(manifest.language));
  }

  function voiceDescriptor(voice) {
    if (!voice) return null;
    return {
      voiceURI: String(voice.voiceURI || ""),
      name: String(voice.name || ""),
      lang: String(voice.lang || ""),
      localService: Boolean(voice.localService),
    };
  }

  function voiceKey(value) {
    const descriptor = value && Object.prototype.hasOwnProperty.call(value, "voiceURI")
      ? value
      : voiceDescriptor(value);
    if (!descriptor) return "";
    return JSON.stringify([
      descriptor.voiceURI || "",
      descriptor.name || "",
      descriptor.lang || "",
      Boolean(descriptor.localService),
    ]);
  }

  function sortVoices(voices, language) {
    const wanted = normalizeLanguage(language || "en");
    return Array.from(voices || []).sort(function (a, b) {
      const score = function (voice) {
        let result = 0;
        if (normalizeLanguage(voice.lang) === wanted) result += 16;
        else if (languageMatches(voice.lang, wanted)) result += 8;
        if (voice.default) result += 4;
        if (voice.localService) result += 2;
        return result;
      };
      return score(b) - score(a)
        || String(a.lang || "").localeCompare(String(b.lang || ""))
        || String(a.name || "").localeCompare(String(b.name || ""));
    });
  }

  function resolveVoice(voices, preferred, language) {
    const wanted = normalizeLanguage(language || (preferred && preferred.lang) || "en");
    const list = sortVoices(voices, wanted).filter(function (voice) {
      return languageMatches(voice.lang, wanted);
    });
    if (!list.length) return { voice: null, matched: false, strategy: "no-compatible-voice" };
    const compatiblePreference = preferred && languageMatches(preferred.lang, wanted) ? preferred : null;
    let match = compatiblePreference && list.find(function (voice) { return voiceKey(voice) === voiceKey(compatiblePreference); });
    if (match) return { voice: match, matched: true, strategy: "exact" };
    if (compatiblePreference && compatiblePreference.voiceURI) {
      match = list.find(function (voice) { return String(voice.voiceURI || "") === compatiblePreference.voiceURI; });
      if (match) return { voice: match, matched: true, strategy: "voice-uri" };
    }
    match = compatiblePreference && list.find(function (voice) {
      return String(voice.name || "") === String(compatiblePreference.name || "")
        && normalizeLanguage(voice.lang) === normalizeLanguage(compatiblePreference.lang);
    });
    if (match) return { voice: match, matched: true, strategy: "name-language" };
    return {
      voice: list[0],
      matched: !preferred,
      strategy: normalizeLanguage(list[0].lang) === wanted ? "exact-language-fallback" : "same-language-fallback",
    };
  }

  // Cache only the current block, not the book. All offsets remain UTF-16 offsets
  // for speech boundary events, but every emitted endpoint is a grapheme boundary.
  let segmentationCache = null;

  function boundariesFor(text, language) {
    const locale = normalizeLanguage(language || "en");
    if (segmentationCache && segmentationCache.text === text && segmentationCache.locale === locale) {
      return segmentationCache;
    }
    if (typeof Intl === "undefined" || typeof Intl.Segmenter !== "function") {
      throw new Error("grapheme-segmentation-unavailable");
    }
    const result = { text: text, locale: locale };
    for (const granularity of ["grapheme", "word", "sentence"]) {
      const boundaries = [0];
      const segmenter = new Intl.Segmenter(locale, { granularity: granularity });
      for (const segment of segmenter.segment(text)) boundaries.push(segment.index + segment.segment.length);
      result[granularity] = boundaries;
    }
    segmentationCache = result;
    return result;
  }

  function floorBoundary(boundaries, offset) {
    let low = 0;
    let high = boundaries.length;
    while (low < high) {
      const middle = Math.floor((low + high) / 2);
      if (boundaries[middle] <= offset) low = middle + 1;
      else high = middle;
    }
    return Math.max(0, low - 1);
  }

  function safeOffset(text, offset, language) {
    const boundaries = boundariesFor(text, language).grapheme;
    return boundaries[floorBoundary(boundaries, clamp(offset, 0, text.length))];
  }

  function nextChunk(value, rawOffset, maximumLength, language) {
    const text = String(value || "");
    if (!text || rawOffset >= text.length) return null;
    const numericLimit = Number(maximumLength);
    const limit = Number.isFinite(numericLimit) && numericLimit > 0
      ? Math.max(80, Math.floor(numericLimit)) : DEFAULT_MAX_CHUNK;
    const boundaries = boundariesFor(text, language);
    const startIndex = floorBoundary(boundaries.grapheme, clamp(rawOffset, 0, text.length));
    const start = boundaries.grapheme[startIndex];
    let end = boundaries.grapheme[floorBoundary(boundaries.grapheme, Math.min(text.length, start + limit))];
    // A single oversized cluster is indivisible: prefer fidelity to a soft length cap.
    if (end <= start) end = boundaries.grapheme[startIndex + 1];
    if (end < text.length && end - start <= limit) {
      const minimumUseful = start + Math.floor(limit * 0.55);
      for (const kind of ["sentence", "word"]) {
        const candidate = boundaries[kind][floorBoundary(boundaries[kind], end)];
        if (candidate >= minimumUseful && candidate > start) {
          end = candidate;
          break;
        }
      }
    }
    return { start: start, spokenEnd: end, nextOffset: end, text: text.slice(start, end),
      oversizedGrapheme: end - start > limit };
  }

  function validateManifest(manifest) {
    if (!manifest || manifest.schema_version !== 1 || !Array.isArray(manifest.chapters)) {
      throw new TypeError("Hands-free manifest schema_version 1 with chapters[] is required.");
    }
    if (!manifest.corpus_id || !manifest.language) {
      throw new TypeError("Hands-free manifest needs corpus_id and language.");
    }
    const chapters = manifest.chapters.map(function (chapter, chapterIndex) {
      if (!chapter || !chapter.chapter_key || !Array.isArray(chapter.blocks)) {
        throw new TypeError("Invalid chapter at index " + chapterIndex + ".");
      }
      const blocks = chapter.blocks.filter(function (block) {
        return block && block.block_id && String(block.text || "").trim();
      }).map(function (block) {
        return Object.assign({}, block, { text: String(block.text) });
      });
      if (!blocks.length) throw new TypeError("Chapter " + chapter.chapter_key + " has no speakable blocks.");
      return Object.assign({}, chapter, { blocks: blocks });
    });
    if (!chapters.length) throw new TypeError("Hands-free manifest has no chapters.");
    return Object.assign({}, manifest, { chapters: chapters });
  }

  function safeParse(value) {
    try { return JSON.parse(value || "null"); }
    catch (_error) { return null; }
  }

  function normalizedSettings(saved, language) {
    const settings = saved && saved.settings ? saved.settings : {};
    return {
      rate: clamp(settings.rate || DEFAULT_RATE, 0.1, 10),
      voice: settings.voice && typeof settings.voice === "object" && languageMatches(settings.voice.lang, language)
        ? voiceDescriptor(settings.voice) : null,
    };
  }

  function initialState(manifest, saved) {
    const reusableSettings = saved
      && saved.version === STATE_VERSION
      && saved.editionId === editionId(manifest)
      && normalizeLanguage(saved.language) === normalizeLanguage(manifest.language);
    const reusablePosition = reusableSettings
      && saved.corpusId === manifest.corpus_id
      && saved.position;
    const position = reusablePosition ? {
      chapterIndex: Math.floor(clamp(saved.position.chapterIndex, 0, manifest.chapters.length)),
      blockIndex: Math.max(0, Math.floor(Number(saved.position.blockIndex) || 0)),
      charOffset: Math.max(0, Math.floor(Number(saved.position.charOffset) || 0)),
    } : { chapterIndex: 0, blockIndex: 0, charOffset: 0 };
    return {
      version: STATE_VERSION,
      editionId: editionId(manifest),
      language: normalizeLanguage(manifest.language),
      corpusId: manifest.corpus_id,
      position: position,
      settings: normalizedSettings(reusableSettings ? saved : null, manifest.language),
    };
  }

  class HandsFreeController {
    constructor(options) {
      const config = options || {};
      this.manifest = validateManifest(config.manifest);
      this.speech = config.speech;
      this.createUtterance = config.createUtterance;
      this.storage = config.storage || null;
      this.persistenceReadAvailable = Boolean(this.storage);
      this.persistenceWriteAvailable = Boolean(this.storage);
      this.persistenceAvailable = Boolean(this.storage);
      this.persistenceError = this.storage ? null : "storage-unavailable";
      this.storageKey = storageKeyFor(this.manifest, config.storageKey);
      this.maxChunkLength = config.maxChunkLength || DEFAULT_MAX_CHUNK;
      this.persistenceStride = config.persistenceStride || 40;
      this.onStateChange = typeof config.onStateChange === "function" ? config.onStateChange : function () {};
      if (!this.speech || typeof this.speech.speak !== "function" || typeof this.createUtterance !== "function") {
        throw new TypeError("A speech adapter and utterance factory are required.");
      }
      let saved = null;
      try { saved = safeParse(this.storage && this.storage.getItem(this.storageKey)); }
      catch (_error) {
        saved = null;
        this.persistenceReadAvailable = false;
        this.persistenceAvailable = false;
        this.persistenceError = "storage-read-failed";
      }
      this.state = initialState(this.manifest, saved);
      this.status = "idle";
      this.lastError = null;
      this.activeUtterance = null;
      this.activeChunk = null;
      this.wantsPlayback = false;
      this.generation = 0;
      this.lastPersistedOffset = this.state.position.charOffset;
      this._normalizePosition();
      this.persist();
    }

    snapshot() {
      const current = this.current();
      return {
        status: this.status,
        error: this.lastError,
        position: Object.assign({}, this.state.position),
        settings: {
          rate: this.state.settings.rate,
          voice: this.state.settings.voice ? Object.assign({}, this.state.settings.voice) : null,
        },
        persistence: {
          available: this.persistenceAvailable,
          error: this.persistenceError,
          readAvailable: this.persistenceReadAvailable,
          writeAvailable: this.persistenceWriteAvailable,
        },
        current: current ? {
          chapter: current.chapter,
          block: current.block,
          chapterIndex: this.state.position.chapterIndex,
          blockIndex: this.state.position.blockIndex,
        } : null,
      };
    }

    _emit(reason) {
      this.onStateChange(this.snapshot(), reason);
    }

    persist() {
      if (!this.storage) {
        this.persistenceReadAvailable = false;
        this.persistenceWriteAvailable = false;
        this.persistenceAvailable = false;
        this.persistenceError = "storage-unavailable";
        return false;
      }
      try {
        this.storage.setItem(this.storageKey, JSON.stringify(this.state));
        this.persistenceWriteAvailable = true;
        this.persistenceAvailable = this.persistenceReadAvailable && this.persistenceWriteAvailable;
        this.persistenceError = this.persistenceReadAvailable ? null : "storage-read-failed";
        return this.persistenceAvailable;
      } catch (_error) {
        this.persistenceWriteAvailable = false;
        this.persistenceAvailable = false;
        this.persistenceError = "storage-write-failed";
        return false;
      }
    }

    _normalizePosition() {
      const position = this.state.position;
      while (position.chapterIndex < this.manifest.chapters.length) {
        const chapter = this.manifest.chapters[position.chapterIndex];
        if (position.blockIndex >= chapter.blocks.length) {
          position.chapterIndex += 1;
          position.blockIndex = 0;
          position.charOffset = 0;
          continue;
        }
        const block = chapter.blocks[position.blockIndex];
        position.charOffset = clamp(position.charOffset, 0, block.text.length);
        if (position.charOffset >= block.text.length) {
          position.blockIndex += 1;
          position.charOffset = 0;
          continue;
        }
        return;
      }
      position.chapterIndex = this.manifest.chapters.length;
      position.blockIndex = 0;
      position.charOffset = 0;
    }

    current() {
      this._normalizePosition();
      const position = this.state.position;
      if (position.chapterIndex >= this.manifest.chapters.length) return null;
      const chapter = this.manifest.chapters[position.chapterIndex];
      return { chapter: chapter, block: chapter.blocks[position.blockIndex] };
    }

    setRate(value) {
      this.state.settings.rate = clamp(value, 0.1, 10);
      this.persist();
      this._emit("settings");
    }

    setVoice(value) {
      if (value && !languageMatches(value.lang, this.manifest.language)) {
        throw new RangeError("The selected voice does not match this edition's language.");
      }
      this.state.settings.voice = value ? voiceDescriptor(value) : null;
      this.persist();
      this._emit("settings");
    }

    seek(chapterIndex, blockIndex, charOffset) {
      this.generation += 1;
      this.wantsPlayback = false;
      if (typeof this.speech.cancel === "function") this.speech.cancel();
      this.activeUtterance = null;
      this.activeChunk = null;
      this.state.position = {
        chapterIndex: Math.floor(clamp(chapterIndex, 0, this.manifest.chapters.length)),
        blockIndex: Math.max(0, Math.floor(Number(blockIndex) || 0)),
        charOffset: Math.max(0, Math.floor(Number(charOffset) || 0)),
      };
      this._normalizePosition();
      this.lastPersistedOffset = this.state.position.charOffset;
      this.status = this.current() ? "idle" : "ended";
      this.lastError = null;
      this.persist();
      this._emit("seek");
    }

    seekChapter(chapterKey) {
      const index = this.manifest.chapters.findIndex(function (chapter) {
        return chapter.chapter_key === chapterKey;
      });
      if (index < 0) throw new RangeError("Unknown chapter: " + chapterKey);
      this.seek(index, 0, 0);
    }

    restart() {
      this.seek(0, 0, 0);
    }

    play() {
      if (this.status === "paused" && this.activeUtterance && this.speech.paused) {
        this.wantsPlayback = true;
        this.status = "playing";
        this.speech.resume();
        this._emit("resume");
        return;
      }
      if (!this.current()) this.state.position = { chapterIndex: 0, blockIndex: 0, charOffset: 0 };
      this._normalizePosition();
      this.wantsPlayback = true;
      this.lastError = null;
      this.status = "playing";
      if (this.speech.paused && typeof this.speech.resume === "function") this.speech.resume();
      this._emit("play-requested");
      if (!this.activeUtterance) this._speakNext();
    }

    pause() {
      this.wantsPlayback = false;
      if (this.activeUtterance && typeof this.speech.pause === "function") this.speech.pause();
      this.status = "paused";
      this.persist();
      this._emit("pause");
    }

    toggle() {
      if (this.status === "playing") this.pause();
      else this.play();
    }

    _failSynthesis(code, reason) {
      this.activeUtterance = null;
      this.activeChunk = null;
      this.wantsPlayback = false;
      this.status = "error";
      this.lastError = String(code || "synthesis-failed");
      this.persist();
      this._emit(reason || "utterance-error");
    }

    _speakNext() {
      if (!this.wantsPlayback) return;
      const current = this.current();
      if (!current) {
        this.status = "ended";
        this.wantsPlayback = false;
        this.activeUtterance = null;
        this.activeChunk = null;
        this.persist();
        this._emit("book-ended");
        return;
      }
      let chunk;
      try {
        chunk = nextChunk(current.block.text, this.state.position.charOffset, this.maxChunkLength, this.manifest.language);
      } catch (_error) {
        this._failSynthesis("grapheme-segmentation-unavailable", "utterance-error");
        return;
      }
      if (!chunk) {
        this.state.position.blockIndex += 1;
        this.state.position.charOffset = 0;
        this._normalizePosition();
        this._speakNext();
        return;
      }

      let utterance;
      let voices;
      try {
        utterance = this.createUtterance(chunk.text);
        voices = typeof this.speech.getVoices === "function" ? this.speech.getVoices() : [];
      } catch (_error) {
        this._failSynthesis("synthesis-setup-failed", "utterance-error");
        return;
      }
      const selection = resolveVoice(voices, this.state.settings.voice, this.manifest.language);
      if (!selection.voice) {
        this._failSynthesis("no-compatible-voice", "voice-unavailable");
        return;
      }
      utterance.lang = this.manifest.language;
      utterance.rate = this.state.settings.rate;
      if (selection.voice) utterance.voice = selection.voice;
      const generation = this.generation;
      this.activeUtterance = utterance;
      this.activeChunk = chunk;

      utterance.onstart = () => {
        if (generation !== this.generation || utterance !== this.activeUtterance) return;
        this.status = "playing";
        this._emit(selection.matched ? "utterance-start" : "voice-fallback");
      };
      utterance.onboundary = (event) => {
        if (generation !== this.generation || utterance !== this.activeUtterance) return;
        const relative = clamp(event && event.charIndex, 0, chunk.text.length);
        this.state.position.charOffset = safeOffset(current.block.text, chunk.start + relative, this.manifest.language);
        if (Math.abs(this.state.position.charOffset - this.lastPersistedOffset) >= this.persistenceStride) {
          this.persist();
          this.lastPersistedOffset = this.state.position.charOffset;
        }
        this._emit("boundary");
      };
      utterance.onend = () => {
        if (generation !== this.generation || utterance !== this.activeUtterance) return;
        this.state.position.charOffset = chunk.nextOffset;
        this._normalizePosition();
        this.lastPersistedOffset = this.state.position.charOffset;
        this.activeUtterance = null;
        this.activeChunk = null;
        this.persist();
        if (!this.current()) {
          this.status = "ended";
          this.wantsPlayback = false;
          this._emit("book-ended");
          return;
        }
        this._emit("utterance-end");
        this._speakNext();
      };
      utterance.onerror = (event) => {
        if (generation !== this.generation || utterance !== this.activeUtterance) return;
        this._failSynthesis(event && event.error || "synthesis-failed", "utterance-error");
      };
      try {
        this.speech.speak(utterance);
      } catch (_error) {
        if (generation === this.generation && utterance === this.activeUtterance) {
          this._failSynthesis("speak-threw", "utterance-error");
        }
      }
    }
  }

  return {
    DEFAULT_MAX_CHUNK: DEFAULT_MAX_CHUNK,
    DEFAULT_STORAGE_KEY: DEFAULT_STORAGE_KEY,
    HandsFreeController: HandsFreeController,
    languageMatches: languageMatches,
    nextChunk: nextChunk,
    resolveVoice: resolveVoice,
    sortVoices: sortVoices,
    storageKeyFor: storageKeyFor,
    validateManifest: validateManifest,
    voiceDescriptor: voiceDescriptor,
    voiceKey: voiceKey,
  };
});
