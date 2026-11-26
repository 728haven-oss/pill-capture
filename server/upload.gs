// 알약캡쳐 사용자 사진 수집 서버 (Google Apps Script 웹 앱)
// 앱에서 사용자가 [사진 보내기]를 눌렀을 때만 사진 1장 + 개수·위치 정보(JSON)를 받아
// 이 계정의 Google Drive "알약캡쳐_사용자사진/날짜" 폴더에 저장합니다.
const KEY = 'pcu_d392ddf5e913c523';          // 앱에 들어있는 간단한 키(무작위 스팸 방지용)
const ROOT = '알약캡쳐_사용자사진';
const MAX_BYTES = 6 * 1024 * 1024;  // 사진 1장 최대 6MB
const DAILY_MAX = 1000;             // 하루 최대 저장 건수

function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    const b = JSON.parse(e.postData.contents);
    if (b.k !== KEY) return out({ ok: false, err: 'key' });
    const meta = b.meta || {};
    const img = Utilities.base64Decode(String(b.img || ''));
    if (!img.length || img.length > MAX_BYTES) return out({ ok: false, err: 'size' });

    lock.waitLock(20000);
    const day = Utilities.formatDate(new Date(), 'Asia/Seoul', 'yyyyMMdd');
    const props = PropertiesService.getScriptProperties();
    const cnt = Number(props.getProperty('cnt_' + day) || 0);
    if (cnt >= DAILY_MAX) return out({ ok: false, err: 'daily' });
    props.setProperty('cnt_' + day, String(cnt + 1));

    const folder = sub(sub(DriveApp.getRootFolder(), ROOT), day);
    const safe = s => String(s == null ? '' : s).replace(/[^0-9A-Za-z_-]/g, '').slice(0, 40);
    const name = safe(meta.id || Date.now()) + '_app' + safe(meta.shown_total) + '_real' + safe(meta.actual);
    folder.createFile(Utilities.newBlob(img, 'image/jpeg', name + '.jpg'));
    meta.received = new Date().toISOString();
    folder.createFile(name + '.json', JSON.stringify(meta, null, 1), 'application/json');
    return out({ ok: true });
  } catch (err) {
    return out({ ok: false, err: String(err).slice(0, 200) });
  } finally {
    try { lock.releaseLock(); } catch (_) {}
  }
}

function doGet() { return out({ ok: true, service: 'pillcapture-upload' }); }

function sub(parent, name) {
  const it = parent.getFoldersByName(name);
  return it.hasNext() ? it.next() : parent.createFolder(name);
}
function out(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
