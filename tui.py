from textual.app import App, ComposeResult
from textual.containers import *
from textual.widgets import *
from textual import on
from os.path import exists

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
                        read_only=True,
                    ),
                ),
                Vertical(
                    Static(" Payload Viewer",id="tip-payload"),
                    TextArea(
                        id="payload",
                        read_only=True,
                    ),
                ),
                id="response"
            )

        # Request Viewer
        yield Vertical(
                Static(" Response Viewer (Payload Mode: JSON)",id="tip-response"),
                TextArea(
                    id="ret",
                    read_only=True,
                ),
                id="request",
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

if __name__ == "__main__":
    SendPost().run()