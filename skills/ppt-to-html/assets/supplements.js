/* Supporting HTML runs in a sandboxed dialog; the presentation keeps its step. */
(()=>{
 const deck=JSON.parse(document.getElementById('deck-data').textContent),dialog=document.getElementById('supplements-dialog'),frames=[document.getElementById('supplement-frame')];let selected=0;
 function select(index){selected=index;const item=deck.supplements[index];if(!frames[index]){const frame=document.createElement('iframe');frame.id='supplement-resource-'+index;frame.setAttribute('sandbox','allow-scripts allow-downloads allow-forms allow-modals');dialog.append(frame);frames[index]=frame;}const frame=frames[index];frame.className='supplement-resource';if(!frame.srcdoc)frame.srcdoc=item.html;frame.title=item.label;frames.forEach((n,i)=>n.hidden=i!==index);document.querySelectorAll('#supplement-tabs button').forEach((n,i)=>n.setAttribute('aria-pressed',String(i===index)));}
 deck.supplements.forEach((item,index)=>{const button=document.createElement('button');button.type='button';button.textContent=item.label;button.addEventListener('click',()=>select(index));document.getElementById('supplement-tabs').append(button);});
 document.getElementById('open-supplements').addEventListener('click',()=>{dispatchEvent(new Event('ppt-open-supplement'));select(selected);dialog.showModal();});
 document.getElementById('close-supplements').addEventListener('click',()=>dialog.close());
 dialog.addEventListener('close',()=>{document.getElementById('open-supplements').focus();});
})();
