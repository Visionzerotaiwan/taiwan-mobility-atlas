const fs=require('fs');
function loadA1(f){const s=fs.readFileSync(f,"utf8");const st=s.indexOf("window.CITY_A1");const lb=s.indexOf("[",s.indexOf("=",st));let d=0,inStr=false,esc=false,end=-1;for(let i=lb;i<s.length;i++){const c=s[i];if(inStr){if(esc)esc=false;else if(c==="\\")esc=true;else if(c===String.fromCharCode(34))inStr=false;continue;}if(c===String.fromCharCode(34))inStr=true;else if(c==="[")d++;else if(c==="]"){if(--d===0){end=i;break;}}}return JSON.parse(s.slice(lb,end+1));}
function cat(vm){if(!vm)return"其他";if(vm==="人")return"人";if(vm.includes("機車")||vm.includes("機踏車"))return"機車";if(vm.includes("自行車")||vm.includes("腳踏")||vm.includes("慢車"))return"慢車";if(/客車|貨車|曳引|聯結|貨/.test(vm))return"汽車";return"其他";}
function ageBand(a){a=+a;if(!a&&a!==0)return null;if(a<=17)return"兒少";if(a<=29)return"青年";if(a<=49)return"壯年";if(a<=64)return"中年";return"高齡";}
const SLUGS=['taipei','newtaipei','taoyuan','taichung','tainan','kaohsiung','changhua','miaoli','yunlin','chiayi','pingtung','nantou','yilan','hsinchu','taitung','hualien','hsinchucity','chiayicity','keelung','kinmen','penghu','lienchiang'];
const MODES=['機車','汽車','人','慢車','其他'];
function blank(){return{deaths:0, ident:0, m:0, f:0, byMode:Object.fromEntries(MODES.map(k=>[k,{m:0,f:0}])), byAge:{}};}
function deceasedGender(r){ // returns {gender, age, mode} or null
  if(!r.parties||!r.parties.length)return null;
  const match=r.parties.filter(p=>cat(p.vehicle_main)===r.mode && p.gender);
  if(match.length===1)return{gender:match[0].gender,age:match[0].age,mode:r.mode};
  if(match.length>1){const g=[...new Set(match.map(p=>p.gender))]; if(g.length===1){const oldest=match.slice().sort((a,b)=>(+b.age||0)-(+a.age||0))[0]; return{gender:g[0],age:oldest.age,mode:r.mode};}}
  return null;
}
const out={};
const nat=blank();
for(const slug of SLUGS){
  const arr=loadA1("data/"+slug+".js");
  const c=blank();
  for(const r of arr){
    const dn=r.deaths||0; c.deaths+=dn; nat.deaths+=dn;
    const dec=deceasedGender(r);
    if(!dec)continue;
    const g=dec.gender==="男"?"m":dec.gender==="女"?"f":null; if(!g)continue;
    c.ident++; c[g]++; nat.ident++; nat[g]++;
    const md=MODES.includes(dec.mode)?dec.mode:"其他"; c.byMode[md][g]++; nat.byMode[md][g]++;
    const ab=ageBand(dec.age); if(ab){c.byAge[ab]=c.byAge[ab]||{m:0,f:0}; c.byAge[ab][g]++; nat.byAge[ab]=nat.byAge[ab]||{m:0,f:0}; nat.byAge[ab][g]++;}
  }
  out[slug]=c;
}
out.national=nat;
fs.writeFileSync("data/gender.json",JSON.stringify(out));
// report
function pct(o){const t=o.m+o.f;return t?((o.m/t*100).toFixed(0)+"% 男 / "+(o.f/t*100).toFixed(0)+"% 女"):"—";}
console.log("全國 A1 死者性別（可辨識 "+nat.ident+" / 總死亡 "+nat.deaths+"，涵蓋 "+(nat.ident/nat.deaths*100).toFixed(0)+"%）：",pct(nat));
console.log("\n按死者運具（全國）：");
for(const md of MODES){const o=nat.byMode[md];const t=o.m+o.f;console.log("  "+md.padEnd(3)+" 死者"+String(t).padStart(4)+"  "+pct(o));}
console.log("\n按年齡層（全國）：");
for(const ab of ["兒少","青年","壯年","中年","高齡"]){const o=nat.byAge[ab];if(o)console.log("  "+ab.padEnd(3)+" 死者"+String(o.m+o.f).padStart(4)+"  "+pct(o));}
console.log("\nwritten data/gender.json ("+(fs.statSync('data/gender.json').size/1024).toFixed(1)+"KB)");
