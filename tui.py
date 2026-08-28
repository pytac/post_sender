from textual.app import App, ComposeResult
from textual.containers import *
from textual.widgets import *
from textual import on
from os.path import exists
import time
import requests
import json
import threading
from tkinter import filedialog, Tk

def process_str(string: str):
    string = string.strip()
    if string.startswith('"') or string.startswith("'"):
        string = string[1:]
    if string.endswith('"') or string.endswith("'"):
        string = string[:-1]
    string = "\\".join(string.split("/"))
    return string

def send_requests(url, headers, payload, mode: bool = True):
    if (mode):
        res = requests.post(url, headers=headers, json=payload)
    else:
        res = requests.post(url, headers=headers, data=payload)

    return res

def time_stamp_log(string):
    return "["+ time.strftime("%H:%M:%S", time.localtime()) +"] " + string

class SendPost(App):
    """最简单的 Textual 应用"""

    CSS_PATH = ["style/overview.tcss"]
    
    def compose(self) -> ComposeResult:
        # Inputer
        yield Vertical(
                Horizontal(
                    Label("URL: "),
                    Input(placeholder="URL", id="url"),
                    id="url-container",
                ),
                Horizontal(
                    Label("Headers File(json): "),
                    Input(placeholder="Headers File", id="headers"),
                    id="headers-container",
                ),
                Horizontal(
                    Label("Payload File(json): "),
                    Input(placeholder="Payload File", id="payload"),
                    id="payload-container",
                ),
                id="inputer",
            )

        # Tools
        yield Horizontal(
            Button("Send",id="send"),
            Checkbox("Send JSON",id="payload-mode",value=True),
            id="tools",
        )

        yield Vertical(
            Static("Log"),
            Log(id="log"),
            id="logs"
        )

        # Request Viewer
        yield Vertical(
            Static(" Response Viewer (Payload Mode: JSON)",id="tip-response"),
            TextArea(
                id="ret",
                language="json",
                read_only=True,
            ),
            id="requests",
        )
        
        yield Footer()

    def on_mount(self):
        self.headers_file = None
        self.payload_file = None

    BINDINGS = [
        ("ctrl+g","send","(GO)Send"),
        ("ctrl+s","save","Save as Preset"),
        ("ctrl+o","open","Open Preset"),
    ]

    @on(Checkbox.Changed, "#payload-mode")
    def payload_mode_changed(self):
        mode = self.query_one("#payload-mode").value
        self.query_one("#tip-response").update(" Response Viewer (Payload Mode: "+("JSON" if mode else "String")+")")
        
    @on(Button.Pressed,"#send")
    def send(self):
        try:
            # load url
            url = self.query_one("#url").value.strip()
            if (not url):
                self.notify("Please Type URL",severity="error")
                return

            # load headers
            headers_file = self.query_one("#headers").value
            headers_file = process_str(headers_file)
            headers = None
            if (not headers_file):
                headers = {}
            else:
                try:
                    f = open(headers_file, "r")
                    headers = json.load(f)
                    f.close()
                except FileNotFoundError as e:
                    self.notify(f"Headers File is not Exist", title="Headers File Analysis Error", severity="error", timeout=2)
                    return
                except json.JSONDecodeError as e:
                    self.notify(f"Error: {e}", title="Headers File Analysis Error", severity="error", timeout=10)
                    return

            # load payload
            payload_file = self.query_one("#payload").value
            payload_file = process_str(payload_file)
            mode = self.query_one("#payload-mode").value
            payload = None
            if (not payload_file):
                payload = None
            else:
                if (mode):
                    try:
                        f = open(payload_file, "r")
                        payload = json.load(f)
                        f.close()
                    except FileNotFoundError as e:
                        self.notify(f"Payload File is not Exist", title="Payload File Analysis Error", severity="error", timeout=2)
                        return
                    except json.JSONDecodeError as e:
                        self.notify(f"Error: {e}", title="Payload File Analysis Error", severity="error", timeout=10)
                        return
                else:
                    try:
                        f = open(payload_file, "r")
                        payload = f.read()
                        f.close()
                    except FileNotFoundError as e:
                        self.notify(f"Payload File is not Exist", title="Payload File Analysis Error", severity="error", timeout=2)
                        return

            self.notify("load file successfully & sending",severity="information",timeout=3)
            log = self.query_one("#log")
            log.write_line("---")
            # log.write_line("["+time.strftime("%H:%M:%S", time.localtime())+"] Making Response...")
            log.write_line(time_stamp_log("Making Response..."))
            log.write_line(f"URL: {url}, Payload_Mode: {'JSON' if mode else 'String'}")
            log.write_line(f"Headers: {self.headers_file}, Payload: {self.payload_file}")
            log.refresh()

            def send_core(self,url,headers,payload,mode):
                if (not url.startswith("http")):
                    url = "https://" + url

                if (url.startswith("http://")):
                    log.write_line(f"Protocols: http")
                else:
                    log.write_line(f"Protocols: httpS")

                res = None
                try:
                    # 第一次尝试
                    res = send_requests(url, headers, payload, mode)
                    log.write_line(f"Status: {res.status_code}")
                    log.write_line(time_stamp_log("Task Successfully"))
                except requests.exceptions.SSLError as e:
                    # 证书错误（切换协议）
                    log.write_line("SSL Error, Switching Protocols...")
                    if (url.startswith("http://")):
                        url = url.replace("http://", "https://")
                        log.write_line(f"Protocols: httpS")
                    else:
                        url = url.replace("https://", "http://")
                        log.write_line(f"Protocols: http")
                    log.write_line(f"URL: {url}")
                    log.refresh()
                    # 第二次尝试
                    try:
                        res = send_requests(url, headers, payload, mode)
                        log.write_line(f"Status: {res.status_code}")
                        log.write_line(time_stamp_log("Task Successfully"))
                    except Exception as e:
                        log.write_line(f"Error: {e}")
                        log.write_line(time_stamp_log("Task Failed"))
                        self.notify(str(e),title="Connect Error",severity="error",timeout=5)
                        res = False
                except Exception as e:
                    log.write_line(f"Error: {e}")
                    log.write_line(time_stamp_log("Task Failed"))
                    self.notify(str(e),title="Connect Error",severity="error",timeout=5)
                    res = False
                log.refresh()

                if (res == False):
                    self.query_one("#tip-response").styles.background = "#FF0000"
                    self.query_one("#tip-response").styles.color = "#FFFFFF"
                    self.query_one("#ret").text = ""
                elif (res.status_code//100) != 2:
                    self.query_one("#tip-response").styles.background = "#FF0000"
                    self.query_one("#tip-response").styles.color = "#FFFFFF"
                    self.query_one("#tip-response").update(f" Response (Payload: {'JSON' if mode else 'String'}, Status: {res.status_code}, Res: {res.headers['Content-Type']})")
                    if ("charset=" in res.headers['Content-Type']):
                        res.encoding = res.headers['Content-Type'].split("charset=")[-1]
                    else:
                        res.encoding = "utf-8"
                    self.query_one("#ret").text = res.text
                else:
                    self.query_one("#tip-response").styles.background = "#00FF00"
                    self.query_one("#tip-response").styles.color = "#000000"
                    self.query_one("#tip-response").update(f" Response (Payload: {'JSON' if mode else 'String'}, Status: {res.status_code}, Res: {res.headers['Content-Type']})")
                    if ("charset=" in res.headers['Content-Type']):
                        res.encoding = res.headers['Content-Type'].split("charset=")[-1]
                    else:
                        res.encoding = "utf-8"
                    self.query_one("#ret").text = res.text

            t = threading.Thread(target=send_core,args=(self,url,headers,payload,mode))
            t.start()

        except Exception as e:
            self.notify(e,title="Error&Stop Task",severity="error",timeout=5)

    def action_send(self):
        self.send()

    def action_save(self):
        root = Tk()
        root.withdraw()
        pth = filedialog.asksaveasfilename(
            title="Save as Preset",
            initialfile="post_preset.json",
            defaultextension=".json",
            filetypes=[("JSON files","*.json"),("All files","*.*")]
        )
        root.destroy()
        if (not pth):
            return
        
        try:
            with open(pth,"w",encoding="utf-8") as f:
                preset = {
                    "url":self.query_one("#url").value,
                    "headers_f":self.query_one("#headers").value,
                    "payload_f":self.query_one("#payload").value
                }
                json.dump(preset,f)
                self.notify("save preset successfully",severity="information",timeout=3)
        except Exception as e:
            self.notify(e,title="Save Failed",severity="error",timeout=5)

    def action_open(self):
        root = Tk()
        root.withdraw()
        pth = filedialog.askopenfilename(
            title="Open A Preset",
            defaultextension=".json",
            filetypes=[("JSON files","*.json"),("All files","*.*")]
        )
        root.destroy()
        if (not pth):
            return
        
        try:
            preset = None
            with open(pth,"r",encoding="utf-8") as f:
                # try-except -> JSON Decoded Error
                preset = json.load(f)

            if (not "url" in preset):
                raise ValueError("url phase is not exists")
            if (not "headers_f" in preset):
                raise ValueError("headers_f phase is not exists")
            if (not "payload_f" in preset):
                raise ValueError("payload_f phase is not exists")
            
            self.query_one("#url").value = preset["url"]
            self.query_one("#headers").value = preset["headers_f"]
            self.query_one("payload").value = preset["payload_f"]

        except json.JSONDecodeError as e:
            self.notify(f"JSON File is Broken, {e}",title="Load Failed",severity="error",timeout=5)
        except ValueError as e:
            self.notify(f"JSON File is Broken, {e}",title="Load Failed",severity="error",timeout=5)
        except Exception as e:
            self.notify(e,title="Load Failed",severity="error",timeout=5)

if __name__ == "__main__":
    SendPost().run()