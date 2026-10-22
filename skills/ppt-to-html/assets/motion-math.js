/* Pure geometry and timeline helpers; no optimization solver is included. */
((root)=>{
  'use strict';
  const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
  const lerp=(a,b,t)=>a+(b-a)*t;
  const ease=t=>{t=clamp(t);return t*t*(3-2*t);};
  const distance=(a,b)=>Math.hypot(b[0]-a[0],b[1]-a[1]);
  const length=points=>points.slice(1).reduce((sum,p,i)=>sum+distance(points[i],p),0);
  function pointAt(points,t){
    const total=length(points);let remaining=clamp(t)*total;
    for(let i=1;i<points.length;i++){
      const d=distance(points[i-1],points[i]);
      if(remaining<=d&&d>0)return [lerp(points[i-1][0],points[i][0],remaining/d),lerp(points[i-1][1],points[i][1],remaining/d)];
      remaining-=d;
    }
    return points[points.length-1].slice();
  }
  const route=(story,ids)=>[story.hub,...ids.map(i=>story.stops[i]),story.hub];
  const totalLength=(story,plan)=>plan.reduce((sum,ids)=>sum+length(route(story,ids)),0);
  const project=(x,y,z=0)=>[635+(x-y)*.57,142+(x+y)*.28-z];
  const phase=(time,duration,count=4)=>Math.min(count-1,Math.floor(clamp(time/duration)*count));
  const api={clamp,lerp,ease,distance,length,pointAt,route,totalLength,project,phase};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.MotionMath=api;
})(globalThis);
