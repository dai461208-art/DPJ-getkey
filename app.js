const notice = document.getElementById("notice");
const state = document.getElementById("state");
const keyArea = document.getElementById("key-area");
const params = new URLSearchParams(location.search);
const session = params.get("session");

async function start() {
  if (!session) {
    notice.textContent = "Thiếu mã phiên. Hãy lấy link mới bằng lệnh /getkey trong bot.";
    return;
  }
  try {
    const res = await fetch(`/api/claim?session=${encodeURIComponent(session)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Không thể xác minh phiên.");
    state.hidden = true;
    keyArea.hidden = false;
    document.getElementById("key-value").textContent = data.key;
    notice.textContent = "Đã cấp key thành công. Nhập key vào bot Telegram để nhận 1 lượt.";
  } catch (e) {
    notice.textContent = e.message;
  }
}
document.getElementById("copy").addEventListener("click", async () => {
  const value = document.getElementById("key-value").textContent;
  try {
    await navigator.clipboard.writeText(value);
    document.getElementById("copy").textContent = "ĐÃ SAO CHÉP";
  } catch {
    notice.textContent = "Không thể tự sao chép. Hãy chọn và sao chép key thủ công.";
  }
});
start();
