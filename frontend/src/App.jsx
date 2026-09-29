import { useMemo, useRef, useState } from 'react';
import { ArrowDownToLine, ArrowRight, Captions, Check, CheckCheck, Clock3, Copy, ExternalLink, Link2, Plus, Search, X } from 'lucide-react';
import Hero from './components/Hero';
import TranscriptDisplay from './components/TranscriptDisplay';
import SkeletonLoader from './components/SkeletonLoader';
import EmptyState from './components/EmptyState';
import ErrorToast from './components/ErrorToast';
import Footer from './components/Footer';
import { buildTranscriptExport, CODEX_PROMPT, downloadExport, formatTime, safeFilename } from './lib/transcript';

const API_BASE_URL = import.meta.env.DEV ? (import.meta.env.VITE_API_URL || '') : '';
const EXAMPLE_URL = 'https://www.youtube.com/watch?v=Hrbq66XqtCo';

async function post(path, body) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body), signal: AbortSignal.timeout(120000),
    });
  } catch {
    throw new Error('Could not reach the local extractor. Check that start.command is running, then retry.');
  }
  const data = await response.json();
  if (!response.ok) throw new Error(data.message || 'The request failed. Check the video link and retry.');
  return data;
}

function VideoInfo({ data }) {
  const [imgSrc, setImgSrc] = useState(`https://img.youtube.com/vi/${data.video_id}/maxresdefault.jpg`);
  return (
    <section className="video-info" aria-label="Video details">
      <a className="video-thumbnail" href={`https://www.youtube.com/watch?v=${data.video_id}`} target="_blank" rel="noopener noreferrer" aria-label="Watch this video on YouTube">
        <img src={imgSrc} alt={data.title} onError={() => setImgSrc(`https://img.youtube.com/vi/${data.video_id}/hqdefault.jpg`)} />
        {data.duration > 0 && <span className="video-duration">{formatTime(data.duration)}</span>}
        <span className="video-open"><ExternalLink size={15} /> Open video</span>
      </a>
      <p className="eyebrow">Source video</p>
      <h2>{data.title}</h2>
      <p className="video-channel">{data.channel}</p>
    </section>
  );
}

function CodexHandoff({ data, onError }) {
  const [copied, setCopied] = useState(false);
  async function copyAll() {
    try {
      const item = buildTranscriptExport(data);
      await navigator.clipboard.writeText(`${CODEX_PROMPT}\n\n${item.content}`);
      setCopied(true);
    } catch (failure) {
      onError(failure.name === 'NotAllowedError' ? 'Clipboard access failed. Download the transcript and attach it in Codex.' : failure.message);
    }
  }
  function download() {
    try {
      downloadExport(buildTranscriptExport(data), safeFilename(data));
    } catch (failure) {
      onError(failure.message);
    }
  }
  return (
    <div className="codex-handoff" aria-label="Take the transcript to Codex">
      <div className="handoff-heading"><div><h4>Ready for Codex</h4><p>One complete file. Every timestamp included.</p></div><span className="file-type">.MD</span></div>
      <div className="export-toolbar">
        <button className="button button-dark" onClick={download}><ArrowDownToLine size={16} />Download for Codex</button>
        <button className="button button-quiet" onClick={copyAll}>
          {copied ? <CheckCheck size={16} /> : <Copy size={16} />}
          {copied ? 'Transcript & prompt copied' : 'Copy for Codex'}
        </button>
      </div>
      <p className="handoff-instruction">Attach the downloaded file in Codex and use this prompt, or paste everything with Copy for Codex.</p>
      <p className="handoff-prompt">{CODEX_PROMPT}</p>
      <p className="handoff-note">The video-brief skill guides the summary. Analysis happens in your Codex chat.</p>
    </div>
  );
}

export default function App() {
  const [url, setUrl] = useState('');
  const [video, setVideo] = useState(null);
  const [trackId, setTrackId] = useState('');
  const [result, setResult] = useState(null);
  const [stage, setStage] = useState('');
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const urlInput = useRef(null);
  const loading = Boolean(stage);
  const visibleLines = useMemo(() => {
    const lines = result?.transcript_lines || [];
    const query = search.trim().toLocaleLowerCase();
    return query ? lines.filter((line) => line.text.toLocaleLowerCase().includes(query)) : lines;
  }, [result, search]);
  const wordCount = useMemo(() => result?.plain_text.trim().split(/\s+/u).length || 0, [result]);

  function changeUrl(value) {
    setUrl(value);
    setVideo(null);
    setResult(null);
    setTrackId('');
    setError('');
    setSearch('');
  }

  function startNew(value = '') {
    changeUrl(value);
    urlInput.current?.focus();
  }

  async function handleExtract(event) {
    event.preventDefault();
    setError('');
    setResult(null);
    setSearch('');
    try {
      let selected = trackId;
      let current = video;
      if (!current) {
        setStage('Checking available captions…');
        current = await post('/api/video-info', { url: url.trim() });
        setVideo(current);
        selected = current.recommended_track_id || '';
        setTrackId(selected);
      }
      if (!current.tracks.length) throw new Error('This video has no retrievable captions. Try a video with subtitles.');
      if (!selected) return;
      setStage('Retrieving the full transcript…');
      const transcript = await post('/api/extract', { url: current.video_id, track_id: selected });
      setResult({ ...transcript, channel: current.channel, duration: current.duration });
    } catch (failure) {
      setError(failure.message);
    } finally {
      setStage('');
    }
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#workspace">Skip to workspace</a>
      <header className="app-header">
        <div className="brand"><span className="brand-mark"><Captions size={23} /></span><span>Transcript<span className="brand-period">.</span></span><span className="local-label">LOCAL</span></div>
        <button className="button button-outline" onClick={() => startNew()} disabled={loading}><Plus size={16} />New transcript</button>
      </header>
      <main id="workspace" tabIndex={-1}>
        <Hero />
        <div className="workspace-grid">
          <aside className="source-panel" aria-label="Video source">
            <div className="section-heading"><span className="section-number">01</span><h2>The source</h2></div>
            <form onSubmit={handleExtract} aria-label="YouTube transcript extraction">
              <label htmlFor="youtube-url">YouTube video URL</label>
              <div className="url-input">
                <Link2 size={17} aria-hidden="true" />
                <input id="youtube-url" ref={urlInput} required disabled={loading} value={url} onChange={(event) => changeUrl(event.target.value)} placeholder="Paste a YouTube link…" spellCheck={false} autoComplete="off" aria-describedby="url-hint" />
              </div>
              <p id="url-hint" className="field-hint">A video, a talk, a conversation. Start with a link.</p>
              {video?.tracks.length > 0 && (
                <div className="track-field">
                  <label htmlFor="caption-track">Caption track</label>
                  <select id="caption-track" value={trackId} disabled={loading} onChange={(event) => { setTrackId(event.target.value); setResult(null); setError(''); setSearch(''); }}>
                    <option value="" disabled>Choose a caption language</option>
                    {video.tracks.map((track) => <option key={track.id} value={track.id}>{track.name} ({track.language}) · {track.source === 'uploaded' ? 'Uploaded' : 'Automatic'}</option>)}
                  </select>
                  {!trackId && <p className="field-hint accent-text">Choose a caption track, then get the transcript.</p>}
                </div>
              )}
              <button disabled={loading || !url.trim()} type="submit" className="button button-primary extract-button">
                {loading ? 'Retrieving captions…' : 'Get transcript'}<ArrowRight size={17} />
              </button>
              <ErrorToast error={error} onClose={() => setError('')} />
            </form>
            {video ? <VideoInfo key={video.video_id} data={video} /> : (
              <div className="source-note"><Captions size={20} /><div><h3>The original words.</h3><p>Uploaded or automatic captions, straight from the video.</p></div></div>
            )}
            <div className="source-footnote"><span className="status-dot" /><p>Runs on your Mac.<br /><span>Saved only when you download.</span></p></div>
          </aside>

          <section className={`transcript-panel ${result && !loading ? 'has-transcript' : ''}`} aria-label="Full transcript" aria-busy={loading}>
            <div className="panel-header">
              <div className="section-heading"><span className="section-number">02</span><h2>The transcript</h2></div>
              {result && !loading ? <span className="ready-label"><Check size={13} />Ready for Codex</span> : <span className="panel-meta">Your reading space</span>}
            </div>
            {loading ? <SkeletonLoader stage={stage} /> : result ? (
              <>
                <div className="transcript-summary">
                  <div><p className="eyebrow">Full transcript</p><h3>{result.title}</h3>
                    <p className="transcript-meta"><span>{wordCount.toLocaleString()} words</span><span>{result.transcript_lines.length.toLocaleString()} segments</span><span className="language-label">{result.language}</span></p>
                  </div>
                  <CodexHandoff key={`${result.track_id}-${result.generated_at}`} data={result} onError={setError} />
                </div>
                <div className="reader-toolbar">
                  <div className="search-field"><Search size={17} aria-hidden="true" /><input aria-label="Search transcript" placeholder="Find a word or phrase…" value={search} onChange={(event) => setSearch(event.target.value)} />
                    {search && <button className="icon-button" aria-label="Clear search" onClick={() => setSearch('')}><X size={15} /></button>}
                  </div>
                  <span className="timestamp-label"><Clock3 size={14} />Timestamps included</span>
                </div>
                {search && <p className="search-status" role="status">{visibleLines.length.toLocaleString()} {visibleLines.length === 1 ? 'match' : 'matches'}<span>Copy and downloads include the full transcript.</span></p>}
                <TranscriptDisplay lines={visibleLines} search={search} />
                <div className="reader-footer"><span>{result.source === 'uploaded' ? 'Uploaded captions' : 'YouTube automatic captions'}</span><span>Original wording, every segment.</span></div>
              </>
            ) : <EmptyState hasVideo={Boolean(video)} onExample={() => startNew(EXAMPLE_URL)} />}
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
