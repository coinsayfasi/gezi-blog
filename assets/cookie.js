(function(){
  try{ if(localStorage.getItem('cookie_consent')) return; }catch(e){ return; }
  var d=document.createElement('div');
  d.id='cookie-banner';
  d.style.cssText='position:fixed;left:0;right:0;bottom:0;z-index:60;background:#ffffff;border-top:1px solid #ece8e1;color:#1f2733;padding:14px 18px;font-size:13.5px;line-height:1.55;box-shadow:0 -6px 24px rgba(31,39,51,.08)';
  d.innerHTML='<div style="max-width:1080px;margin:0 auto;display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between">'
    +'<span>Analiz ve reklam (Google AdSense dahil) için çerez kullanıyoruz. Detay: <a href="/cerez.html" style="color:#1380a6;font-weight:600">Çerez Politikası</a> · <a href="/gizlilik.html" style="color:#1380a6;font-weight:600">Gizlilik</a>.</span>'
    +'<span style="white-space:nowrap"><button id="ck-r" style="background:none;border:1px solid #d4cfc6;color:#69727f;padding:7px 14px;border-radius:9px;cursor:pointer;margin-right:8px;font-size:13px">Reddet</button>'
    +'<button id="ck-a" style="background:linear-gradient(110deg,#1380a6,#0f7a8c);border:0;color:#fff;padding:7px 17px;border-radius:9px;cursor:pointer;font-weight:600;font-size:13px">Kabul Et</button></span></div>';
  document.body.appendChild(d);
  function close(v){try{localStorage.setItem('cookie_consent',v);}catch(e){}if(window.__grantConsent)__grantConsent(v==='accepted');d.remove();}
  document.getElementById('ck-a').onclick=function(){close('accepted');};
  document.getElementById('ck-r').onclick=function(){close('rejected');};
})();
