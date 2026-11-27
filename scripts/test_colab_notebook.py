import ast
import asyncio
import contextlib
import io
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from langchain_core.messages import AIMessage, ToolMessage
from pydantic import SecretStr

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "sample-agent-collab.ipynb"


def notebook_cells():
    return json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))["cells"]


def code_cell(cells, marker):
    return next(
        "".join(cell["source"])
        for cell in cells
        if cell["cell_type"] == "code" and marker in "".join(cell["source"])
    )


def execute_cell(cells, marker, namespace):
    exec(code_cell(cells, marker), namespace)  # noqa: S102 - execute the notebook under test


class FakeModel:
    def __init__(self, **kwargs):
        self.calls = 0
        self.saw_tool_result = False

    def bind_tools(self, tools):
        return self

    async def ainvoke(self, messages):
        self.calls += 1
        if self.calls == 1:
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "list_services",
                        "args": {"zone": "leste"},
                        "id": "test-call",
                    }
                ],
            )
        self.saw_tool_result = isinstance(messages[-1], ToolMessage)
        return AIMessage(content="Resposta simulada")


class ColabNotebookTests(unittest.TestCase):
    def test_snapshots_and_syntax(self):
        cells = notebook_cells()
        for cell in cells:
            if cell["cell_type"] == "code":
                source = "".join(cell["source"])
                if not source.startswith("%pip"):
                    compile(
                        source, "<notebook>", "exec", ast.PyCF_ALLOW_TOP_LEVEL_AWAIT
                    )

        namespace = {}
        execute_cell(cells, "catalog = json.loads", namespace)
        prompt = ROOT / "backend" / "prompts" / "assistant.md"
        catalog = ROOT / "data" / "processed" / "services.sample.json"
        self.assertEqual(
            namespace["prompt"], prompt.read_text(encoding="utf-8").strip()
        )
        self.assertEqual(
            namespace["catalog"], json.loads(catalog.read_text(encoding="utf-8"))
        )

    def test_zone_restriction(self):
        cells = notebook_cells()
        namespace = {}
        execute_cell(cells, "catalog = json.loads", namespace)
        execute_cell(cells, "def list_services", namespace)
        tool = namespace["list_services"]
        for zone in ("centro", "leste", "norte", "sul", "oeste"):
            namespace["ZONE"] = zone
            namespace["selected"] = [
                item
                for item in namespace["catalog"]["services"]
                if item["zone"] == zone
            ]
            result = json.loads(tool.invoke({"zone": zone}))
            self.assertEqual(len(result["services"]), 8)
            self.assertEqual(result["zone"], zone)
            rejected = json.loads(tool.invoke({"zone": "outra"}))
            self.assertEqual(rejected, {"error": "zone_mismatch", "active_zone": zone})

    def test_graph_executes_tool_with_simulated_model(self):
        cells = notebook_cells()
        namespace = {}
        output = io.StringIO()
        with (
            patch(
                "builtins.input",
                side_effect=["https://example.test/openai/v1/", "demo"],
            ),
            patch("getpass.getpass", return_value="fake-key"),
            patch("langchain_openai.ChatOpenAI", FakeModel),
            contextlib.redirect_stdout(output),
        ):
            execute_cell(cells, "from getpass import getpass", namespace)
            execute_cell(cells, "catalog = json.loads", namespace)
            execute_cell(cells, "def list_services", namespace)
            execute_cell(cells, "builder = StateGraph", namespace)
            execution = compile(
                code_cell(cells, "result = await agent.ainvoke"),
                "<notebook>",
                "exec",
                ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )
            asyncio.run(eval(execution, namespace))

        self.assertEqual(namespace["model"].calls, 2)
        self.assertTrue(namespace["model"].saw_tool_result)
        self.assertIn("Tools consultadas: list_services", output.getvalue())
        self.assertIn("Resposta simulada", output.getvalue())
        self.assertNotIn("fake-key", output.getvalue())

    def test_local_notebook_uses_same_execution_and_configured_limits(self):
        colab_cells = notebook_cells()
        local_path = ROOT / "notebooks" / "sample-agent.ipynb"
        local_cells = json.loads(local_path.read_text(encoding="utf-8"))["cells"]
        marker = "result = await agent.ainvoke"
        self.assertEqual(code_cell(local_cells, marker), code_cell(colab_cells, marker))

        namespace = {
            "base_url": "https://example.test/openai/v1/",
            "config": {
                "CARECOMPASS_FOUNDRY_DEPLOYMENT": "demo",
                "CARECOMPASS_FOUNDRY_API_KEY": "fake-key",
                "CARECOMPASS_AGENT_TIMEOUT_SECONDS": "23",
                "CARECOMPASS_AGENT_MAX_STEPS": "9",
            },
            "SecretStr": SecretStr,
        }
        output = io.StringIO()
        with (
            patch("langchain_openai.ChatOpenAI", FakeModel),
            contextlib.redirect_stdout(output),
        ):
            execute_cell(colab_cells, "catalog = json.loads", namespace)
            execute_cell(colab_cells, "def list_services", namespace)
            execute_cell(local_cells, "builder = StateGraph", namespace)
            execution = compile(
                code_cell(local_cells, marker),
                "<notebook>",
                "exec",
                ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )
            asyncio.run(eval(execution, namespace))

        self.assertEqual(namespace["timeout_seconds"], 23)
        self.assertEqual(namespace["max_steps"], 9)
        self.assertTrue(namespace["model"].saw_tool_result)
        self.assertIn("Tools consultadas: list_services", output.getvalue())
        self.assertNotIn("fake-key", output.getvalue())

    def test_invalid_endpoint_is_rejected(self):
        cells = notebook_cells()
        with (
            patch(
                "builtins.input", side_effect=["http://example.test/openai/v1/", "demo"]
            ),
            patch("getpass.getpass", return_value="fake-key"),
            self.assertRaisesRegex(ValueError, "endpoint HTTPS"),
        ):
            execute_cell(cells, "from getpass import getpass", {})


if __name__ == "__main__":
    unittest.main()
