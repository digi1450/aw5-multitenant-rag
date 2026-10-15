'use strict';
const message = document.querySelector('#message');
const form = document.querySelector('#enroll');
let csrf = '', requestId = null, previousData = null;
function status(text) { message.textContent = text; }
async function api(path, method = 'GET', data) {
  const response = await fetch('/v1/admin/portal/' + path, {
    method, credentials: 'same-origin', redirect: 'error',
    headers: {'Content-Type': 'application/json', 'X-AW5-CSRF': csrf},
    body: data === undefined ? undefined : JSON.stringify(data)
  });
  const raw = await response.text();
  let result; try { result = JSON.parse(raw); } catch { result = {}; }
  if (!response.ok) {
    if (response.status === 403) throw new Error('ลิงก์หรือสิทธิ์หมดอายุ ใช้ /aw5-admin ใน Discord เพื่อเปิดใหม่');
    throw new Error(result.error || raw || 'ติดต่อระบบไม่สำเร็จ');
  }
  return result;
}
function roleMode() {
  const existing = form.elements.role_mode.value === 'existing';
  document.querySelector('#role-label').hidden = !existing;
  document.querySelector('#roles').required = existing;
}
form.elements.role_mode.forEach(element => element.addEventListener('change', roleMode));
async function refresh() {
  const model = await api('model'); csrf = model.csrf;
  const projects = document.querySelector('#projects'); projects.replaceChildren();
  if (!model.projects.length) projects.textContent = 'ยังไม่มีโปรเจกต์';
  for (const project of model.projects) {
    const row = document.createElement('div'); row.className = 'project';
    const roleName = project.discord_role_name || `${project.discord_role_id} (ไม่สามารถโหลดชื่อยศได้)`;
    const heading = document.createElement('div'); heading.className = 'project-heading';
    const description = document.createElement('span');
    description.textContent = `${project.tenant_name} · Tenant ${project.tenant_id}\nสถานะ: ${project.status} · ยศ: ${roleName}`;
    const remove = document.createElement('button'); remove.type = 'button';
    remove.className = 'delete-project'; remove.textContent = 'ลบ';
    remove.setAttribute('aria-label', `ลบโปรเจกต์ ${project.tenant_name}`);
    remove.addEventListener('click', async () => {
      const name = prompt(`ลบ ${project.tenant_name} (Tenant ${project.tenant_id}) ออกจาก AW5?\nจะลบทะเบียนและข้อมูล ticket/conversation ที่ผูกใน AW5 กู้คืนผ่าน Portal ไม่ได้\nไม่ลบยศหรือข้อความ Discord และไม่ลบแอป/เอกสาร/conversation ใน Dify\nพิมพ์ชื่อโปรเจกต์เพื่อยืนยัน: ${project.tenant_name}`);
      if (name === null) return;
      if (name !== project.tenant_name) { status('ชื่อยืนยันไม่ตรง ยังไม่ได้ลบโปรเจกต์'); return; }
      remove.disabled = true;
      try {
        const result = await api(`projects/${project.tenant_id}`, 'DELETE', {
          confirmation_name: name, dify_app_id: project.dify_app_id, discord_role_id: project.discord_role_id
        });
        await refresh();
        status(`ลบ ${project.tenant_name} ออกจาก AW5 แล้ว (${result.deleted_tickets} ticket) — ลงทะเบียนใหม่ได้ โดยต้องเปิด ticket ใหม่`);
      } catch (error) { status(error.message); }
      finally { remove.disabled = false; }
    });
    heading.append(description, remove); row.append(heading);
    const details = document.createElement('details');
    const summary = document.createElement('summary'); summary.textContent = 'ดู Role ID';
    const id = document.createElement('code'); id.textContent = project.discord_role_id;
    details.append(summary, id); row.append(details);
    const appDetails = document.createElement('details');
    const appSummary = document.createElement('summary'); appSummary.textContent = 'ดู Dify App ID';
    const appId = document.createElement('code'); appId.textContent = project.dify_app_id;
    appDetails.append(appSummary, appId); row.append(appDetails);
    const edit = document.createElement('details');
    const editTitle = document.createElement('summary'); editTitle.textContent = 'เปลี่ยนยศที่ผูก';
    const roleForm = document.createElement('form');
    const label = document.createElement('label'); label.textContent = 'ยศใหม่สำหรับโปรเจกต์นี้';
    const select = document.createElement('select'); select.required = true;
    select.append(new Option('เลือกยศ…', ''));
    for (const role of model.roles) select.add(new Option(`${role.name} (${role.id})`, role.id));
    if (model.can_create) select.add(new Option('สร้างยศใหม่ตามชื่อโปรเจกต์', 'new'));
    label.append(select);
    const help = document.createElement('p');
    help.textContent = 'เปลี่ยนสิทธิ์เข้าถึงทันที ไม่ลบยศเดิม ไม่เพิ่มสมาชิกให้อัตโนมัติ และไม่เปลี่ยน Dify app หรือประวัติ ticket';
    const save = document.createElement('button'); save.type = 'submit'; save.textContent = 'ยืนยันเปลี่ยนยศ';
    let changeRequest = null, changeSelection = null;
    roleForm.addEventListener('submit', async event => {
      event.preventDefault();
      if (!confirm(`เปลี่ยนยศที่เข้าถึง ${project.tenant_name}? สมาชิกต้องมียศใหม่จึงจะใช้งานต่อได้`)) return;
      if (changeSelection !== select.value) { changeSelection = select.value; changeRequest = crypto.randomUUID(); }
      save.disabled = true;
      try {
        await api(`projects/${project.tenant_id}/role`, 'POST', {
          request_id: changeRequest, role_mode: select.value === 'new' ? 'new' : 'existing',
          discord_role_id: select.value === 'new' ? undefined : select.value
        });
        await refresh(); status(`เปลี่ยนยศของ ${project.tenant_name} สำเร็จ — มอบยศใหม่ให้สมาชิกใน Discord เพื่อใช้งาน`);
      } catch (error) { status(error.message); }
      finally { save.disabled = false; }
    });
    roleForm.append(label, help, save); edit.append(editTitle, roleForm); row.append(edit);
    projects.append(row);
  }
  const roles = document.querySelector('#roles'); roles.replaceChildren(new Option('เลือกยศ…', ''));
  for (const role of model.roles) roles.add(new Option(`${role.name} (${role.id})`, role.id));
  document.querySelector('#new-role').disabled = !model.can_create;
  document.querySelector('#role-help').textContent = model.can_create ? 'ยศใหม่ไม่มีสิทธิ์จัดการเซิร์ฟเวอร์ ใช้ระบุสมาชิกโปรเจกต์เท่านั้น' : 'หากต้องการสร้างยศใหม่ ให้เปิด Manage Roles สำหรับ AW5-Bot ก่อน แล้วเปิดหน้านี้ใหม่';
  roleMode(); document.querySelector('#workspace').hidden = false; document.querySelector('#logout').hidden = false;
}
form.addEventListener('submit', async event => {
  event.preventDefault(); const submit = document.querySelector('#submit'); submit.disabled = true;
  const data = Object.fromEntries(new FormData(form));
  // Keep a retry identity only in this page's memory. Never persist credentials.
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(JSON.stringify(data)));
  const signature = Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, "0")).join("");
  if (signature !== previousData) { requestId = crypto.randomUUID(); previousData = signature; }
  data.request_id = requestId;
  status('กำลังตรวจคีย์, Published workflow, metadata และยศ… กรุณารอ');
  try {
    const project = await api('projects', 'POST', data);
    form.reset(); previousData = null; requestId = null;
    await refresh();
    const next = project.status === 'active' ? 'มอบยศให้สมาชิกใน Discord ได้เลย' : 'ยังไม่พร้อมใช้งาน ตรวจ metadata และ Published workflow ก่อน';
    status(`ลงทะเบียน ${project.tenant_name} สำเร็จ · Tenant ${project.tenant_id} · สถานะ ${project.status} — ${next}`);
  } catch (error) { status(error.message); }
  finally { submit.disabled = false; }
});
document.querySelector('#logout').addEventListener('click', async () => {
  try { await api('logout', 'POST', {}); } catch (_) {}
  csrf = ''; previousData = null; form.reset(); document.querySelector('#workspace').hidden = true;
  document.querySelector('#logout').hidden = true; status('ออกจากระบบแล้ว');
});
(async () => {
  const token = new URLSearchParams(location.hash.slice(1)).get('login');
  history.replaceState(null, '', '/admin');
  try {
    if (token) { const result = await api('session', 'POST', {token}); csrf = result.csrf; }
    await refresh(); status('ตรวจสิทธิ์แล้ว พร้อมลงทะเบียนโปรเจกต์');
  } catch (error) { status(error.message); }
})();
