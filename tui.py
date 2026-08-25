from textual.app import App, ComposeResult
from textual.containers import *
from textual.widgets import *
from textual import on

class SendPost(App):
    """最简单的 Textual 应用"""

    CSS_PATH = ["style/overview.tcss"]
    
    def compose(self) -> ComposeResult:
        # Inputer
        yield Vertical(
                Horizontal(
                    Label("Input URL: "),
                    Input(placeholder="URL", id="url"),
                    id="url-container",
                ),
                Horizontal(
                    Label("Headers File: "),
                    Input(placeholder="Headers File", id="headers-file"),
                    id="headers-container",
                ),
                Horizontal(
                    Label("Payload File: "),
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
                id="tools",
            )
        
        # Sending Viewer
        yield Horizontal(
                Vertical(
                    Static("Headers Viewer"),
                    TextArea(
                        id="headers",
                        read_only=True,
                    ),
                ),
                Vertical(
                    Static("Payload Viewer"),
                    TextArea(
                        id="payload",
                        read_only=True,
                    ),
                ),
                id="response"
            )

        # Request Viewer
        yield Vertical(
                Static("Response Viewer"),
                TextArea(
                    id="ret",
                    read_only=True,
                ),
                id="request",
            )
        yield Footer()

    # @on(Button.Pressed, "#send")
    # def on_send_pressed(self):
    #     self.query_one("#response").text = "Sending...\nabc"

if __name__ == "__main__":
    SendPost().run()