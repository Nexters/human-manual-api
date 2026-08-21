import json


def render_admin_page(page: str, result_code: str | None = None) -> str:
    config = json.dumps({"page": page, "resultCode": result_code}, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pakit Admin</title>
  <style>
    :root {{ color-scheme: dark; --bg:#11131a; --panel:#1b1e29; --line:#303545;
      --text:#f4f5f8; --muted:#9da5ba; --accent:#8ea2ff; }}
    * {{ box-sizing:border-box }} body {{ margin:0; background:var(--bg); color:var(--text);
      font-family:system-ui,-apple-system,sans-serif }}
    header {{ position:sticky;top:0;background:#11131aee;border-bottom:1px solid var(--line);
      padding:18px 24px;display:flex;gap:24px;align-items:center;z-index:2 }}
    header strong {{font-size:20px}} nav a {{color:var(--muted);text-decoration:none;margin-right:16px}}
    main {{max-width:1280px;margin:0 auto;padding:28px 24px 60px}}
    h1 {{font-size:28px;margin:0 0 22px}} h2 {{font-size:19px;margin:28px 0 12px}}
    .cards {{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}}
    .card,.panel {{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px}}
    .label {{color:var(--muted);font-size:13px}} .value {{font-size:27px;font-weight:800;margin-top:7px}}
    .grid {{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}}
    table {{width:100%;border-collapse:collapse;font-size:14px}} th,td {{text-align:left;padding:11px 9px;
      border-bottom:1px solid var(--line);white-space:nowrap}} th {{color:var(--muted)}}
    .scroll {{overflow:auto}} a {{color:var(--accent)}} input,select,button {{background:#151823;color:var(--text);
      border:1px solid var(--line);border-radius:8px;padding:10px}} button {{cursor:pointer;background:#536de8}}
    form {{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}} pre {{white-space:pre-wrap;word-break:break-word;
      background:#0d0f15;border-radius:10px;padding:16px;max-height:70vh;overflow:auto}}
    .error {{color:#ff9da7}} .pill {{display:inline-block;padding:4px 8px;border-radius:99px;background:#282d3d;
      margin:2px;font-size:12px}} @media(max-width:700px){{header{{display:block}}nav{{margin-top:10px}}}}
  </style>
</head>
<body>
<header><strong>Pakit Admin</strong><nav><a href="/admin">대시보드</a><a href="/admin/results">전체 결과</a><a href="/admin/analytics">통계</a></nav></header>
<main id="app"><p class="label">불러오는 중…</p></main>
<script>
const CONFIG = {config};
const app = document.querySelector('#app');
const esc = value => String(value ?? '-').replace(/[&<>"']/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[ch]));
const pct = value => value == null ? '계측 전/데이터 없음' : `${{value}}%`;
async function api(path) {{ const response = await fetch(path); if(!response.ok) throw new Error(`${{response.status}} ${{await response.text()}}`); return response.json(); }}
function dist(title, items) {{ return `<section class="panel"><h2>${{esc(title)}}</h2>${{items.length ? items.map(x=>`<div>${{esc(x.key)}} <b>${{x.count}}</b> <span class="label">(${{x.ratio}}%)</span></div>`).join('') : '<p class="label">데이터 없음</p>'}}</section>`; }}
async function dashboard() {{ const d=await api('/api/admin/dashboard'); app.innerHTML=`<h1>운영 대시보드</h1><div class="cards">
  ${{[['오늘 결과',d.counts.today_results],['7일 결과',d.counts.seven_day_results],['30일 결과',d.counts.thirty_day_results],['누적 결과',d.counts.total_results],['오늘 궁합',d.counts.today_compatibility],['7일 궁합',d.counts.seven_day_compatibility],['궁합 경험 비율',pct(d.experience_ratio)],['조회→궁합 전환',pct(d.view_to_compatibility_ratio)]].map(([l,v])=>`<div class="card"><div class="label">${{l}}</div><div class="value">${{v}}</div></div>`).join('')}}</div>
  <h2>최근 7일 추이</h2><div class="panel scroll"><table><thead><tr><th>날짜</th><th>결과</th><th>조회</th><th>궁합</th></tr></thead><tbody>${{d.trend.map(x=>`<tr><td>${{x.date}}</td><td>${{x.results}}</td><td>${{x.views}}</td><td>${{x.compatibility}}</td></tr>`).join('')}}</tbody></table></div>
  <div class="grid">${{dist('MBTI 상위',d.top_mbti)}}${{dist('장난감 상위',d.top_characters)}}${{dist('키워드 상위',d.top_tags)}}${{dist('궁합 조합 상위',d.top_compatibility_pairs)}}</div>`; }}
async function results(query='') {{
  const params = new URLSearchParams(query);
  const d = await api('/api/admin/results?' + params);
  app.innerHTML=`<h1>전체 결과 <span class="label">${{d.total}}건</span></h1>
  <form id="search">
    <input name="result_code" placeholder="결과 코드"><input name="nickname" placeholder="닉네임">
    <input name="mbti" placeholder="MBTI"><input name="character_id" placeholder="장난감 ID">
    <input name="tag" placeholder="키워드"><input name="date_from" type="date"><input name="date_to" type="date">
    <input name="assessment_version" placeholder="문항 버전"><input name="content_version" placeholder="콘텐츠 버전">
    <select name="has_compatibility"><option value="">궁합 전체</option><option value="true">궁합 있음</option><option value="false">궁합 없음</option></select>
    <select name="sort"><option value="newest">최신순</option><option value="oldest">오래된순</option></select><button>검색</button>
  </form>
  <div class="panel scroll"><table><thead><tr><th>생성</th><th>코드</th><th>닉네임</th><th>MBTI</th><th>결과</th><th>키워드</th><th>축 점수</th><th>버전</th><th>조회</th><th>궁합</th></tr></thead><tbody>${{d.items.map(x=>`<tr><td>${{new Date(x.created_at).toLocaleString('ko-KR')}}</td><td><a href="/admin/results/${{esc(x.result_code)}}">${{esc(x.result_code)}}</a></td><td>${{esc(x.nickname)}}</td><td>${{esc(x.mbti)}}</td><td>${{esc(x.result_name)}}</td><td>${{x.tags.map(t=>`<span class="pill">${{esc(t)}}</span>`).join('')}}</td><td>${{Object.values(x.axis_scores).join(' / ')}}</td><td>${{esc(x.assessment_version)}}<br>${{esc(x.content_version)}}</td><td>${{x.view_count}}</td><td>${{x.compatibility_count}}</td></tr>`).join('')}}</tbody></table></div>
  <p><button id="prev" ${{d.page<=1?'disabled':''}}>이전</button> <span class="label">${{d.page}} / ${{d.pages || 1}}</span> <button id="next" ${{d.page>=d.pages?'disabled':''}}>다음</button></p>`;
  const form=document.querySelector('#search');
  for(const [key,value] of params) if(form.elements[key]) form.elements[key].value=value;
  form.addEventListener('submit',e=>{{e.preventDefault();const q=new URLSearchParams(new FormData(e.target));for(const [k,v] of [...q])if(!v)q.delete(k);q.delete('page');results(q)}});
  document.querySelector('#prev').addEventListener('click',()=>{{params.set('page',String(d.page-1));results(params)}});
  document.querySelector('#next').addEventListener('click',()=>{{params.set('page',String(d.page+1));results(params)}});
}}
async function detail() {{ const d=await api('/api/admin/results/'+encodeURIComponent(CONFIG.resultCode)); app.innerHTML=`<h1>${{esc(d.result_code)}} 상세</h1><div class="cards"><div class="card"><div class="label">닉네임</div><div class="value">${{esc(d.nickname)}}</div></div><div class="card"><div class="label">공개 조회</div><div class="value">${{d.usage.view_count}}</div></div><div class="card"><div class="label">궁합</div><div class="value">${{d.usage.compatibility_count}}</div></div></div><h2>생성 당시 스냅샷</h2><pre id="snapshot"></pre>`;document.querySelector('#snapshot').textContent=JSON.stringify(d,null,2); }}
async function analytics(query='') {{
  const params=new URLSearchParams(query);
  const suffix=params.toString()?'?'+params:'';
  const [r,c]=await Promise.all([api('/api/admin/analytics/results'+suffix),api('/api/admin/analytics/compatibility'+suffix)]);
  app.innerHTML=`<h1>백엔드 통계</h1><form id="period"><input name="date_from" type="date"><input name="date_to" type="date"><button>기간 적용</button></form><div class="cards"><div class="card"><div class="label">생성 결과</div><div class="value">${{r.total_results}}</div></div><div class="card"><div class="label">결과 조회</div><div class="value">${{c.result_view_count}}</div></div><div class="card"><div class="label">조회된 결과 비율</div><div class="value">${{pct(c.viewed_result_ratio)}}</div></div><div class="card"><div class="label">궁합 완료</div><div class="value">${{c.completed_count}}</div></div><div class="card"><div class="label">궁합 경험 비율</div><div class="value">${{pct(c.experience_ratio)}}</div></div><div class="card"><div class="label">조회→궁합 전환</div><div class="value">${{pct(c.view_to_compatibility_ratio)}}</div></div><div class="card"><div class="label">평균 궁합 점수</div><div class="value">${{c.average_score ?? '-'}}</div></div></div><div class="grid">${{dist('MBTI',r.mbti)}}${{dist('장난감',r.characters)}}${{dist('키워드',r.tags)}}${{dist('궁합 조합',c.mbti_combinations)}}${{dist('궁합 버전',c.versions)}}</div><h2>성향 축</h2><pre>${{esc(JSON.stringify(r.axes,null,2))}}</pre>`;
  const form=document.querySelector('#period');for(const [key,value] of params)if(form.elements[key])form.elements[key].value=value;
  form.addEventListener('submit',e=>{{e.preventDefault();const q=new URLSearchParams(new FormData(e.target));for(const [k,v] of [...q])if(!v)q.delete(k);analytics(q)}});
}}
(async()=>{{try{{if(CONFIG.page==='dashboard')await dashboard();else if(CONFIG.page==='results')await results();else if(CONFIG.page==='detail')await detail();else await analytics();}}catch(error){{app.innerHTML=`<p class="error">불러오지 못했습니다: ${{esc(error.message)}}</p>`}}}})();
</script></body></html>"""
