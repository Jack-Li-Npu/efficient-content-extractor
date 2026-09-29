import { ArrowUpRight, AlignLeft, Quote } from 'lucide-react';

export default function EmptyState({ hasVideo, onExample }) {
  return (
    <div className="empty-state">
      <div className="paper-illustration" aria-hidden="true">
        <div className="paper-shadow" />
        <div className="paper-sheet"><div className="paper-top"><AlignLeft size={18} /><span>TRANSCRIPT</span></div><Quote size={28} className="paper-quote" /><div className="paper-lines"><i /><i /><i /><i /><i /></div><div className="paper-bottom"><span>01:24</span><span className="paper-highlight" /></div></div>
      </div>
      <p className="eyebrow">From watching to understanding</p>
      <h3>The whole conversation.<br />Ready for your next step.</h3>
      <p className="empty-description">{hasVideo ? 'Choose the captions you want, then click Get transcript. Every available segment will appear here.' : 'Add a YouTube link. Take its full, timestamped transcript to Codex for a summary and the moments worth watching.'}</p>
      {!hasVideo && <button className="text-button" onClick={onExample}>Try the example video<ArrowUpRight size={16} /></button>}
      <div className="format-signature"><span>ONE MARKDOWN FILE</span><span>FULL TEXT + TIMESTAMPS</span></div>
    </div>
  );
}
