// 알약 중심점 검출기(pillnet) 브라우저 실행기 — tf.js 로 그래프를 직접 구성(BN 접힌 conv 가중치)
// 사용: await PillNet.load(jsonUrl, binUrl); const r = await PillNet.run(canvas); r.peaks = [{x,y,score,size}] (원본 캔버스 좌표)
const PillNet = (() => {
  let meta=null, W=null;  // W[i] = {k:tf.Tensor4d, b:tf.Tensor1d}
  async function load(jsonUrl, binUrl, jsonObj, binBuf){
    const get = (url, type) => new Promise((res, rej) => {   // fetch 가 안 되는 환경(file://, 일부 WebView)에서도 읽히도록 XHR
      const x = new XMLHttpRequest(); x.open('GET', url); x.responseType = type; x.onload = () => (x.status === 0 || (x.status >= 200 && x.status < 300)) ? res(x.response) : rej(new Error('HTTP ' + x.status + ' ' + url)); x.onerror = () => rej(new Error('load failed ' + url)); x.send(); });
    meta = jsonObj || await get(jsonUrl, 'json');
    const buf = binBuf || await get(binUrl, 'arraybuffer');
    const f16 = new Uint16Array(buf);
    W = meta.layers.map(L => {
      const w = new Float32Array(L.wlen); const base=L.woff/2;
      for(let i=0;i<L.wlen;i++) w[i]=f16to32(f16[base+i]);
      const b = new Float32Array(buf, L.boff, L.cout);
      return { k: tf.tensor4d(w,[L.k,L.k,L.cin,L.cout]), b: tf.tensor1d(new Float32Array(b)) };
    });
  }
  function f16to32(h){ const s=(h&0x8000)?-1:1, e=(h>>10)&0x1f, f=h&0x3ff; if(e===0) return s*Math.pow(2,-14)*(f/1024); if(e===31) return f?NaN:s*Infinity; return s*Math.pow(2,e-15)*(1+f/1024); }
  function conv(x, i){ const L=meta.layers[i]; let y=x;
    if(L.pad>0) y=tf.pad(y,[[0,0],[L.pad,L.pad],[L.pad,L.pad],[0,0]]);
    y=tf.conv2d(y, W[i].k, L.stride, 'valid'); y=tf.add(y, W[i].b); return L.relu? tf.relu(y) : y; }
  function up2(x){ return tf.image.resizeNearestNeighbor(x,[x.shape[1]*2,x.shape[2]*2]); }
  // canvas → 긴 변 input 크기로 축소, 정사각 패딩(회색) → NHWC float
  function prep(canvas){
    const S=meta.input; const w=canvas.width, h=canvas.height; const sc=S/Math.max(w,h); const nw=Math.round(w*sc), nh=Math.round(h*sc);
    const c=document.createElement('canvas'); c.width=S; c.height=S; const cx=c.getContext('2d'); cx.fillStyle='rgb(128,128,128)'; cx.fillRect(0,0,S,S);
    const ox=(S-nw)>>1, oy=(S-nh)>>1; cx.drawImage(canvas,0,0,w,h,ox,oy,nw,nh);
    const id=cx.getImageData(0,0,S,S).data; const f=new Float32Array(S*S*3); for(let i=0,j=0;i<id.length;i+=4,j+=3){ f[j]=id[i]/255; f[j+1]=id[i+1]/255; f[j+2]=id[i+2]/255; }
    return { x: tf.tensor4d(f,[1,S,S,3]), sc, ox, oy };
  }
  async function run(canvas, thr){
    thr = thr || 0.35;
    const {x, sc, ox, oy} = prep(canvas);
    const out = tf.tidy(() => {
      const e1=conv(conv(x,0),1), e2=conv(conv(e1,2),3), e3=conv(conv(conv(e2,4),5),6), e4=conv(conv(conv(e3,7),8),9), e5=conv(conv(e4,10),11);
      const d4=conv(tf.concat([up2(e5),e4],3),12), d3=conv(tf.concat([up2(d4),e3],3),13);
      const hm=tf.sigmoid(conv(conv(d3,14),15)), sz=conv(conv(d3,16),17);
      const mx=tf.maxPool(hm,3,1,'same'); const keep=tf.logicalAnd(tf.equal(hm,mx), tf.greaterEqual(hm,thr));
      return [hm, sz, keep];
    });
    const [hmT,szT,keepT]=out; const [hm,sz,keep]=await Promise.all([hmT.data(),szT.data(),keepT.data()]); tf.dispose([x,hmT,szT,keepT]);
    const HS=meta.input/meta.stride; const peaks=[];
    for(let i=0;i<keep.length;i++) if(keep[i]){ const yy=(i/HS)|0, xx=i%HS; const px=(xx+0.5)*meta.stride, py=(yy+0.5)*meta.stride;
      peaks.push({ x:(px-ox)/sc, y:(py-oy)/sc, score:hm[i], size:Math.exp(sz[i])*meta.stride/sc }); }
    return { peaks, hm, HS, sc, ox, oy };
  }
  return { load, run, get ready(){ return !!W; } };
})();
if(typeof window!=='undefined') window.PillNet=PillNet;
if(typeof module!=='undefined') module.exports=PillNet;
