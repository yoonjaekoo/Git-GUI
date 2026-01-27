import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
import os
import subprocess

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Git GUI")
        self.geometry("400x550")
        self.folder_path = ""
        self.load_saved_path()
        self.setup_ui()
        if not self.folder_path:
            self.after(100, self.select_folder)

    def setup_ui(self):
        self.title_label = ctk.CTkLabel(self, text="Git GUI", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)
        self.folder_label = ctk.CTkLabel(self, text=self.folder_path if self.folder_path else "Git 폴더 선택 안 됨", wraplength=350)
        self.folder_label.pack(pady=10)

        # 버튼들
        self.btn_folder = ctk.CTkButton(self, text="📁 폴더 선택", command=self.select_folder)
        self.btn_user   = ctk.CTkButton(self, text="👤 사용자 정보", command=self.open_user_window)
        self.btn_commit = ctk.CTkButton(self, text="📝 커밋", command=self.open_commit_window)
        self.btn_push   = ctk.CTkButton(self, text="⬆️ 푸시", command=self.execute_push)
        self.btn_sync   = ctk.CTkButton(self, text="🔄 동기화", command=self.execute_sync) # 연결!
        self.btn_repo   = ctk.CTkButton(self, text="📦 리포지토리", command=self.open_repo_window) # 연결!

        for btn in (self.btn_folder, self.btn_user, self.btn_commit, self.btn_push, self.btn_sync, self.btn_repo):
            btn.pack(pady=6, ipadx=10, ipady=5)

    def load_saved_path(self):
        try:
            if os.path.exists("folderpath.txt"):
                with open("folderpath.txt", "r", encoding="utf-8") as f:
                    path = f.read().strip()
                    if path and os.path.exists(path): self.folder_path = path
        except: pass

    def is_git_repo(self, path):
        return os.path.isdir(os.path.join(path, ".git"))

    def select_folder(self):
        path = filedialog.askdirectory()
        if not path: return
        self.folder_path = path
        self.folder_label.configure(text=path)
        with open("folderpath.txt", "w", encoding="utf-8") as f: f.write(path)

    def run_git_command(self, args):
        if not self.folder_path: return ""
        try:
            result = subprocess.check_output(
                ["git", "-C", self.folder_path] + args,
                stderr=subprocess.STDOUT, text=True, encoding="utf-8"
            )
            return result.strip()
        except Exception as e:
            return ""

    # --- 사용자 정보 & 커밋 & 푸시 (기존과 동일) ---
    def open_user_window(self):
        if not self.folder_path: return
        self.user_win = ctk.CTkToplevel(self)
        self.user_win.title("사용자 정보")
        self.user_win.geometry("300x280")
        self.user_win.attributes("-topmost", True)
        current_name = self.run_git_command(["config", "user.name"])
        current_email = self.run_git_command(["config", "user.email"])
        ctk.CTkLabel(self.user_win, text="Git 사용자 이름:").pack(pady=(20, 0))
        self.name_entry = ctk.CTkEntry(self.user_win, width=220); self.name_entry.insert(0, current_name); self.name_entry.pack(pady=5)
        ctk.CTkLabel(self.user_win, text="Git 이메일:").pack(pady=(10, 0))
        self.email_entry = ctk.CTkEntry(self.user_win, width=220); self.email_entry.insert(0, current_email); self.email_entry.pack(pady=5)
        ctk.CTkButton(self.user_win, text="저장", command=self.save_user_info).pack(pady=25)

    def save_user_info(self):
        self.run_git_command(["config", "user.name", self.name_entry.get().strip()])
        self.run_git_command(["config", "user.email", self.email_entry.get().strip()])
        messagebox.showinfo("성공", "정보 업데이트 완료!")
        self.user_win.destroy()

    def open_commit_window(self):
        status = self.run_git_command(["status", "--short"])
        if not status: messagebox.showinfo("알림", "변경사항이 없어!"); return
        self.commit_win = ctk.CTkToplevel(self); self.commit_win.title("커밋"); self.commit_win.geometry("400x420")
        self.commit_win.attributes("-topmost", True)
        self.status_display = ctk.CTkTextbox(self.commit_win, width=350, height=120); self.status_display.insert("0.0", status); self.status_display.configure(state="disabled"); self.status_display.pack(pady=20)
        self.commit_entry = ctk.CTkEntry(self.commit_win, width=350, placeholder_text="커밋 메시지"); self.commit_entry.pack(pady=5)
        ctk.CTkButton(self.commit_win, text="✅ 커밋 실행", command=self.execute_commit).pack(pady=20)

    def execute_commit(self):
        msg = self.commit_entry.get().strip()
        if not msg: return
        self.run_git_command(["add", "."])
        self.run_git_command(["commit", "-m", msg])
        messagebox.showinfo("성공", "커밋 완료!"); self.commit_win.destroy()

    def execute_push(self):
        branch = self.run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        if not branch: messagebox.showerror("오류", "리포지토리가 아니거나 브랜치가 없어."); return
        if messagebox.askyesno("푸시", f"'{branch}'로 푸시할까?"):
            self.run_git_command(["push", "origin", branch])
            messagebox.showinfo("완료", "푸시 성공!")

    # --- 🔄 동기화 기능 추가 ---
    def execute_sync(self):
        branch = self.run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        if not branch: messagebox.showerror("오류", "리포지토리가 아니야."); return
        messagebox.showinfo("알림", "서버와 동기화 중...")
        result = self.run_git_command(["pull", "origin", branch])
        messagebox.showinfo("완료", "동기화(Pull) 작업을 마쳤어!")

    # --- 📦 리포지토리 관리 창 ---
    def open_repo_window(self):
        if not self.folder_path:
            messagebox.showwarning("알림", "폴더를 먼저 선택해줘.")
            return

        self.repo_win = ctk.CTkToplevel(self)
        self.repo_win.title("리포지토리 관리")
        self.repo_win.geometry("300x250")
        self.repo_win.attributes("-topmost", True)

        ctk.CTkLabel(self.repo_win, text="리포지토리 설정", font=ctk.CTkFont(weight="bold")).pack(pady=15)

        # Git 초기화 버튼
        btn_init = ctk.CTkButton(self.repo_win, text="🆕 새 Git 만들기 (Init)", 
                                 fg_color="#2c3e50", command=self.execute_init)
        btn_init.pack(pady=10)

        # GitHub 연결 버튼
        btn_remote = ctk.CTkButton(self.repo_win, text="🔗 GitHub 연결 (Remote)", 
                                   fg_color="#27ae60", command=self.execute_remote_add)
        btn_remote.pack(pady=10)

    def execute_init(self):
        if self.is_git_repo(self.folder_path):
            messagebox.showinfo("알림", "이미 Git 리포지토리야!")
            return
        
        self.run_git_command(["init"])
        # 기본 브랜치 이름을 main으로 설정 (요즘 트렌드)
        self.run_git_command(["branch", "-M", "main"])
        messagebox.showinfo("성공", "이 폴더에 새로운 Git 저장소를 만들었어!")
        self.repo_win.destroy()

    def execute_remote_add(self):
        url = simpledialog.askstring("GitHub 연결", "GitHub 저장소 주소(URL)를 입력해줘:\n(예: https://github.com/유저명/저장소명.git)")
        if not url: return

        # 기존 리모트가 있는지 확인 후 삭제하거나 추가
        self.run_git_command(["remote", "remove", "origin"]) # 기존꺼 삭제 (안전하게)
        self.run_git_command(["remote", "add", "origin", url])
        
        messagebox.showinfo("성공", f"이제 이 폴더는 다음 주소와 연결됐어:\n{url}")
        self.repo_win.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()