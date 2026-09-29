export default function SkeletonLoader({ stage }) {
  return (
    <div className="loading-state" role="status" aria-live="polite">
      <p className="eyebrow">Making room for the words</p>
      <h3>{stage}</h3>
      <p>Long videos can take a moment. Keep this window open.</p>
      <div className="skeleton-lines" aria-hidden="true">
        {Array.from({ length: 7 }, (_, index) => <div className="skeleton-row" key={index}><span /><div><i /><i /></div></div>)}
      </div>
    </div>
  );
}
