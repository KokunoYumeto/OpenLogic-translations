import assert from 'node:assert/strict';
let checks = 0;
const check = (x,label) => { assert.ok(x,label); checks++; };
const truthRows = [];
for (const b of [false,true]) for (const c of [false,true]) {
 const and = b && c, or = b || c, imp = !b || c;
 check(!and === (!b || !c),'false conjunction');
 check(!or === (!b && !c),'false disjunction');
 check(!imp === (b && !c),'false implication');
 truthRows.push({b,c,true_disjunction:or,false_conjunction:!and,false_disjunction:!or,false_implication:!imp});
}
check((true || false) && !(!true || false), 'original T-disjunction alternatives fail when B=true,C=false');
check(!(true && false) && !(!true || !true), 'original false-conjunction IH fails when B=true,C=false');
check((!false && !false) && (false || true), 'repeated-B false-disjunction conclusion does not ensure F(B or C)');
check(!(true && !true) && !( !true || false ), 'original false-conditional conclusion impossible although conditional can be false');
let models = 0, worldCases = 0, reverseViolations = 0, forwardCounterexamples = 0;
for (let relation = 0; relation < 512; relation++) {
 const successors = Array.from({length:3}, (_,w)=>[0,1,2].filter(v=>relation & (1 << (w*3+v))));
 for (let pMask=0;pMask<8;pMask++) for(let qMask=0;qMask<8;qMask++) {
  models++;
  const p = w => !!(pMask & (1<<w)), q = w => !!(qMask & (1<<w));
  const box = (w,predicate)=>successors[w].every(predicate), diamond = (w,predicate)=>successors[w].some(predicate);
  for(let w=0;w<3;w++){
   worldCases++;
   const bothAtSuccessor=diamond(w,v=>p(v)&&q(v));
   const separateWitnesses=diamond(w,p)&&diamond(w,q);
   if(bothAtSuccessor && !separateWitnesses) reverseViolations++;
   if(separateWitnesses && !bothAtSuccessor) forwardCounterexamples++;
   check(box(w,p) === successors[w].every(p),'T-box used successors');
   check(!diamond(w,p) === successors[w].every(v=>!p(v)),'F-diamond used successors');
   check(!box(w,p) === successors[w].some(v=>!p(v)),'F-box witness');
   check(diamond(w,p) === successors[w].some(p),'T-diamond witness');
  }
 }
}
check(reverseViolations===0,'reverse diamond implication has no counterexample in bounded models');
check(forwardCounterexamples>0,'intended diamond implication has counterexamples');
const succ = [[1,2],[],[]];
const p = [false,true,false], q = [false,false,true];
const dia = f=>succ[0].some(f), box=f=>succ[0].every(f);
check(dia(i=>p[i]) && dia(i=>q[i]) && !dia(i=>p[i]&&q[i]), 'exact diamond diagram countermodel');
const pBox = [false,false,true], qBox = [false,true,false];
check(box(i=>pBox[i]||qBox[i]) && !(box(i=>pBox[i])||box(i=>qBox[i])),'exact box diagram countermodel');
console.log(JSON.stringify({status:'PASS',checks,truthRows,finite_models:models,world_cases:worldCases,reverse_diamond_violations:reverseViolations,intended_diamond_counterexamples:forwardCounterexamples,exact_worked_countermodels:2,scope:'Semantic checks only. No source/target byte check, TeX build, or full translation certification is performed by this public script.'},null,2));
