from local_inference import MODEL_CONFIGS
from main import model_names, run_pipeline
import gradio as gr

def generate(pdf_file, api_key, model_name, local_model, chunk_sens, deck_name, mode):
    if mode == "Local":
        return run_pipeline(pdf_file.name, chunk_sens, "data", "output", "", "", "", local_model, True, deck_name)
    else:
        return run_pipeline(pdf_file.name, chunk_sens, "data", "output", api_key, model_name, "groq", "", False, deck_name)

def toggle_mode(mode):
    return gr.update(visible=mode=="API"), gr.update(visible=mode=="Local")

with gr.Blocks(css="footer {display: none !important}") as demo:
    gr.Markdown("## PDF to Anki Flashcard Generator")

    with gr.Row():

        with gr.Column():

            pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])

            mode = gr.Radio(["API", "Local"], value="API", label="Inference Mode")
            with gr.Group(visible=True) as api_group:

                model_input = gr.Dropdown(choices=model_names, label="Model")
                api_key_input = gr.Textbox(label="API Key", type="password")

            with gr.Group(visible=False) as local_group:

                local_model_input = gr.Dropdown(choices=list(MODEL_CONFIGS.keys()), label="Local Model")

            chunk_sens_input = gr.Slider(5, 50, value=15, step=1, label="Chunk Sensitivity")
            deck_name_input = gr.Textbox(value="My Deck", label="Deck Name")
            run_btn = gr.Button("Generate Flashcards", variant="primary")

        with gr.Column():
            
            output_file = gr.File(label="Download Anki Deck")

    mode.change(fn=toggle_mode, inputs=mode, outputs=[api_group, local_group])

    run_btn.click(fn=generate, inputs=[pdf_input, api_key_input, model_input, local_model_input, chunk_sens_input, deck_name_input, mode], outputs=output_file)

demo.launch()