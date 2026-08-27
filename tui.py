from textual.app import App, ComposeResult
from textual.containers import *
from textual.widgets import *
from textual import on
from os.path import exists
import time
import requests
import json

def process_str(string: str):
    string = string.strip()
    if string.startswith('"') or string.startswith("'"):
        string = string[1:]
    if string.endswith('"') or string.endswith("'"):
        string = string[:-1]
    string = "\\".join(string.split("/"))
    return string

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
                    Input(placeholder="Headers File", id="headers-file"),
                    id="headers-container",
                ),
                Horizontal(
                    Label("Payload File(json): "),
                    Input(placeholder="Payload File", id="payload-file"),
                    id="payload-container",
                ),
                id="inputer",
            )

        # Tools
        yield Horizontal(
                Button("Update Headers",id="upd-headers"),
                Button("Update Payload",id="upd-payload"),
                Button("Send",id="send"),
                Checkbox("Send JSON",id="payload-mode",value=True),
                id="tools",
            )
        
        # Sending Viewer
        yield Horizontal(
                Vertical(
                    Static(" Headers Viewer",id="tip-headers"),
                    TextArea(
                        id="headers",
                        language="json",
                        read_only=True,
                    ),
                ),
                Vertical(
                    Static(" Payload Viewer",id="tip-payload"),
                    TextArea(
                        id="payload",
                        language="json",
                        read_only=True,
                    ),
                ),
                id="response"
            )

        # Request Viewer
        yield Horizontal(
            Vertical(
                Static(" Response Viewer (Payload Mode: JSON)",id="tip-response"),
                TextArea(
                    id="ret",
                    language="json",
                    read_only=True,
                ),
                id="requests",
            ),
            Vertical(
                Static("Log"),
                Log(id="log"),
                id="logs"
            ),
            id="req_viewer"
        )
        yield Footer()

    def on_mount(self):
        self.headers_file = None
        self.payload_file = None

    # @on(Button.Pressed, "#send")
    # def on_send_pressed(self):
    #     self.query_one("#response").text = "Sending...\nabc"

    @on(Checkbox.Changed, "#payload-mode")
    def payload_mode_changed(self):
        mode = self.query_one("#payload-mode").value
        self.query_one("#tip-response").update(" Response Viewer (Payload Mode: "+("JSON" if mode else "String")+")")
        
    @on(Button.Pressed, "#upd-headers")
    def upd_headers(self):
        self.headers_file = self.query_one("#headers-file").value
        self.headers_file = process_str(self.headers_file)

        if not self.headers_file:
            self.headers_file = None
            self.notify("Please Input Headers File Path First",
                severity="warning",
                timeout=3
            )
            return

        if not exists(self.headers_file):
            self.headers_file = None
            self.notify("Headers File Is Not Exist",
                severity="error",
                timeout=5
            )
            return

        tip = self.query_one("#tip-headers")
        show_pth = "\\".join(self.headers_file.split('\\')[-2:])
        tip.update(f" Headers: ...\\{show_pth}")
        tip.styles.background = "#00FF00"
        tip.styles.color = "#000000"

        with open(self.headers_file, "r", encoding="utf-8") as f:
            self.query_one("#headers").text = f.read()

    
    @on(Button.Pressed, "#upd-payload")
    def upd_payload(self):
        self.payload_file = self.query_one("#payload-file").value
        self.payload_file = process_str(self.payload_file)

        if not self.payload_file:
            self.payload_file = None
            self.notify("Please Input Payload File Path First",
                severity="warning",
                timeout=3
            )
            return

        if not exists(self.payload_file):
            self.payload_file = None
            self.notify("Payload File Is Not Exist",
                severity="error",
                timeout=5
            )
            return

        tip = self.query_one("#tip-payload")
        show_pth = "\\".join(self.payload_file.split('\\')[-2:])
        tip.update(f" Payload: ...\\{show_pth}")
        tip.styles.background = "#00FF00"
        tip.styles.color = "#000000"

        with open(self.payload_file, "r", encoding="utf-8") as f:
            self.query_one("#payload").text = f.read()

    @on(Button.Pressed,"#send")
    def send(self):
        url = self.query_one("#url").value.strip()
        if (not url):
            self.notify("Please Type URL",severity="error")
            return

        headers = self.query_one("#headers").text
        if (not headers):
            headers = "{}"
        headers = json.loads(headers)

        payload = self.query_one("#payload").text
        if (not payload):
            self.notify("Please Upload Payload File",severity="error")
            return
        mode = self.query_one("#payload-mode").value
        if (mode):
            payload = json.loads(payload)

        log = self.query_one("#log")
        log.write_line("["+time.strftime("%H:%M:%S", time.localtime())+"] Making Response...")
        log.write_line(f"URL: {url}, Payload_Mode: {'JSON' if mode else 'String'}")
        log.write_line(f"Headers: {self.headers_file}, Payload: {self.payload_file}")

        res = None
        if (not url.startswith("http")):
            log.write_line("Try httpS")
            send_url = "https://" + url
            try:
                res = requests.post(send_url, headers=headers, json=payload)
                log.write_line(f"Status: {res.status_code}")
            except Exception as e:
                log.write_line(f"Error: {e}, Status: {res.status_code}")
                log.write_line(f"Try http")
                try:
                    res = requests.post(send_url, headers=headers, json=payload)
                    log.write_line(f"Status: {res.status_code}")
                except Exception as e:
                    log.write_line(f"Error: {e}, Status: {res.status_code}")
                    log.write_line(f"Task failed")
                    res = False
        else:
            try:
                res = requests.post(url, headers=headers, json=payload)
                log.write_line(f"Status: {res.status_code}")
            except Exception as e:
                log.write_line(f"Error: {e}, Status: {res.status_code}")
                log.write_line(f"Task failed")
                res = False

        if (not res or (res.status_code//100) != 2):
            self.query_one("#tip-response").styles.background = "#FF0000"
            self.query_one("#tip-response").styles.color = "#FFFFFF"
        else:
            self.query_one("#tip-response").update(f" Response (Payload: {'JSON' if mode else 'String'}, Res: {res.headers['Content-Type']})")
            self.query_one("#tip-response").styles.background = "#00FF00"
            self.query_one("#tip-response").styles.color = "#000000"
            res.encoding = "utf-8"
            self.query_one("#ret").text = res.text


if __name__ == "__main__":
    SendPost().run()