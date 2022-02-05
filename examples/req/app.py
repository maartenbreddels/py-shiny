from shiny import *

app_ui = ui.page_fluid(
    ui.input_action_button("safe", "Throw a safe error"),
    ui.output_ui("safe"),
    ui.input_action_button("unsafe", "Throw an unsafe error"),
    ui.output_ui("unsafe"),
    ui.input_text(
        "txt",
        "Enter some text below, then remove it. Notice how the text is never fully removed.",
    ),
    ui.output_ui("txt_out"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc()
    def safe_click():
        req(input.safe())
        return input.safe()

    @output()
    @render_ui()
    def safe():
        raise SafeException(f"You've clicked {str(safe_click())} times")

    @output()
    @render_ui()
    def unsafe():
        req(input.unsafe())
        raise Exception(f"Super secret number of clicks: {str(input.unsafe())}")

    @reactive.effect()
    def _():
        req(input.unsafe())
        print("unsafe clicks:", input.unsafe())
        # raise Exception("Observer exception: this should cause a crash")

    @output()
    @render_ui()
    def txt_out():
        req(input.txt(), cancel_output=True)
        return input.txt()


app = App(app_ui, server)
app.SANITIZE_ERRORS = True