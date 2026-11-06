// CyberCampus shared frontend helpers (fictional lab)
const NAV = [["index.html","Home"],["courses.html","Courses"],["schedule.html","Schedule"],["profile.html","Profile"]];

function renderLayout(active){
  const logged = !!sessionStorage.getItem("cc_token");
  const links = NAV.map(([h,t]) => `<a href="/${h}" class="${h===active?'active':''}">${t}</a>`).join("");
  const auth = logged ? `<a href="#" id="logout">Logout</a>` : `<a href="/login.html" class="${active==='login.html'?'active':''}">Login</a>`;
  document.querySelector("header").innerHTML =
    `<div class="bar"><div class="brand">Cyber<span>Campus</span></div><nav>${links}${auth}</nav></div>`;
  document.querySelector("footer").textContent =
    "CyberCampus - fictional institution for the ENSIASD M111 lab. All data is fictional. Local use only.";
  const lo = document.getElementById("logout");
  if (lo) lo.onclick = async e => { e.preventDefault(); await api("/api/logout",{method:"POST"}); sessionStorage.clear(); location.href="/index.html"; };
}

async function api(path, opts = {}) {
  const headers = Object.assign({"Content-Type":"application/json"}, opts.headers || {});
  const token = sessionStorage.getItem("cc_token");
  if (token) headers["Authorization"] = "Bearer " + token;
  const res = await fetch(path, Object.assign({}, opts, {headers}));
  let data = null; try { data = await res.json(); } catch(_) {}
  return {status: res.status, ok: res.ok, data};
}

function requireLogin(){
  if (!sessionStorage.getItem("cc_token")) { location.href = "/login.html"; return false; }
  return true;
}
