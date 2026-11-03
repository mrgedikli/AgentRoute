// Playback controls: play / pause / rewind, speed, scrubber (like NetAnim / nam).
const SPEEDS = [0.01, 0.05, 0.2, 1];

export default function Timeline({ t, duration, playing, speed, direction, onTime, onPlay,
  onSpeed, onDirection }) {
  return (
    <div className="timeline">
      <button className="btn" onClick={() => { onDirection(-1); onPlay(true); }}
        aria-pressed={playing && direction < 0} title="Play backwards">{"◀◀"}</button>
      <button className="btn primary" onClick={() => { if (!playing) onDirection(1); onPlay(!playing); }}
        title={playing ? "Pause" : "Play"}>{playing ? "❚❚" : "▶"}</button>
      <button className="btn" onClick={() => onTime(0)} title="Back to start">{"⏮"}</button>
      <input type="range" min={0} max={duration} step={0.001} value={t}
        onChange={(e) => onTime(Number(e.target.value))} aria-label="Simulation time" />
      <span className="time">{t.toFixed(3)} s</span>
      <label className="speed">
        speed
        <select value={speed} onChange={(e) => onSpeed(Number(e.target.value))}>
          {SPEEDS.map((s) => <option key={s} value={s}>{s}x</option>)}
        </select>
      </label>
    </div>
  );
}
