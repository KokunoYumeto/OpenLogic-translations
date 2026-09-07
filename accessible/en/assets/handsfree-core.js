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

  const STATE_VERSION = 1;
  const DEFAULT_STORAGE_KEY = "openlogic-handsfree-listen-state-v1";
  const DEFAULT_RATE = 1;
  const DEFAULT_MAX_CHUNK = 280;

  function clamp(value, minimum, maximum) {
    const number = Number(value);
    return Number.isFinite(number) ? Math.min(maximum, Math.max(minimum, number)) : minimum;
  }

  function normalizeLanguage(value) {
    return String(value || "").trim().replace(/_/g, "-").toLowerCase();
  }

  function languageMatches(candidate, wanted) {
    const left = normalizeLanguage(candidate);
    const right = normalizeLanguage(wanted);
    if (!left || !right) return false;
    return left === right || left.split("-")[0] === right.split("-")[0];
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
        if (languageMatches(voice.lang, wanted)) result += 8;
        if (voice.default) result += 4;
        if (voice.localService) result += 2;
        return result;
      };
      return score(b) - score(a)
        || String(a.lang || "").localeCompare(String(b.lang || ""))
        || String(a.name || "").localeCompare(String(b.name || ""));
    });
  }

  function resolveVoice(voices, preferred) {
    const list = Array.from(voices || []);
    if (!preferred) return { voice: null, matched: true, strategy: "browser-default" };
    let match = list.find(function (voice) { return voiceKey(voice) === voiceKey(preferred); });
    if (match) return { voice: match, matched: true, strategy: "exact" };
    if (preferred.voiceURI) {
      match = list.find(function (voice) { return String(voice.voiceURI || "") === preferred.voiceURI; });
      if (match) return { voice: match, matched: true, strategy: "voice-uri" };
    }
    match = list.find(function (voice) {
      return String(voice.name || "") === String(preferred.name || "")
        && normalizeLanguage(voice.lang) === normalizeLanguage(preferred.lang);
    });
    if (match) return { voice: match, matched: true, strategy: "name-language" };
    return { voice: null, matched: false, strategy: "browser-default-fallback" };
  }

  function nextChunk(value, rawOffset, maximumLength) {
    const text = String(value || "");
    const limit = Math.max(80, Math.floor(maximumLength || DEFAULT_MAX_CHUNK));
    let start = clamp(rawOffset, 0, text.length);
    while (start < text.length && /\s/.test(text[start])) start += 1;
    if (start >= text.length) return null;

    const hardEnd = Math.min(text.length, start + limit);
    let end = hardEnd;
    if (hardEnd < text.length) {
      const minimumUseful = Math.floor(limit * 0.55);
      const candidate = text.slice(start, hardEnd + 1);
      const sentence = /[.!?;:](?:["'”’\)\]])?\s+/g;
      let sentenceMatch;
      let sentenceEnd = -1;
      while ((sentenceMatch = sentence.exec(candidate)) !== null) {
        const possible = sentenceMatch.index + sentenceMatch[0].search(/\s/);
        if (possible >= minimumUseful) sentenceEnd = possible;
      }
      if (sentenceEnd > 0) {
        end = start + sentenceEnd;
      } else {
        const whitespace = candidate.slice(0, hardEnd - start + 1).lastIndexOf(" ");
        if (whitespace >= minimumUseful) end = start + whitespace;
      }
    }
    if (end <= start) end = Math.min(text.length, start + limit);
    let nextOffset = end;
    while (nextOffset < text.length && /\s/.test(text[nextOffset])) nextOffset += 1;
    return {
      start: start,
      spokenEnd: end,
      nextOffset: nextOffset,
      text: text.slice(start, end),
    };
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
        return Object.assign({}, block, { text: String(block.text).trim() });
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

  function normalizedSettings(saved) {
    const settings = saved && saved.settings ? saved.settings : {};
    return {
      rate: clamp(settings.rate || DEFAULT_RATE, 0.1, 10),
      voice: settings.voice && typeof settings.voice === "object" ? settings.voice : null,
    };
  }

  function initialState(manifest, saved) {
    const reusablePosition = saved
      && saved.version === STATE_VERSION
      && saved.corpusId === manifest.corpus_id
      && saved.position;
    const position = reusablePosition ? {
      chapterIndex: Math.floor(clamp(saved.position.chapterIndex, 0, manifest.chapters.length)),
      blockIndex: Math.max(0, Math.floor(Number(saved.position.blockIndex) || 0)),
      charOffset: Math.max(0, Math.floor(Number(saved.position.charOffset) || 0)),
    } : { chapterIndex: 0, blockIndex: 0, charOffset: 0 };
    return {
      version: STATE_VERSION,
      corpusId: manifest.corpus_id,
      position: position,
      settings: normalizedSettings(saved),
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
      this.storageKey = config.storageKey || DEFAULT_STORAGE_KEY;
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
      const chunk = nextChunk(current.block.text, this.state.position.charOffset, this.maxChunkLength);
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
      const selection = resolveVoice(voices, this.state.settings.voice);
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
        this.state.position.charOffset = chunk.start + relative;
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
    validateManifest: validateManifest,
    voiceDescriptor: voiceDescriptor,
    voiceKey: voiceKey,
  };
});
