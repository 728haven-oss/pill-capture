// 알약 상자 검출기(YOLOv8n, tf.js 그래프 모델) 브라우저 실행기
// 사용: await PillYolo.load(modelJsonUrl); const r = await PillYolo.run(canvas, conf); r.boxes = [{x,y,w,h,score}] (원본 캔버스 좌표, 중심+크기)
const PillYolo = (() => {
  let model = null, S = 640;
  async function load(url) {
    model = await tf.loadGraphModel(url);
    const sh = model.inputs && model.inputs[0] && model.inputs[0].shape; if (sh && sh.length === 4 && sh[1] > 0) S = sh[1];
  }
  // letterbox: 긴 변을 S 로 축소, 나머지는 회색(114) 패딩 → [1,S,S,3] 0..1
  function prep(canvas) {
    const w = canvas.width, h = canvas.height; const sc = S / Math.max(w, h); const nw = Math.round(w * sc), nh = Math.round(h * sc);
    const c = document.createElement('canvas'); c.width = S; c.height = S; const cx = c.getContext('2d'); cx.fillStyle = 'rgb(114,114,114)'; cx.fillRect(0, 0, S, S);
    const ox = (S - nw) >> 1, oy = (S - nh) >> 1; cx.drawImage(canvas, 0, 0, w, h, ox, oy, nw, nh);
    const id = cx.getImageData(0, 0, S, S).data; const f = new Float32Array(S * S * 3);
    for (let i = 0, j = 0; i < id.length; i += 4, j += 3) { f[j] = id[i] / 255; f[j + 1] = id[i + 1] / 255; f[j + 2] = id[i + 2] / 255; }
    return { x: tf.tensor4d(f, [1, S, S, 3]), sc, ox, oy };
  }
  async function run(canvas, conf, iou) {
    conf = conf || 0.35; iou = iou || 0.5;
    const { x, sc, ox, oy } = prep(canvas);
    let out = model.execute(x); if (Array.isArray(out)) out = out[0];
    const shape = out.shape; const data = await out.data(); tf.dispose([x, out]);
    // 출력 [1,5,N] 또는 [1,N,5] (cx,cy,w,h,score); 좌표가 0..1 정규화면 S 배
    let N, get;
    if (shape[1] === 5) { N = shape[2]; get = (k, i) => data[k * N + i]; } else { N = shape[1]; get = (k, i) => data[i * 5 + k]; }
    let maxc = 0; for (let i = 0; i < N; i += 97) maxc = Math.max(maxc, get(0, i), get(1, i));
    const mul = maxc <= 1.5 ? S : 1;
    const bxs = [], scs = [];
    for (let i = 0; i < N; i++) { const s = get(4, i); if (s < conf) continue; const cx = get(0, i) * mul, cy = get(1, i) * mul, w = get(2, i) * mul, h = get(3, i) * mul; bxs.push([cy - h / 2, cx - w / 2, cy + h / 2, cx + w / 2]); scs.push(s); }
    const boxes = [];
    if (bxs.length) {
      const bt = tf.tensor2d(bxs, [bxs.length, 4]), st = tf.tensor1d(scs);
      const keep = await tf.image.nonMaxSuppressionAsync(bt, st, 1000, iou, conf); const ki = await keep.data(); tf.dispose([bt, st, keep]);
      for (const i of ki) { const [y0, x0, y1, x1] = bxs[i]; boxes.push({ x: ((x0 + x1) / 2 - ox) / sc, y: ((y0 + y1) / 2 - oy) / sc, w: (x1 - x0) / sc, h: (y1 - y0) / sc, score: scs[i] }); }
    }
    return { boxes, S, sc, ox, oy };
  }
  return { load, run, get ready() { return !!model; } };
})();
if (typeof window !== 'undefined') window.PillYolo = PillYolo;
if (typeof module !== 'undefined') module.exports = PillYolo;
