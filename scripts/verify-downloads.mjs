// Usage: node scripts/verify-downloads.mjs '/path/to/extract-response.json' '/path/to/download.transcript.md'
import fs from 'node:fs';
import assert from 'node:assert/strict';
import { buildTranscriptExport } from '../frontend/src/lib/transcript.js';

const [source, filename] = process.argv.slice(2);
if (!source || !filename) throw new Error('Pass the saved extraction response JSON and the downloaded .transcript.md file.');
const data = JSON.parse(fs.readFileSync(source, 'utf8'));
const downloaded = fs.readFileSync(filename, 'utf8');
// Metadata from /api/video-info is added by the UI; compare it when present in the supplied response.
const metadata = JSON.parse(downloaded.match(/^(`{3,})json\n([\s\S]*?)\n\1$/m)?.[2] || 'null');
assert.ok(metadata, 'Video metadata missing');
const expected = buildTranscriptExport({ channel: metadata.channel, duration: metadata.video_duration_seconds, ...data });
assert.equal(downloaded, expected.content, 'Downloaded content differs from the complete source transcript');
console.log(JSON.stringify({ segments: metadata.segment_count, language: metadata.language, source: metadata.caption_source, firstStart: metadata.caption_start, lastEnd: metadata.caption_end, exactMatch: true }, null, 2));
