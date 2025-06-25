from crewai.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import PrivateAttr
import base64
import time
import os

class CustomImageInterpreter(BaseTool):
    name: str = "custom_image_interpreter"
    description: str = "Extracts layout and structure from UI images using GPT-4o."

    _llm: ChatOpenAI = PrivateAttr()
    _system_prompt: str = PrivateAttr()

    def __init__(
        self,
        model_name: str = "gpt-4o",
        temperature: float = 0.2,
        prompt_path: str = "prompts/image_interpreter_prompt.txt"
    ):
        super().__init__()
        self._llm = ChatOpenAI(model=model_name, temperature=temperature)
        self._system_prompt = self._load_prompt(prompt_path)

    def _load_prompt(self, path: str) -> str:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return "You are a layout interpreter AI."

    def _run(self, image_path: str) -> str:
        try:
            start = time.time()

            # Read and encode image
            with open(image_path, "rb") as img_file:
                img_bytes = img_file.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")
            image_url = f"data:image/png;base64,{img_b64}"

            # Multimodal prompt for GPT-4o
            messages = [
                {"role": "system", "content": self._system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Please analyze this UI image and provide a detailed breakdown of its visual hierarchy, layout zones, components, and relationships."},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ]
                }
            ]

            print("📤 Sending image to GPT-4o...")
            response = self._llm.invoke(messages)
            print(f"✅ Response in {time.time() - start:.2f} seconds")

            return response.content

        except Exception as e:
            return f"❌ Error during interpretation: {e}"
