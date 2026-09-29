import { SearchX } from 'lucide-react';

function HighlightedText({ text, query }) {
  const needle = query.trim();
  if (!needle) return text;
  const escaped = needle.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return text.split(new RegExp(`(${escaped})`, 'giu')).map((part, index) => index % 2 ? <mark key={index}>{part}</mark> : part);
}

export default function TranscriptDisplay({ lines, search = '' }) {
  return (
    <div className="transcript-scroll" tabIndex={0} aria-label="Scrollable transcript">
      {!lines.length && <div className="no-matches"><SearchX size={23} /><h3>No matching words</h3><p>Try another phrase or clear your search.</p></div>}
      <ul aria-label="Transcript lines" className="transcript-lines">
        {lines.map((line, index) => (
          <li key={`${line.start}-${index}`} className="transcript-line">
            <span className="caption-time">{line.timestamp}</span>
            <span className="caption-text"><HighlightedText text={line.text} query={search} /></span>
          </li>
        ))}
      </ul>
    </div>
  );
}
