import re
from typing import Callable


class ReActAgent:
    def __init__(
            self,
            llm: Callable[[list[dict]], str],
            tools: list[str],
            max_steps: int = 5,
    ):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps

    def build_system_prompt(self) -> str:
        return f"""
你是一个ReaAct Agent,

当前可用工具及工具描述:
{AVAILABLE_TOOLS}

回答时，必须严格遵循下面格式中的一种进行回答:

格式1(需要执行工具时):
Thought: 思考过程
Action: 需要的工具名称
Action Input: 工具的输入参数

格式2(已经得到最终答案时):
Action: Finish
Action Input: 最终结果
"""

    def parse_response(self, response: str) -> dict:
        result = {
            "thought": "",
            "action": "",
            "action_input": "",
        }

        thought = re.search(r"Thought:\s*(.*?)(?=\nAction:)", response, re.DOTALL)
        action = re.search(r"Action:\s*(.*?)(?=\nAction Input:)", response, re.DOTALL)
        action_input = re.search(r"Action Input:\s*(.*)", response, re.DOTALL)

        if thought:
            result["thought"] = thought.group(1).strip()
        if action:
            result["action"] = action.group(1).strip()
        if action_input:
            result["action_input"] = action_input.group(1).strip()

        return result

    def run(self, question: str) -> str:
        messages: list[dict] = [
            {"role": "system", "content": self.build_system_prompt()},
            {"role": "user", "content": question},
        ]
        for step in range(self.max_steps):
            response = self.llm(messages)

            print(f"Step {step + 1}:\n", response)
            out = self.parse_response(response)

            action = out["action"]
            action_input = out["action_input"]

            if action == "Finish":
                return action_input

            if action not in self.tools:
                observation = f"Tool {action} is not available."
            else:
                try:
                    observation = action(action_input)
                except Exception as e:
                    observation = f"Exception: {e}"
            messages.extend([
                {"role": "assistant", "content": response},
                {"role": "tool", "content": f"Observation:{observation}"},
            ])
        return "Reach Max Steps."


def calculator(expression: str) -> str:
    return str(eval(expression))


def mock_llm(messages: list[dict]) -> str:
    if "Observation" in messages[-1]["content"]:
        return f"""
Thought:已经获取到最终答案
Action: Finish
Action Input: 20 * 3 + 5 = 65
"""
    else:
        return f"""
Thought: 计算20 * 3 + 5，需要调用工具 [calculator]
Action: calculator
Action Input: 20 * 3 + 5
"""


if __name__ == "__main__":
    AVAILABLE_TOOLS: dict[str, str] = {
        "calculator": "用于进行计算操作的工具"
    }
    agent = ReActAgent(llm=mock_llm, tools=list(AVAILABLE_TOOLS.keys()))
    res = agent.run(question="20 * 3 + 5 的结果是多少?")
    print(res)
