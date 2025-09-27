(function(){
  const profileName = "Profile_5";
  try {
    const apply = () => {
      const t = document.title || '';}
    ;
  } catch(e) {}
  const prefix = profileName + ' | ';
  const set = () => {
    try {
      if (!document.title.startsWith(prefix)) {
        document.title = prefix + document.title;
      }
    } catch(e) {}
  };
  set();
  const obs = new MutationObserver(set);
  try { obs.observe(document.querySelector('title') || document.documentElement, {subtree:true, childList:true, characterData:true}); } catch(e) {}
})();
